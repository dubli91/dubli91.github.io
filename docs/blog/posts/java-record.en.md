---
date: 2023-08-25
categories:
  - Java
tags:
  - Java
  - Record
slug: java-record
---

# Notes on Records

I was watching Toby's Spring lectures on YouTube when Records came up. As someone who makes a living with Java and Spring, I was more than a little flustered to hear a keyword I had never encountered before. A bit of googling suggested it's actually quite an important keyword, on par with class, interface, and the like — so I'm writing up my notes here.

## What a Java Record Is
It turns out Records first appeared in Java 14 and became a standard feature in Java 16. Here's the definition from JEP 359.

> *Records* are a new kind of type declaration in the Java language. Like an `enum`, a `record` is a restricted form of class. It declares its representation, and commits to an API that matches that representation. Records give up a freedom that classes usually enjoy: the ability to decouple API from representation. In return, records gain a significant degree of concision.

## Why It Was Created
Even to create classes that merely represent data, traditional Java forces you to write a mountain of code (the so-called boilerplate: equals(), getters, setters, and so on). That comes with the following problems:

1. There's room for errors to creep in while writing the boilerplate.
2. IDEs like IntelliJ can generate the code in no time these days, but it's still verbose — so from another programmer's perspective, it's hard to tell at a glance whether a class is purely a data carrier or whether it also contains some functions or logic.

## How to Use It

The code is written as shown below. It's a type declaration, but what's distinctive is that it's declared in a form resembling a function. You declare the fields you want the Record to contain inside the parentheses. Then the following happens:

- The fields in the parentheses are declared final.
- Public accessors are declared automatically. However, instead of the usual getterField() style, you access them simply by the field name, as in field().
- A canonical constructor is declared automatically. It takes the Record's declared fields as arguments, in order.
- toString(), hashCode(), and equals() are also auto-generated. equals() returns true when comparing the same record type with all field values equal.

Additionally, it appears that static variables and methods can be declared just like in a class. A record cannot be abstract, but implementing an interface seems to be possible... I'll have to check the spec or verify with the IDE whenever I actually need it.

You can also add extra constructors. You can declare parameters explicitly, or, if you declare no parameters, it replaces the default canonical constructor.

A constructor with explicitly declared parameters ultimately has to call the canonical constructor via this(), and this() can only appear as the first statement of the constructor. So it looks like adding any logic before the this() call is impossible. A constructor with parameters ends up simply forwarding its variables to the canonical constructor, and any data validation logic apparently has to happen in the canonical constructor itself.

```java
// Declaring a Java Record and its constructors
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


That was a quick look — and personally, I don't think I'll be using it. Here's why:

- It can't be used as a JPA Entity → presumably because it has no getter/setter methods and only final fields.
- Lombok already cuts down plenty of boilerplate methods on its own.
- My company is still on Java 8 (oops!).

I've heard that not just my company but most codebases out there still run on Java 8. Will Records catch on once Java 16+ becomes mainstream? Honestly, I'm not sure. Still, I think the fact that Java now natively supports an immutable data structure is meaningful in itself.
