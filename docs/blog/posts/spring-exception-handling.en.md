---
date: 2020-10-24
categories:
  - Springboot
tags:
  - Java
  - Springboot
slug: spring-exception-handling
---

# Defining Exceptions in Spring Boot

In a REST API, when an error occurs you sometimes want to return a server-defined error code instead of just a generic status code like 404. Defining your own error codes on the server side lets you, for example, break the same 404 error down into finer-grained cases, and it also makes error handling on the client side much easier for each situation.

The usual approach seems to be @ExceptionHandler and @ControllerAdvice, but this time I'm going to try overriding ErrorAttributes instead.

## DefaultErrorAttributes
With Spring Boot's default configuration, when an exception occurs in a @RestController, the client receives a default error response in the following format.<br/>

```json
{
    "timestamp": "2020-10-20T11:57:49.947+00:00",
    "status": 404,
    "error": "Not found",
    "message": "blahblah",
    "path": "/user/abc"
}
```

This error format follows DefaultErrorAttributes, which implements ErrorAttributes. So by extending DefaultErrorAttributes and registering it as a component, we can customize the error response like this:

```json
{
    "errorCode": "TEST-40401",
    "message": "No such user - user" 
}
```

## Defining a custom Exception class that extends Exception
Before defining DefaultErrorAttributes, let's first define a custom Exception. All we need is a custom class that extends Exception.

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

Now let's define the Error that we'll pass as a parameter when throwing a CustomException. Defining errors as an enum makes it convenient both when defining new error codes and when throwing exceptions.

```java
public enum CustomError{
    //This represents errors expressed via errorCode, not Java errors.
    
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

Now everything is in place, and all that's left is to override DefaultErrorAttributes. We can use getErrorAttributes() to fetch the fields of the error response, and then adjust the error response by adding new fields or removing existing ones.

Apply whatever logic you want and register it with @Component.
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

When actually throwing the exception from a controller, just pass the CustomError enum value as a parameter to CustomException. With this in place, CustomErrorAttribute manipulates the error response and delivers it to the client in exactly the shape we want.

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
