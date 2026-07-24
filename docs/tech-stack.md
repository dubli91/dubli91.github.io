# 기술 스택

> 숙련도 순으로 나열합니다.

---


## 주요 언어 및 프레임워크

| 기술 | 한 줄 코멘트 |
| --- | --- |
| Python | Python 3.11~14 및 FastAPI + UV 조합의 백엔드 서버 개발  |
| Java | Java 8-11 수준의 레거시 백엔드 서버 개발 및 유지보수 |
| C / C++ | 자료구조 / 알고리즘 문제 풀이 수준 |


## 프레임워크 및 백엔드 기술

| 기술 | 한 줄 코멘트 |
| --- | --- |
| FastAPI | 부서 내 FastAPI + UV 최초 도입 및 베스트 프렉티스 소개, REST API 개발, AWS Lambda 및 k8s를 통한 서비스 배포 |
| Spring Boot | TDD를 통한 REST API 개발, Spring REST Docs 도입, jib 플러그인을 통한 이미지 빌드 |


## 인프라 / DevOps

### IaaS
AWS 에서 주로 작업하였으며, 최근 GCP도 도입하여 GCP 운영 경험도 쌓고 있습니다.

| 기술 | 한 줄 코멘트 |
| --- | --- |
| AWS Lambda | [aws-lambda-adapter](https://github.com/aws/aws-lambda-web-adapter)를 통한 FastAPI 서비스 운영 |
| AWS EKS | 가전기기 트래픽 수집 및 처리 서비스(Smarthome) 클러스터의 가용성 및 버전관리 / Karpenter 활용 |
| GCP GKE | 가전용 AI 서버의 인프라 운영 / Keda 활용 |
| AWS EC2 | Springboot 기반의 레거시 백엔드 서버 코드 운영 |

### 모니터링 / CICD
| 기술 | 한 줄 코멘트 |
| --- | --- |
| Github Action | EC2 기반 및 K8S 기반 서비스의 검증 및 배포 파이프라인 구축|
| LGT 스택 | GCP 상에서 Grafana + Prometheus + Loki + Open Telemetry + Tempo + FluentBit |
| Argo CD / Rollout | GCP 상에서 Argo CD 배포 구축 / Argo rollout을 통한 Canary 배포 구축 |


## 데이터베이스

| 기술 | 한 줄 코멘트 |
| --- | --- |
| Redis / Valkey | 인증정보 저장 및 데이터 캐싱을 위해 AWS Elasticache 활용 |
| NoSQL | AWS DynamoDB 및 MongoDB Atlas 사용, PynamoDB를 통한 접근 |
| Mysql | AuroraDB 활용, jdbc 사용 |