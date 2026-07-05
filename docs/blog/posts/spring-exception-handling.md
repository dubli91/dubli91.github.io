---
date: 2020-10-24
categories:
  - Springboot
tags:
  - Java
  - Springboot
slug: spring-exception-handling
---

# Spring Boot로 Exception 정의하기

REST API에서는 에러가 발생할 경우 404 같은 일반적인 status code가 아닌, 서버 쪽에서 정의한 error code를 별도로 리턴하는 경우가 있다. 서버쪽에서 error code를 별도로 정의하면 예를 들어 같은 404 에러라도 세분화하여 에러를 구분할 수 있고, 클라이언트 측에서도 상황별로 에러 처리를 하기가 편해진다.

보통은 @ExceptionHandler 및 @ControllerAdvice를 사용하는 듯 하지만, 이번에는 ErrorAttribute를 재정의하는 방법을 사용해본다.  

## DefaultErrorAttributes
Spring boot 기본 설정에서는 @RestController에서 예외가 발생하면 클라이언트에게 다음과 같은 형식으로 기본 error response가 전달된다.<br/>

```json
{
    "timestamp": "2020-10-20T11:57:49.947+00:00",
    "status": 404,
    "error": "Not found",
    "message": "blahblah",
    "path": "/user/abc"
}
```

이 에러형식은 ErrorAttribute를 구현한 DefaultErrorAttributes를 따른다. 따라서 이 DefaultErrorAttribute를 상속하여 구현하고 컴포넌트로 등록해주면 다음과 같이 error response를 커스텀할 수 있다. 

```json
{
    "errorCode": "TEST-40401",
    "message": "No such user - user" 
}
```

## Exception을 상속받는 커스텀 Exception 클래스 정의
DefaultErrorAttributes를 정의하기 전에 먼저 커스텀 Exception을 먼저 정의하자. Exception을 상속받은 커스텀 클래스를 만들면 된다.

```java
package com.expyh.exceptiontest.exception;

public class CustomException extends Exception{
    CustomError error;
    String message;

    public CustomException(CustomError error, String... args) {
        this.error = error;
        if (args.length > 0){
            this.message = String.format(error.getMessage(), args);
        }
        else {
            this.message = error.getMessage();
        }
    }

    public CustomError getError() {
        return error;
    }

    public void setError(CustomError error) {
        this.error = error;
    }

    @Override
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
```

이제 CustomException을 던질 때 매개변수로 넣어줄 Error를 정의하자. Error는 enum 형태로 정의하면 새로운 error code를 정의할 때나 Exception을 던질 때 편하다.

```java
public enum CustomError{
    //java의 에러가 아닌 erorCode로 표현되는 에러를 표현하는 것임.
    
    NO_SUCH_USER("TEST-40401", HttpStatus.BAD_REQUEST.value(), "No such user - %s"),

    String errorCode;
    int status;
    String message;

    CustomError(String errorCode, int status, String message) {
        this.errorCode = errorCode;
        this.status = status;
        this.message = message;
    }

    public String getErrorCode() {
        return errorCode;
    }

    public void setErrorCode(String errorCode) {
        this.errorCode = errorCode;
    }

    public int getStatus() {
        return status;
    }

    public void setStatus(int status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
```

이제 모든 준비가 끝났고 DefaultErrorAttributes만 재정의해주면 된다.  getErrorAttributes()를 이용해서 error response의 항목들을 가져온 다음 여기에 새로 추가하거나 제거함으로써 error response를 조정할 수 있다. 

원하는 로직을 적용하고 @Component를 이용해서 등록해준다.
```java
@Component
public class CustomErrorAttribute extends DefaultErrorAttributes {

    @Override
    public Map<String, Object> getErrorAttributes(WebRequest webRequest, ErrorAttributeOptions options) {
        Map <String, Object> errorAttributes = super.getErrorAttributes(webRequest, options);
        Throwable error = super.getError(webRequest);
        if (error instanceof CustomException) {
            errorAttributes.put("errorCode", ((CustomException) error).getError().getErrorCode() );
        }
        else {
            errorAttributes.put("errorCode", "TEST-50001");
        }
        errorAttributes.remove("timestamp");
        errorAttributes.remove("status");
        errorAttributes.remove("error");
        errorAttributes.remove("path");

        return errorAttributes;
    }

}
```

실제 컨트롤러에서 Exception을 던질 때는 CustomException의 매개변수로 enum으로 선언한 CustomError를 넣어주면 된다. 이렇게 되면 CustomErrorAttribute가 error response를 조작하여 우리가 원하는 형태로 클라이언트에게 전달해준다.

```java
@RestController
public class HelloController {
    List <String> users = Arrays.asList("expyh");
    @RequestMapping("/test/{user}")
    public String index(@PathVariable("user") String user) throws CustomException {
        if (!users.contains(user)){
            throw new CustomException(CustomError.NO_SUCH_USER, user);
        }
        return "Found : " + user ;
    }
}
```
