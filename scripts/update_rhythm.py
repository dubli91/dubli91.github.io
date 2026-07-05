#!/usr/bin/env python3
"""CPI(https://cpi.makecir.com) 프로필을 긁어와 docs/rhythm.md 를 갱신하는 스크립트.

- 표준 라이브러리만 사용 (GitHub Actions 에서 별도 설치 없이 실행)
- rhythm.md 안의 <!-- cpi:NAME:start --> ... <!-- cpi:NAME:end --> 블록만 교체
- 파싱 실패 시 즉시 종료(비정상 데이터로 페이지를 덮어쓰지 않음)
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

BASE_URL = "https://cpi.makecir.com"
TABLE_URL = f"{BASE_URL}/users/tables/13196"

REPO_ROOT = Path(__file__).resolve().parent.parent
RHYTHM_MD = REPO_ROOT / "docs" / "rhythm.md"

# 곡 셀 배경색 → 클리어 램프
COLOR_LAMP = {
    "#FF9966": "FC",
    "#FFFF99": "EX",
    "#FF6666": "HC",
    "#99CCFF": "CL",
    "#99FF99": "EC",
    "#FF66CC": "AC",
    "#CCCCCC": "FA",
    "#FFFFFF": "NP",
}

LAMP_ORDER = ["FC", "EX", "HC", "CL", "EC", "AC", "FA", "NP"]
LAMP_MEANING = {
    "FC": "Full Combo",
    "EX": "EX-HARD Clear",
    "HC": "Hard Clear",
    "CL": "Clear",
    "EC": "Easy Clear",
    "AC": "Assist Clear",
    "FA": "Failed",
    "NP": "Not Played",
}

DAN_NOTE = {
    "中伝": "중급자 티어",
    "皆伝": "최고 단위",
    "十段": "상급자 관문",
}


def die(msg: str) -> None:
    sys.exit(f"update_rhythm: {msg}")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (rhythm-page-updater)"})
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001 - 재시도 후 실패 시 그대로 보고
            last_err = e
            time.sleep(10 * (attempt + 1))
    die(f"페이지 요청 실패: {last_err}")
    raise AssertionError  # unreachable


def md_escape(text: str) -> str:
    """마크다운 표/링크 텍스트용 이스케이프 (HTML 엔티티는 그대로 유지)."""
    text = re.sub(r"\s+", " ", text).strip()
    for ch in "\\|[]*_`":
        text = text.replace(ch, "\\" + ch)
    return text


# ---------------------------------------------------------------- 파싱


def parse_profile(html: str) -> dict:
    m = re.search(r'<h4 class="card-title"[^>]*>([^<]+)</h4>', html)
    if not m:
        die("플레이어 이름을 찾지 못함")
    name = m.group(1).strip()
    window = html[m.start() : m.start() + 8000]

    def grab(pattern: str, label: str, flags: int = 0) -> str:
        g = re.search(pattern, window, flags)
        if not g:
            die(f"{label}을(를) 찾지 못함")
        return g.group(1)

    player_id = grab(r"(\d{4}-\d{4})", "플레이어 ID")
    cpi = grab(r"CPI\s*:\s*([\d.]+)", "CPI 값")

    # (推定 : </h6><h5 ...>8458</h5><h6 ...>位程度) 구조 - 태그 안의 순수 숫자를 찾는다
    rank_seg_start = window.find("推定")
    rank_seg = window[rank_seg_start : rank_seg_start + 400] if rank_seg_start >= 0 else ""
    rank_m = re.search(r">\s*([\d,]+)\s*<", rank_seg)
    if rank_seg_start < 0 or "位程度" not in rank_seg or not rank_m:
        die("추정 순위를 찾지 못함")
    rank = int(rank_m.group(1).replace(",", ""))

    dan_idx = window.find("段位")
    if dan_idx < 0:
        die("段位를 찾지 못함")
    dan_m = re.search(r"SP\s*([^\s<>/]+)", window[dan_idx : dan_idx + 500])
    if not dan_m:
        die("段位 값을 찾지 못함")
    dan = dan_m.group(1)

    created = grab(r"作成日\s*[::]\s*([\d/]+)", "프로필 작성일")

    upd = re.search(r"更新日\s*[::]\s*([\d/]+)", html)
    if not upd:
        die("更新日을 찾지 못함")

    return {
        "name": name,
        "id": player_id,
        "cpi": cpi,
        "rank": rank,
        "dan": dan,
        "created": created.replace("/", "."),
        "updated": upd.group(1).replace("/", "."),
    }


def parse_achievements(html: str) -> dict:
    """easy/clear/hard 섹션의 達成済 X / Y ( Z% )."""
    result = {}
    for key in ("easy", "clear", "hard"):
        i = html.find(f'id="{key}"')
        if i < 0:
            die(f"섹션 앵커 #{key}를 찾지 못함")
        window = html[i : i + 1200]
        m = re.search(r"達成済\s*(\d+)\s*/\s*(\d+).*?\(\s*(\d+)%\s*\)", window, re.S)
        if not m:
            die(f"#{key} 達成済 수치를 찾지 못함")
        result[key] = {"done": int(m.group(1)), "total": int(m.group(2)), "pct": int(m.group(3))}
    totals = {v["total"] for v in result.values()}
    if len(totals) != 1:
        die(f"섹션별 대상 곡 수가 일치하지 않음: {totals}")
    result["total"] = totals.pop()
    return result


def parse_hard_table(html: str) -> list[dict]:
    """HARD 표를 [{label, songs: [(title, url, cpi, kojinsa, lamp)]}] 로 파싱 (문서 순서 유지)."""
    m = re.search(r'<table id="hard_table".*?</table>', html, re.S)
    if not m:
        die("hard_table을 찾지 못함")
    table = m.group(0)

    header_re = re.compile(
        r'<tr class="text-center" bgcolor=#444444 id="hard-[^"]*">.*?HARD 適正CPI ([^<]*)</td>.*?</tr>',
        re.S,
    )
    cell_re = re.compile(
        r'<td align="center" bgcolor=(#[0-9A-Fa-f]{6})[^>]*>\s*'
        r'<a href="([^"]+)">(.*?)</a>\s*'
        r'<div class="small-txt"[^>]*>\s*([^<]*?)\s*</div>',
        re.S,
    )

    total_cells = len(re.findall(r'<td align="center" bgcolor=', table))
    parts = header_re.split(table)
    # parts = [머리말, label1, body1, label2, body2, ...]
    if len(re.findall(r'<td align="center" bgcolor=', parts[0])):
        die("구간 머리글 앞에 곡 셀이 존재함 (표 구조 변경 의심)")

    bands = []
    parsed = 0
    for label, body in zip(parts[1::2], parts[2::2]):
        songs = []
        for color, href, title, values in cell_re.findall(body):
            lamp = COLOR_LAMP.get(color.upper())
            if lamp is None:
                die(f"알 수 없는 램프 색상 {color} (곡: {title.strip()!r})")
            vm = re.match(r"([\d.]+|-)\s*/\s*([\d.]+|-)$", values.strip())
            if not vm:
                die(f"適正CPI/個人差度 형식이 예상과 다름: {values!r}")
            songs.append(
                {
                    "title": title,
                    "url": BASE_URL + href,
                    "cpi": vm.group(1),
                    "kojinsa": vm.group(2),
                    "lamp": lamp,
                }
            )
        parsed += len(songs)
        bands.append({"label": label.strip(), "songs": songs})

    if parsed != total_cells:
        die(f"곡 셀 {total_cells}개 중 {parsed}개만 파싱됨 (표 구조 변경 의심)")
    return bands


# ---------------------------------------------------------------- 생성


def lamp_span(lamp: str) -> str:
    return f'<span class="lamp lamp-{lamp.lower()}">{lamp}</span>'


def build_profile(p: dict) -> str:
    dan_note = DAN_NOTE.get(p["dan"], "beatmania IIDX SP 단위")
    return f"""\
