---
date: 2020-12-07
categories:
  - java
tags:
  - Java
slug: main-overriding-overloading
---

# Overriding / Overloading the Main Method

The main method serves as both the beginning and the end of a Java program, which gives the impression that it must be treated differently from other methods.

```java
public class Main {
    public static void main(String[] args){
        System.out.println("Hello World");
    }
}
```
<br>
So, can this method be overridden or overloaded?
<br>

# 1) Overriding

Of course not. The reason is that the main method is static, and static methods cannot be overridden.

```java
//Fails
public class ChildMain extends Main{
    //Method does not override method from its superclass
    @Override
    public static void main(String[] args) {
        System.out.println("hello world2");
    }
}
```
<br>
Here's why static methods cannot be overridden:
- For static methods, which method a class will call is decided at compile time, not at runtime, so overriding is impossible.
- Static methods are not inherited by child classes in the first place(!)

[//]: # (Hello)
<br>

So if you remove @Override as shown below, there's no compile error. However, the main method in Main and the main method in ChildMain are completely unrelated, entirely separate methods. Calling the parent class's method with super(); is of course impossible too.

<br>

```java
public class ChildMain extends Main{

    //Fails 
    /*        
    public static void main(String[] args) {
        super();
    }
    */

    //Succeeds
    public static void main(String[] args) {
        System.out.println("hello world2");
    }
}
```
<br>

# 2) Overloading

Overloading, surprisingly, is possible. But when the program runs, it's the main method taking String[] args as its parameter that gets executed.
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
If you really want to use one of the other main methods, your only option is to call it from inside main(String[] args) like this.
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

# Conclusion
- The main method essentially follows the same rules as any other method.
- The main method is static, so @Override doesn't work on it.
- The main method can be overloaded, but there doesn't seem to be much reason to bother.
<br>
<br>

Knowledge acquired.
