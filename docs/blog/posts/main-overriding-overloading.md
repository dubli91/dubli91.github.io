---
date: 2020-12-07
categories:
  - java
tags:
  - Java
slug: main-overriding-overloading
---

# Main함수의 Overriding / Overloading

main함수는 main함수는 java 프로그램의 시작이자 끝의 역할을 하고 있어 다른 함수들과는 다른 취급을 받을거라는 인상을 준다. 

```java
public class Main {
    public static void main(String[] args){
        System.out.println("Hello World");
    }
}
```
<br>
그렇다면 이 함수는 Overriding / Overloading이 될까?
<br>

# 1) Overriding

당연히 안된다. 이유는 main 메소드는 static이고 static 메소드는  overriding이 안되기 때문이다. 

```java
//실패
public class ChildMain extends Main{
    //Method does not override method from its superclass
    @Override
    public static void main(String[] args) {
        System.out.println("hello world2");
    }
}
```
<br>
static 메소드가 overriding이 안되는 이유는 다음과 같다
- static 메소드는 클래스가 어떤 메소드를 호출할 지 runtime이 아닌 compile 타임에 결정하기 때문에 overriding할 수 없음.
- static 메소드는 애초에 자식 클래스에 상속하는 메소드가 아님(!)

[//]: # (Hello)
<br>

그래서 아래같이 @Override를 빼면 컴파일 에러는 나지 않는다. 다만 Main의 main 메소드와 ChildMain의 main 메소드는 관련이 전혀 없는 아예 별개의 메소드이다. super(); 로 부모 클래스의 메소드를 호출하는 것도 물론 불가능하다.

<br>

```java
public class ChildMain extends Main{

    //실패 
    /*        
    public static void main(String[] args) {
        super();
    }
    */

    //성공
    public static void main(String[] args) {
        System.out.println("hello world2");
    }
}
```
<br>

# 2) Overloading

overloading은 의외로 가능하다. 하지만 프로그램 실행 시에는 String[] args 를 매개변수로 가지는 main 메소드가 동작하게 된다.
<br>

```java
public class Main {
    public static void main(String[] args) {
        System.out.println("hello world");
    }

    public static void main(int[] args) {
        System.out.println("hello world");
    }

    public static void main(double[] args) {
        System.out.println("hello world");
    }
}
```
<br>
굳이 다른 main 메소드를 쓰고 싶다면 다음과 같이 main(String[] args) 안에서 호출하는 수밖에 없다.
<br>

```java
public class Main {
    public static void main(String[] args) {
        int[] integersArray = new int[args.length];
        for (int i = 0 ; i < args.length ; ++i){
            integersArray[i] = Integer.parseInt(args[i]);
        }
        main(integersArray);
    }

    public static void main(int[] args) {
        for (int arg : args)
            System.out.println(arg);
    }
}
```
<br>

# 결론
- main 메소드는 사실상 다른 메소드와 동일한 규칙을 따른다.
- main 메소드는 static이기 때문에 @Override가 먹히지 않는다.
- main 메소드는 Overloading이 되지만 굳이 그럴 이유는 없어보인다
<br>
<br>

지식이 늘었다.