<div class="grid cards" markdown>

-   :material-trophy:{{ .lg .middle }} __CPI__

    ---

    **{p['cpi']}**

    추정 순위 약 {p['rank']:,}위

-   :material-medal:{{ .lg .middle }} __段位 (단위)__

    ---

    **SP {p['dan']}**

    {dan_note}

-   :material-account:{{ .lg .middle }} __플레이어__

    ---

    **{p['name']}**

    ID {p['id']}

-   :material-update:{{ .lg .middle }} __갱신__

    ---

    **{p['updated']}**

    프로필 개설 {p['created']}

</div>"""


def build_clears(ach: dict) -> str:
    rows = []
    for key, label in (("easy", "EASY"), ("clear", "CLEAR"), ("hard", "HARD")):
        a = ach[key]
        bar = f'<span class="cpi-bar"><span style="width:{a["pct"]}%"></span></span>'
        rows.append(f'| **{label}**{" " * (5 - len(label))} | {a["done"]} / {a["total"]} | {a["pct"]}% | {bar} |')
    body = "\n".join(rows)
    return f"""\
대상 곡 **{ach['total']}곡** 기준. (적정 CPI 표 범위 내)

| 난이도 | 클리어 | 비율 | 진행도 |
| --- | ---: | ---: | --- |
{body}"""


def build_lamps(lamp_counts: Counter) -> str:
    rows = [
        f"| {lamp_span(lamp)} | {LAMP_MEANING[lamp]} | {lamp_counts.get(lamp, 0)} |"
        for lamp in LAMP_ORDER
    ]
    body = "\n".join(rows)
    return f"""\
