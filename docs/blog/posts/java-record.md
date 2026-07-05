---
date: 2023-08-25
categories:
  - Java
tags:
  - Java
  - Record
slug: java-record
---

# Record 정리

토비님의 유튜브에서 스프링 강의를 듣고 있는데 Record에 관련된 이야기가 나왔다. Java 스프링으로 밥 벌어먹고 살고 있는 사람으로서 처음 들어보는 키워드였기 때문에 적잖이 당황했다. 구글링을 해보니 class, interface 등과 동급인, 꽤 중요한 키워드인 것 같아서 여기에 정리해본다.

## Java Record의 정의
찾아보니 Record는 Java 14에서 처음 나왔고, 16에서부터 정식 포함되었다. JEP 359에서 정의를 가져왔다. 번역은 구글번역을 이용했다.

> *Records* are a new kind of type declaration in the Java language. Like an `enum`, a `record` is a restricted form of class. It declares its representation, and commits to an API that matches that representation. Records give up a freedom that classes usually enjoy: the ability to decouple API from representation. In return, records gain a significant degree of concision.
> 
> 레코드는 Java 언어의 새로운 유형 선언입니다. 열거형과 마찬가지로 레코드는 제한된 형태의 클래스입니다. 표현을 선언하고 해당 표현과 일치하는 API에 커밋합니다. 레코드는 클래스가 일반적으로 누리는 자유, 즉 표현에서 API를 분리하는 기능을 포기합니다. 그 대가로 기록은 상당한 수준의 간결성을 얻습니다.

## 왜 만들었는가
단순히 Data만 표현하는 클래스들을 만들기 위해서도 기존 자바에서는 수 많은 코드를 (이른바 boilerplate들. equals() 라던제 getter(), setter() 등…) 작성해야한다. 그러면 다음과 같은 문제점이 있다.

1. boilerplate 코드 작성 도중에 에러가 발생할 여지가 있다.
2. 요즘은 Intellij 같은 IDE에서 금방 코드들을 생성할 수 있지만, 여전히 장황하기 때문에 다른 프로그래머 입장에서는 이 클래스가 그냥 Data만 표현하는 클래스인지, 아니면 또 무슨 함수나 로직같은게 들어가있는지 한 눈에 알기 힘들다.

## 어떻게 쓰는가

코드는 다음과 같이 작성된다. type 선언인데 함수와 비슷한 형태로 선언되는 것이 특징이다. 괄호 안에 Record에 포함하고 싶은 필드들을 선언하면 된다. 그러면 다음과 같은 일이 일어난다.

- 괄호 안 필드들이 final로 선언된다.
- public 접근자가 자동 선언된다. 그런데 일반적인 getterField()와 같은 식으로 쓰지 않고 그냥 필드 이름 그대로 field() 와 같이 접근한다.
- canonical 생성자가 자동으로 선언된다. Record에 선언된 필드들을 순서대로 인자로 받는 생성자이다.
- toString(), hashCode(), equals()도 자동 생성된다. equals의 경우 같은 record이고 field들의 값이 모두 같은 경우 true를 반환한다.

추가적으로 static 변수나 함수정도는 class와 동일하게 선언 가능한 것으로 보인다. abstract는 될 수 없는데, 인터페이스를 구현하는건 가능한 것 같고... 구현이 필요할 때 마다 명세를 찾아보거나 IDE로 확인해봐야겠다.

생성자를 추가로 생성할 수도 있다. 인자를 직접 선언할 수도 있고, 인자를 선언하지 않으면 기본 canonical 생성자를 대체한다.

인자를 직접 선언한 생성자는 this()를 통해서 결국 canonical 생성자를 호출해야하는데, 이 때 this()는 생성자의 첫 줄에만 선언이 가능해다. 따라서 this() 호출 전 별도 로직을 추가하는 것이 불가능해 보인다. 인자가 있는 생성자는 결국 단순히 canonical 생성자에 변수만 단순히 넘겨주고, Data 체크 로직은 결국 canonical 생성자에서 진행해야 하는 것으로 보인다

```java
// Java Record 선언 및 Constructor 선언
public record Point(
        int x,
        int y,
        int radius) {

    public static String gender = "Male";

    //public Point(int x, int y){
	//	  if (x > y) throw new IllegalArgumentException(); 
    //    this(x, y, x+y); // Error : Call to 'this()' must be first statement in constructor body
    //}
    public Point(int x, int y){
        this(x, y, x+y);
    }
    public Point {
        if (x > y) throw new IllegalArgumentException();
    }
}
```


간단히 알아보았는데, 개인적으로는 사용할 것 같지 않다. 이유는 다음과 같다.

- JPA를 위한 Entity 로 사용할 수 없음 → getter / setter함수가 없는데다가 final 필드만 가져서 그런 것 같다.
- Lombok으로도 충분히 boilerplate 함수들을 많이 줄일 수 있다.
- 아직 회사에서 Java 8을 쓰고있다(앗!). 

우리 회사뿐만 아니라 대부분의 코드들이 아직도 Java 8로 동작한다고 들었다. Java 16 이상이 주류가 되면 쓰일까? 솔직히 잘 모르겠다. 그럼에도 immutable 한 자료구조로써 직접 Java에서 지원을 한다는 것 자체에 의의를 두어야 할 것 같다.
