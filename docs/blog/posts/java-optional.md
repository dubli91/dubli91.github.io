---
date: 2023-09-22
categories:
  - Java
tags:
  - Java
  - Optional
slug: java-optional
---

# Optional 정리

약 6년 된 코드를 리팩토링 하고 있는데, Optional을 씌우고 벗기고 하는 과정이 너무 많았다. 굳이 Optional을 안써도 되는데 쓰는건지, 아니면 제대로 쓰고 있는건데 내가 이해를 못하는건지 궁금해졌다. 그래서 공부하고 정리한다. 

## Java Optional의 정의
자바 8에서 Lambda를 도입하면서 함께 도입된 개념 같다. JEP는 따로 없는 것 같고 대신 API문서의 설명을 가져왔다. 

> A container object which may or may not contain a non-null value. If a value is present, isPresent() will return true and get() will return the value.
> 
> null이 아닌 값을 포함하거나 포함하지 않을 수 있는 컨테이너 개체입니다. 값이 있으면 isPresent()는 true를 반환하고 get()은 값을 반환합니다. 

## 왜 만들었는가
Java 아키텍트인 Brian Goetz는 이렇게 설명한다. [해당 문서 36페이지에 나와있다.](https://stuartmarks.files.wordpress.com/2015/10/con6851-api-design-v2.pdf)

> Optional is intended to provide a limited mechanism for library method return types where there is a clear need to represent "no result," and where using null for that is overwhelmingly likely to cause errors.
>
> Optional은 "결과 없음"을 표시해야 하는 명확한 필요성이 있고 이에 대해 null을 사용하면 오류가 발생할 가능성이 압도적으로 높은 라이브러리 메서드 반환 유형에 대한 제한된 메커니즘을 제공하기 위한 것입니다. 
 
## 기본 개념 / 생성법
Java에서 객체는 크게 값을 가지는 경우와 가지지 않는 경우(null)로 나눈다. 이를 Optional로 객체를 감싸면 값이 있는 경우와 비어있는 경우로 나뉜다.
Optional 을 생성하는 방법은 3가지이다.

- Optional.of(object)를 이용한다. null이 아닌게 확실할 때만 쓸 수 있다. 여기에 null을 넣으면 NullPointerException이 발생한다.
- Optional.ofNullable(object)을 이용한다. null인지 아닌지 잘 모르겠으면 이걸 쓴다. 여기에 null을 넣으면 Optional.empty가 된다.
- Optional.empty()를 이용하여 Optional.empty를 만든다.

Optional이 비어있는지 아닌지는 isPresent() 를 사용하면 된다. Optional에서 값을 다시 가져올 때는 get()을 사용하면 된다.

아래 코드를 참고한다.
```java
package org.example;

import java.util.Optional;

public class Main {

    public static void main(String[] args) {
        Point validPoint = new Point(0, 0);
        Point nullPoint = null;
        Optional<Point> maybeValidPoint = Optional.of(validPoint);
        Optional<Point> maybeEmptyPoint = Optional.ofNullable(nullPoint);
        Optional<Point> maybeEmptyPoint = Optional.of(nullPoint); //NullPointerException
        Optional<Point> emptyPoint = Optional.empty();

        System.out.println(maybeValidPoint); //Optional[org.example.Point@2752f6e2]
        System.out.println(maybeEmptyPoint); //Optional.empty
        System.out.println(emptyPoint); //Optional.empty

        System.out.println(maybeValidPoint.isPresent()); //true
        System.out.println(maybeEmptyPoint.isPresent()); //false
        System.out.println(emptyPoint.isPresent()); //false

        System.out.println(maybeValidPoint.get()); //org.example.Point@2752f6e2
        System.out.println(maybeEmptyPoint.get()); //NoSuchElementException: No value present
        System.out.println(emptyPoint.get()); //NoSuchElementException: No value present
    }
}

```
추가로, 비어있는 Optional에서 get()을 하면 NoSuchElementException이 발생한다. 그러니까 굳이 get()으로 꺼내오고 싶다면 우선 isPresent()로 확인하는 것이 필수이다.


## Optional의 이유

중요하게 봐야할 것은 역시 Optional.ofNullable()일 것이다. 값이 있는지 없는지 확실히 아는 상황이라면 굳이 감쌀 이유가 없기 때문이다. <br>

Optional은 "null인지 아닌지 확실치 않은 객체"를 다루는 API를 제공한다. 기존에는 이런 확실치 않은 상황에 대해서 null 체크를 일일히 하면서 진행했어야 했고, 코드량이 많아질 뿐더러 에러를 유발하기도 쉬웠다. 이를 Optional은 좀 더 우아하게 처리해준다.
아래는 대포적인 함수인 map() 및 orElse()를 활용한 Optional 활용 코드와 기존 if문을 활용한 코드가 동일하게 동작하도록 작성해 본 것이다.


```java
// Java Record 선언 및 Constructor 선언
package org.example;

import java.util.Optional;

public class Main {

    public static void main(String[] args) {

        Employee employee = getEmployeeFromDB("John");

        String userCountry = getUserCountryByIf(employee);
        String userCountry2 = getUserCountryByOptional(employee);

        System.out.println(userCountry);
        System.out.println(userCountry2);
    }


    private static Employee getEmployeeFromDB(String name) {
        Address addressWithNullCountry = new Address(null);
        Employee employee = new Employee(addressWithNullCountry);
        return employee;
    }

    private static String getUserCountryByOptional(Employee employee) {
        if (employee != null ) {
            Address address = employee.getAddress();
            if (address != null){
                String country = address.getCountry();
                if (country != null) {
                    return country;
                }
            }
        }
        return "not specified";
    }

    private static String getUserCountryByIf(Employee employee) {
        return Optional.ofNullable(employee)
                .map(Employee::getAddress)
                .map(Address::getCountry)
                .orElse("not specified");
    }

}
```

먼저, Optional에서 자주 사용하는 함수인 map()은 다음과 같이 동작한다.
- 입력 Optional이 값을 가지고 있으면, 함수를 실행하여 얻은 결과값을 다시 Optional로 감싸준다.
- 입력 Optional이 empty라면, 함수를 실행하지 않고 그대로 빈 Optional을 넘겨준다.

위 예시를 보면 Optional api를 사용하여 중복 if문을 없애고 함수 체이닝으로 가독성 좋게 처리한 것을 알 수 있다.
다른 filter() 같은 함수들도 Optional을 받아서 Optional을 리턴하거나 하므로 함수 체이닝을 활용할 수 있다.

그리고 마지막에 orElse()는 이러한 Optional 연산의 최종 결과물에 따라 다음과 같이 동작한다.
- 입력이 값이 있는 Optional이라면 그대로 리턴한다.
- 입력이 빈 Optional이라면 지정된 값을 리턴한다.

따라서 위의 경우 Address::getCountry 값이 있으면 해당 값을, 아니면 "not specified"를 리턴한다.


## 결론
null을 한 번 감싸서 nullpointer 예외를 방지해주는 점에선 환영할 만한 키워드이지만 그만큼 오용도 많이 되는 키워드이다. 
Optional로 감싸고 벗기는 데에 컴퓨팅 연산이 들어갈 뿐더러 다른 종류의 예외가 여전히 발생할 수 있기 때문이다(NoSuchElementException). <br>

매개변수로 Optional을 받거나, 리턴을 Optional로 하는 경우가 종종 있는데 호출자 입장에서 추가적인 로직을 강요하고 혼동을 야기할 수 있기 때문에
이런 건 지양하고 Optional 연산은 체이닝등을 이용해서 한 문장 내에서 끝내는게 좋을 것 같다.
단순한 null 체크용이라면 기존처럼 == 를 쓰는 것이 좋아보인다.<br>

[Optional 사용 시 유읙사항과 관련된 글](https://www.latera.kr/blog/2019-07-02-effective-optional/)들이 온라인에 많이 있으니 참고하면 좋겠다.
