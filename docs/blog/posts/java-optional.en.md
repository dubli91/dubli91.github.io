---
date: 2023-09-22
categories:
  - Java
tags:
  - Java
  - Optional
slug: java-optional
---

# Notes on Optional

I've been refactoring some code that's about six years old, and I kept running into places where values get wrapped in Optional and unwrapped again over and over. I started wondering: is Optional being used where it isn't really needed, or is it being used correctly and I just don't understand it? So I studied up and wrote down what I learned.

## What Java's Optional is
It seems to be a concept that was introduced in Java 8 along with Lambdas. There doesn't appear to be a dedicated JEP for it, so instead here's the description from the API docs.

> A container object which may or may not contain a non-null value. If a value is present, isPresent() will return true and get() will return the value.

## Why it was created
Brian Goetz, a Java architect, explains it like this. [It's on page 36 of this document.](https://stuartmarks.files.wordpress.com/2015/10/con6851-api-design-v2.pdf)

> Optional is intended to provide a limited mechanism for library method return types where there is a clear need to represent "no result," and where using null for that is overwhelmingly likely to cause errors.

## Basic concepts / how to create one
In Java, an object either holds a value or it doesn't (null). Wrapping an object in Optional splits it into two cases: the Optional has a value, or it's empty.
There are three ways to create an Optional.

- Use Optional.of(object). You can only use this when you're certain the value isn't null. Passing null here throws a NullPointerException.
- Use Optional.ofNullable(object). Use this when you're not sure whether the value is null. Passing null here gives you Optional.empty.
- Use Optional.empty() to create an Optional.empty.

To check whether an Optional is empty or not, use isPresent(). To get the value back out of an Optional, use get().

See the code below.
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
One more thing: calling get() on an empty Optional throws a NoSuchElementException. So if you really want to pull the value out with get(), checking with isPresent() first is a must.


## The point of Optional

The one that really matters here is Optional.ofNullable(). If you already know for sure whether a value exists or not, there's no reason to wrap it. <br>

Optional provides an API for dealing with "objects that may or may not be null." Previously, in these uncertain situations you had to do null checks one by one, which bloated the code and made it easy to introduce errors. Optional handles this a bit more elegantly.
Below is code using Optional's most representative functions, map() and orElse(), written to behave identically to the traditional if-statement version.


```java
// Java Record declaration and Constructor declaration
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

First, map(), one of the most commonly used Optional functions, works like this:
- If the input Optional has a value, it runs the function and wraps the result back into an Optional.
- If the input Optional is empty, it skips the function and passes the empty Optional straight through.

Looking at the example above, you can see that the Optional API eliminates the nested if statements and handles everything through readable function chaining.
Other functions like filter() also take an Optional and return an Optional, so they can be used in function chains as well.

And at the end, orElse() acts on the final result of the Optional chain like this:
- If the input is an Optional with a value, it returns that value as is.
- If the input is an empty Optional, it returns the specified fallback value.

So in the case above, if Address::getCountry has a value, that value is returned; otherwise "not specified" is returned.


## Conclusion
As a way to wrap null once and prevent NullPointerExceptions, Optional is a welcome addition — but it's also frequently misused.
Wrapping and unwrapping with Optional costs compute, and a different kind of exception can still occur (NoSuchElementException). <br>

You sometimes see Optional taken as a method parameter or returned from a method, but this forces extra logic onto the caller and can cause confusion,
so I'd avoid that and instead finish Optional operations within a single statement using chaining and the like.
For a simple null check, sticking with the traditional == seems better.<br>

There are plenty of [articles online about the pitfalls of using Optional](https://www.latera.kr/blog/2019-07-02-effective-optional/), so they're worth a look.
