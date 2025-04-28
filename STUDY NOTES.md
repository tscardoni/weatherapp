# Training Sprint Presentation

## Introduction

This document provides a brief summary of the key concepts I studied during my training sprint in February–March 2025. I focused on deepening my understanding of **software design patterns** applied to Python, my primary programming language at the moment, using the Packt-published book [Mastering Python Design Patterns](https://www.packtpub.com/en-us/product/mastering-python-design-patterns-9781837639618).

I hope this resource proves useful to other students considering the same topics.

**Disclaimer:**  
Throughout my studies and final project, I used **Generative AI tools** as a learning aid, primarily treating AI as a tutor. I found that asking the right questions significantly helped me validate my understanding, even though the responses were not always complete or entirely accurate, in my opinion.

- What are design patterns?
  - Reusable solutions to common problems in software design.
  - A common language for discussing design.
- Why are they important?
  - They improve code **flexibility**, **maintainability**, and **reusability**.
  - They facilitate communication between developers.
  - They help build more robust and scalable systems.
- Course Objectives:
  - Understand the **fundamental principles of design**.
  - Learn to apply **creational**, **structural**, and **behavioral design patterns**.
  - Explore **architectural patterns** for complex system design.
  - Understand patterns for **concurrency**, **performance**, and **distributed systems**.
  - Write **more effective tests** using specific patterns.
  - Avoid common **anti-patterns in Python**.

## Module 1 - Fundamental Design Principles (Based on Chapter 1)

- **Encapsulate What Varies**
  - Isolate the parts of the system that are prone to change.
  - Techniques: **Polymorphism**, **Getters and setters** OR **property**.
- **Favor Composition Over Inheritance**
  - Build complex objects from simpler ones.
  - Flexibility and code reusability.
- **Program to an Interface, Not an Implementation**
  - Depend on abstractions (**ABCs**, **Protocols**).
  - Flexibility and maintainability.
- **Loose Coupling Between Program Parts**
  - Minimize dependencies between objects.
  - Techniques: **Dependency Injection**, **Observer Pattern**.

## Module 2 - SOLID Principles (Based on Chapter 2)

- **Single Responsibility Principle (SRP)**
  - A class should have only one reason to change.
- **Open/Closed Principle (OCP)**
  - Open for extension, closed for modification.
- **Liskov Substitution Principle (LSP)**
  - Subtypes must be substitutable for their base types.
- **Interface Segregation Principle (ISP)**
  - Clients should not be forced to depend on interfaces they do not use.
- **Dependency Inversion Principle (DIP)**
  - Depend on abstractions, not concrete implementations.

## Subsequent Modules - Creational, Structural, and Behavioral Patterns (Based on Chapters 3, 4, and 5)

- **Creational Patterns:** **Factory Pattern**, **Builder Pattern**, **Prototype Pattern**, **Singleton Pattern**, **Object Pool Pattern**.
- **Structural Patterns:** **Decorator Pattern**, **Bridge Pattern**, **Facade Pattern**, **Flyweight Pattern**, **Proxy Pattern**.
- **Behavioral Patterns:** **Chain of Responsibility Pattern**, **Command Pattern**, **Observer Pattern**, **State Pattern**, **Strategy Pattern**, etc..
- Brief introduction to each category and some key patterns with their benefits and use cases.

## Advanced Modules - Architectural, Concurrency, Performance, and Distributed Systems Patterns (Based on Chapters 6, 7, 8, and 9)

- **Architectural Patterns:** **Model-View-Controller (MVC)**, **Microservices**, **Serverless**, **Event Sourcing**.
- **Concurrency and Asynchronous Patterns:** **The Thread Pool Pattern**, **The Worker Model Pattern**, **The Future and Promise Pattern**, **The Observer Pattern in Reactive Programming**.
- **Performance Patterns:** **Cache-Aside Pattern**, **Memoization Pattern**, **Lazy Loading Pattern**.
- **Distributed Systems Patterns:** **The Throttling Pattern**, **The Retry Pattern**, **The Circuit Breaker Pattern**.
- Highlight how these patterns address specific challenges in larger contexts.

## Module 10 - Patterns for Testing (Based on Chapter 10)

- **The Mock Object Pattern**: Simulate dependencies for isolated tests.
- **The Dependency Injection Pattern**: Facilitate testing by making dependencies replaceable.
- Importance of writing reliable and maintainable tests.

## Module 11 - Python Anti-patterns (Based on Chapter 11)

- Examples of **code style violations** (**PEP 8**).
- **Correctness anti-patterns** (e.g., incorrect use of `type()`, mutable default arguments).
- **Maintainability anti-patterns** (e.g., wildcard imports, overusing inheritance).
- **Performance anti-patterns** (e.g., string concatenation in loops).
- Importance of writing clean and efficient code.
