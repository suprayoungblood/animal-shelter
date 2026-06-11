# UML Class Diagram — Animal Shelter

Two relationship kinds, each used where it belongs:

- **Inheritance (is-a):** `Dog`, `Cat`, and `Bird` extend the `Animal`
  base class, which holds the shared `name`, `age`, and `__str__`.
- **Containment (has-a):** the `Shelter` *has* up to `capacity`
  `Kennel`s, and each `Kennel` *has-an* `Animal`. The `Shelter` also
  keeps a per-type waiting list and an adoption log.

```mermaid
classDiagram
    class Animal {
        +str name
        +int age
        +__init__(name, age)
        +__str__() str
    }

    class Dog {
        +str breed
        +__init__(name, age, breed)
        +__str__() str
    }

    class Cat {
        +str fur_color
        +__init__(name, age, fur_color)
        +__str__() str
    }

    class Bird {
        +float wingspan
        +__init__(name, age, wingspan)
        +__str__() str
    }

    class Kennel {
        +Animal animal
        +__init__(animal)
        +is_empty() bool
        +add_animal(animal)
        +remove_animal() Animal
        +get_animal_type() str
        +__str__() str
    }

    class Shelter {
        +int capacity
        +list~Kennel~ kennels
        +dict~str,list~ waiting_list
        +list~AdoptionRecord~ adoptions
        +__init__(capacity)
        +is_full() bool
        +occupied_count() int
        +add_animal(animal) IntakeResult
        +adopt(animal_type, adopter) Animal|None
        +__str__() str
    }

    Animal <|-- Dog
    Animal <|-- Cat
    Animal <|-- Bird
    Shelter o-- "0..capacity" Kennel : contains
    Kennel o-- "0..1" Animal : contains
```

## ASCII fallback

```
                                +-------------+
                                |   Animal    |
                                |-------------|
                                | name        |
                                | age         |
                                | __str__()   |
                                +-------------+
                                      ^
                     is-a             | (inheritance)
              +-----------------------+-----------------------+
              |                       |                       |
        +-----------+           +-----------+           +-----------+
        |    Dog    |           |    Cat    |           |   Bird    |
        |-----------|           |-----------|           |-----------|
        | breed     |           | fur_color |           | wingspan  |
        +-----------+           +-----------+           +-----------+

+---------------+   contains    +-----------+   contains   +-----------+
|    Shelter    |<>-------------|  Kennel   |<>------------|  Animal   |
|---------------| 0..capacity   |-----------|    0..1      +-----------+
| capacity      |               | animal    |
| kennels       |               | isEmpty() |
| waiting_list  |               | add()     |
| adoptions     |               | remove()  |
| addAnimal()   |               | getType() |
| adopt()       |               +-----------+
+---------------+
```

**Legend**
- `--|>` / `^` : inheritance — Dog, Cat, and Bird ARE Animals.
- `o--` / `<>----` : aggregation (containment) — Shelter HAS Kennels; a Kennel HAS-AN Animal.
- `0..capacity` / `0..1` : multiplicities — kennels are capped by capacity; a kennel holds at most one animal.
