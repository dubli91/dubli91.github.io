---
date: 2024-07-23
categories:
  - Java
tags:
  - Java
  - Springboot
  - TestContainers
slug: testcontainers-jpa-test
---

# TestContainers를 활용한 JPA 유닛 테스트

오늘은 유닛 테스트를서작성하면서 가장 고민되었던 부분 중 하나인 DB관련 유닛 테스트에 대해 다뤄보려고 한다. 그리고 컨테이너 기술을 통해 DB 유닛 테스트를 도와주는 TestContainers를 소개한다.

## 1) DB 관련 테스트가 어려운 이유

유닛 테스트를 작성하거나 리팩토링(최적화)를 하고 싶을 때 DAO 클래스나 아니면 sql 쿼리 자체를 테스트해보고 싶은 경우가 있다.

내가 레거시 코드의 테스트코드를 작성하기로 맘 먹었을 때 가장 어려웠던 부분이 바로 sql과 관련된 테스트코드 작성이었다. 아직 레거시 코드들이 jdbcTemplate을 사용하고 있어서, DAO 클래스를 테스트하고 싶었는데, 아래와 같은 난관에 부딪혔다.

구글링을 해보니 다들 나와 비슷한 고민을 가지고 있었다.

- 테스트용 DB 준비부터 짜증남
- 로컬 DB를 설치하는 것부터 짜증남.
- 테이블을 일일히 생성하는 것도 짜증남
- 로컬에서 어찌어찌 돌리더라도 Git action 등 CI/CD 환경에서 돌리는 건 또 골치아프다
- 어찌어찌 성공하더라도 매 테스트마다 시간이 오래 걸림
- 테스트 DB 데이터의 정합성이 걱정됨
  - DAO 클래스를 테스트하려면 결국 테이블에 CRUD를 진행하고, 테스트가 끝나면 원상태로 돌려 놓아야함
  - DB의 다른 데이터를 건드리거나 삭제하거나 수정할 수도 있음
  - 심할 경우 운영중인 서비스에 영향이 갈 수도 있음


## 2) 새로운 대안 : Docker를 활용한 TestContainers

이런 상황에서, Docker를 가지고 위 문제들을 해결한 TestContainers라는게 있다는 사실을 발견했다.Spring 프레임워크에서도 지원된다(앗싸).

아쉽게도 JPA 를 사용해야하고 로컬에 Docker가 설치되어야 한다는 점 등등 현업에 적용할 수는 없었다(위에서도 말했지만, 내 레거시 코드는 jdbcTemplate을 쓴다), 대신 집에서 실습을 진행.


TestContainers를 사용하면 대략 다음과 같은 단계를 거친다.

1. Spring에 DB관련 코드 작성
    - Model 코드 작성
1. property 파일에 DB 연결 관련 코드 작성
1. TestContainers를 활용하여 통합 테스트 작성
1. 테스트 실행
1. Docker를 활용해 테스트용 DB 서버를 실행하고 테이블까지 만들어준다!
    - 테스트용 DB 서버에서 테스트를 진행
    - 테스트가 완료되면 Docker 이미지를 삭제


