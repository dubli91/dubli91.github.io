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

# JPA Unit Testing with TestContainers

Today I want to cover one of the parts of writing unit tests that I've agonized over the most: DB-related unit tests. I'll also introduce TestContainers, which uses container technology to make DB unit testing easier.

## 1) Why DB-Related Tests Are Hard

When writing unit tests or doing refactoring (optimization), there are times you want to test a DAO class, or even the SQL queries themselves.

When I decided to write test code for our legacy codebase, the hardest part was exactly this: writing tests involving SQL. The legacy code still uses jdbcTemplate, and I wanted to test the DAO classes, but I ran into the obstacles below.

After some googling, it turned out everyone had the same struggles I did.

- Preparing a test DB is annoying from the start
- Even installing a local DB is annoying.
- Creating every table by hand is annoying too
- Even if you somehow get it running locally, getting it to run in a CI/CD environment like GitHub Actions is another headache
- Even if you somehow succeed, every test run takes a long time
- You worry about the integrity of the test DB data
  - Testing a DAO class ultimately means running CRUD against tables, and you have to restore everything to its original state when the test finishes
  - You might touch, delete, or modify other data in the DB
  - In the worst case, you could even affect a live production service


## 2) A New Alternative: TestContainers, Powered by Docker

In this situation, I discovered that something called TestContainers exists, which solves the problems above using Docker. It's even supported by the Spring framework (nice!).

Unfortunately I couldn't apply it at work — it requires JPA, and Docker has to be installed locally, among other things (as I mentioned, my legacy code uses jdbcTemplate) — so I did this hands-on practice at home instead.


Using TestContainers goes roughly through these steps:

1. Write the DB-related code in Spring
    - Write the Model code
1. Write the DB connection settings in the property file
1. Write an integration test using TestContainers
1. Run the test
1. It uses Docker to spin up a test DB server and even creates the tables for you!
    - The test runs against the test DB server
    - When the test completes, the Docker image is removed


Let's walk through it with the practice code below. The sample code comes from the [TestContainers official website](https://testContainers.com/guides/testing-spring-boot-rest-api-using-testContainers/).


## 3) Code Example
### 3-1) Setting Up the Code
First, write the create table statement in schema.sql. The test tables are created based on this code.
```sql
create table if not exists customers (
    id bigserial not null,
    name varchar not null,
    email varchar not null,
    primary key (id),
    UNIQUE (email)
);
```

Since we need the SQL script to run, let's also set the init mode.

```properties
spring.sql.init.mode=true
```


Now let's implement the Spring code. Following JPA, we implement the Repository and Entity as usual.
```java
package com.testcontainers.demo;

import org.springframework.data.jpa.repository.JpaRepository;

interface CustomerRepository extends JpaRepository<Customer, Long> {}
```

Unlike the original code, I used Lombok in the Entity to cut down on boilerplate.

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

Here's the Controller layer of the practice web application. There's a single simple API that reads all the customer records.

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

### 3-2) Writing the Test Code

The tutorial document used RestAssured, so I'll write it the same way. Apparently mockMvc works too, but I figured this was a good chance to check out RestAssured as well.

Below is the test code.

First, since this is a controller test, we configure it with SpringBootTest and open it on a RandomPort.

Then we declare the container as static. The original practice code uses mysqls, but I was curious whether mysql would also work, so I wrote it with mysql. I liked how simple the switch from mysqls to mysql turned out to be.

If you specify a Docker image, it pulls it straight from the Docker registry and spins it up (so convenient!). In @BeforeAll/@AfterAl we write the code to start / stop the container.

In @DynamicPropertySource we set the information needed for the DB connection.

In @BeforeEach we set the base URL's port (because we gave the RANDOM_PORT option in @springBootTest), and call customerRepository.deleteAll() so the DB table is reset before every test.

The test itself is shouldGetAllCustomers(), written with RestAssured.

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


## 4) Conclusion

TestContainers solved the original problems like this!

1. Preparing a test DB is hard
    - You can reuse most of your existing production code, and the test connection info just goes into the test code.
    - As long as your test environment can run Docker, you can run the tests in CI/CD too!
2. Tests take too long
    - It's much better than creating and connecting to a test DB by hand.
3. You worry about the integrity of the test DB data
    - No worries, since the tables are created and destroyed via the Docker image!


However, there are the following constraints.

1. Docker is required
    - My workplace, where we can't run Docker locally, can't use it.
    - If proxies or policies make Docker hard to use, or connecting to a Docker image registry doesn't work smoothly, it's hard to run.
2. It needs a relatively recent Spring version, so it's hard to apply to legacy code.

I can't use it at work right now, but I'll definitely put it to active use in personal toy projects or when starting a new project.