| 램프 | 의미 | 곡 수 |
| :---: | --- | ---: |
{body}"""


def build_bands_summary(bands: list[dict]) -> str:
    """適正CPI 50 단위 구간을 기존 페이지의 굵은 구간으로 재집계."""
    hard_lamps = {"FC", "EX", "HC"}
    buckets: dict[str, list[int]] = {}
    lows = []

    def bucket_key(lo: int) -> str:
        if lo < 1500:
            return "low"
        if lo < 1600:
            return "1500~1600"
        if lo < 1650:
            return "1600~1650"
        if lo < 1700:
            return "1650~1700"
        return "1700+"

    for band in bands:
        lo_m = re.match(r"(\d+)", band["label"])
        key = bucket_key(int(lo_m.group(1))) if lo_m else "미집계"
        if lo_m and int(lo_m.group(1)) < 1500:
            lows.append(int(lo_m.group(1)))
        n = len(band["songs"])
        hc = sum(1 for s in band["songs"] if s["lamp"] in hard_lamps)
        cur = buckets.setdefault(key, [0, 0])
        cur[0] += n
        cur[1] += hc

    low_label = f"{min(lows)}~1500" if lows else "~1500"
    order = [("low", low_label), ("1500~1600", "1500~1600"), ("1600~1650", "1600~1650"),
             ("1650~1700", "1650~1700"), ("1700+", "1700+"), ("미집계", "미집계")]
    rows = []
    for key, label in order:
        if key not in buckets:
            continue
        n, hc = buckets[key]
        pct = f"{round(100 * hc / n)}%" if n else "—"
        rows.append(f"    | {label} | {n} | {hc} | {pct} |")
    body = "\n".join(rows)
    misses = buckets.get("미집계", [0, 0])[0]
    return f"""\
??? note "適正CPI 구간별 집계 보기 (펼치기)"
    클리어 현황을 CPI의 **適正CPI** 구간별로 묶은 결과입니다.
    하드 클리어는 HC 이상(FC·EX 포함) 램프 기준입니다.

    | 適正CPI | 곡 수 | 하드 클리어 | 클리어율 |
    | --- | ---: | ---: | ---: |
{body}

    *適正CPI 미산출(算出対象外) {misses}곡은 '미집계'로 분류.*"""


def build_full_table(bands: list[dict], total: int) -> str:
    lines = [
        f'??? note "HARD 곡별 전체 표 펼치기 ({total}곡)"',
        f"    원본 표의 곡별 **適正CPI / 個人差度**와 현재 램프입니다."
        f" 구간은 원본과 같이 適正CPI 내림차순입니다.",
        "",
    ]
    for band in bands:
        if not band["songs"]:
            continue
        label = band["label"]
        title = f"適正CPI {label}" if label[0].isdigit() else f"{label} (適正CPI 미산출)"
        lines.append(f"    **{title}** · {len(band['songs'])}곡")
        lines.append("")
        lines.append("    | 곡명 | 適正CPI | 個人差度 | 램프 |")
        lines.append("    | --- | ---: | ---: | :---: |")
        for s in band["songs"]:
            cpi = s["cpi"] if s["cpi"] != "-" else "—"
            kojinsa = s["kojinsa"] if s["kojinsa"] != "-" else "—"
            lines.append(
                f"    | [{md_escape(s['title'])}]({s['url']}) | {cpi} | {kojinsa} | {lamp_span(s['lamp'])} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip()


# ---------------------------------------------------------------- 조립


def replace_block(text: str, name: str, content: str) -> str:
    start = f"<!-- cpi:{name}:start -->"
    end = f"<!-- cpi:{name}:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        die(f"rhythm.md에서 {name} 마커를 찾지 못함")
    replacement = f"{start}\n\n{content}\n\n{end}"
    return pattern.sub(lambda _: replacement, text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="테스트용 로컬 HTML 파일 (미지정 시 실서버 요청)")
    args = parser.parse_args()

    html = args.source.read_text(encoding="utf-8") if args.source else fetch(TABLE_URL)

    profile = parse_profile(html)
    ach = parse_achievements(html)
    bands = parse_hard_table(html)

    lamp_counts = Counter(s["lamp"] for band in bands for s in band["songs"])
    if sum(lamp_counts.values()) != ach["total"]:
        die(f"램프 합계 {sum(lamp_counts.values())} ≠ 대상 곡 수 {ach['total']}")
    hard_done = lamp_counts["FC"] + lamp_counts["EX"] + lamp_counts["HC"]
    if hard_done != ach["hard"]["done"]:
        die(f"HARD 램프 합계 {hard_done} ≠ 達成済 {ach['hard']['done']}")

    text = RHYTHM_MD.read_text(encoding="utf-8")
    text = replace_block(text, "profile", build_profile(profile))
    text = replace_block(text, "clears", build_clears(ach))
    text = replace_block(text, "lamps", build_lamps(lamp_counts))
    text = replace_block(text, "bands", build_bands_summary(bands))
    text = replace_block(text, "full", build_full_table(bands, ach["total"]))
    RHYTHM_MD.write_text(text, encoding="utf-8")

    print(f"updated: CPI {profile['cpi']} / {ach['total']}곡 / 갱신일 {profile['updated']}")


if __name__ == "__main__":
    main()