아래 실습 코드로 알아보자. 샘플 코드는 [TestContainerss 공식 웹페이지](https://testContainers.com/guides/testing-spring-boot-rest-api-using-testContainers/)에서 가져왔다. 


## 3) 코드 예제
### 3-1) 코드 준비
먼저 schema.sql로 create table 구문을 작성한다. 이 코드를 기준으로 테스트용 table이 생성된다.
```sql
create table if not exists customers (
    id bigserial not null,
    name varchar not null,
    email varchar not null,
    primary key (id),
    UNIQUE (email)
);
```

sql 스크립트를 실행해야하니까 init mode도 설정해주자.

```properties
spring.sql.init.mode=true
```


이제는 Spring 코드를 구현해보자. JPA에 따라 Repository, Entity도 그대로 구현해준다.
```java
package com.testcontainers.demo;

import org.springframework.data.jpa.repository.JpaRepository;

interface CustomerRepository extends JpaRepository<Customer, Long> {}
```

Entity에는 원본 코드와 다르게 lombok을 사용하여 코드량을 줄였다.

```java
package com.testcontainers.demo;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.AllArgsConstructor;

@Data
@AllArgsConstructor
@Entity
@Table(name = "customers")
class Customer {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false)
  private String name;

  @Column(nullable = false, unique = true)
  private String email;

}

```

실습용 웹 어플리케이션의 Controller 단이다. 단순하게 구매자 정보를 전부 읽어오는 API가 있다.

```java
package com.testcontainers.demo;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
class CustomerController {

  private final CustomerRepository repo;

  CustomerController(CustomerRepository repo) {
    this.repo = repo;
  }

  @GetMapping("/api/customers")
  List<Customer> getAll() {
    return repo.findAll();
  }
}
```

### 3-2) 테스트 코드 작성

튜토리얼 문서에서는 RestAssured를 사용했기 때문에 똑같이 작성하겠다. mockMvc도 된다고 하지만, 이번 기회에 RestAssured도 구경해보는 것도 좋을 것 같다.

아래가 테스트코드이다. 

우선 컨트롤러 테스트니까 SpringBootTest로 설정해주고 RandomPort로 열겠다.

그리고 static으로 Containers를 작성한다. 원래 실습 코드는 mysqls를 사용하나, 나는 mysql 도 되는지 궁금하여 mysql로 작성해보았다. mysqls에서 mysql로 바꾸는 과정이 매우 간단해서 맘에 들었다. 

도커 이미지를 넣으면 도커 레지스트리에서 그대로 받아와서 띄워준다(편하다!). @BeforeAll/@AfterAl에는 컨테이너를 start / stop할 수 있도록 코드를 작성해준다.

@DynamicPropertySource에는 DB연결에 필요한 정보들을 작성해준다.

@BeforeEach에서는 baseurl의 포트를 설정하고(@springBootTest에서 RANDOM_PORT옵션을 줬기 때문),  매테스트마다 DB 테이블을 리셋할 수 있도록 customerRepository.deleteAll()을 호출해준다.

테스트 코드는 shouldGetAllCustomers() 인데, RestAssured로 작성되어 있다.

```java
package com.testcontainers.demo;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.hasSize;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import java.util.List;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.MySQLContainer;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class CustomerControllerTest {

  @LocalServerPort
  private Integer port;

  static MysqlContainer<?> mysql = new MySQLContainer<>(
    "mysql:8.0.39"
  );

  @BeforeAll
  static void beforeAll() {
    mysql.start();
  }

  @AfterAll
  static void afterAll() {
    mysql.stop();
  }

  @DynamicPropertySource
  static void configureProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", mysql::getJdbcUrl);
    registry.add("spring.datasource.username", mysql::getUsername);
    registry.add("spring.datasource.password", mysql::getPassword);
  }

  @Autowired
  CustomerRepository customerRepository;

  @BeforeEach
  void setUp() {
    RestAssured.baseURI = "http://localhost:" + port;
    customerRepository.deleteAll();
  }

  @Test
  void shouldGetAllCustomers() {
    List<Customer> customers = List.of(
      new Customer(null, "John", "john@mail.com"),
      new Customer(null, "Dennis", "dennis@mail.com")
    );
    customerRepository.saveAll(customers);

    given()
      .contentType(ContentType.JSON)
      .when()
      .get("/api/customers")
      .then()
      .statusCode(200)
      .body(".", hasSize(2));
  }
}
```


## 4) 결론

TestContainers를 통해 기존의 문제점이 다음과 같이 해결되었다!

1. 테스트용 DB 준비가 어렵다
    - 기존에 작성한 운영 코드들을 대부분 사용할 수 있고 테스트용 연결정보는 테스트 코드에 넣으면 된다.
    - 테스트 환경에 도커를 실행할 수만 있다면 CI/CD 환경에서도 테스트를 실행할 수 있다!
2. 테스트 시간이 너무 길다
    - 테스트용 DB를 직접 생성하고 연결하는 것보다 훨씬 낫다.
3. 테스트 DB 데이터의 정합성이 걱정된다
    - 테이블이 docker 이미지를 통해 생성, 삭제 때문에 걱정 없음!


다만 다음과 같은 제약사항이 있다.

1. docker가 필요하다
    - 로컬에서 도커를 못 돌리는 나의 직장은 사용하지 못한다. 
    - 프록시나 정책 문제로 docker를 이용하기 힘들거나 docker 이미지 레지스트리 연결등이 원활하지 않다면 실행하기 힘들다.
2. 비교적 최신의 spring 버전이 필요하다. 따라서 레거시 코드들에 적용하기 어렵다.

현업에서 당장은 못쓰고 개인 토이프로젝트나 새로운 프로젝트를 시작할 때 적극적으로 써 봐야겠다.
