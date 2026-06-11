# UML Class Diagram — Animal Shelter

Containment relationships only. **No inheritance** between any classes.
The `Shelter` *has* up to `capacity` `Kennel`s, and each `Kennel` *has-a*
(contains) at most one of: `Dog`, `Cat`, or `Bird`. The `Shelter` also keeps
a per-type waiting list of adopter names.

```mermaid
classDiagram
    class Dog {
        +str name
        +int age
        +str breed
        +__init__(name, age, breed)
        +__str__() str
    }

    class Cat {
        +str name
        +int age
        +str fur_color
        +__init__(name, age, fur_color)
        +__str__() str
    }

    class Bird {
        +str name
        +int age
        +float wingspan
        +__init__(name, age, wingspan)
        +__str__() str
    }

    class Kennel {
        +Dog|Cat|Bird animal
        +__init__(animal)
        +is_empty() bool
        +add_animal(animal)
        +remove_animal() Dog|Cat|Bird
        +get_animal_type() str
        +__str__() str
    }

    class Shelter {
        +int capacity
        +list~Kennel~ kennels
        +dict~str,list~ waiting_list
        +__init__(capacity)
        +is_full() bool
        +occupied_count() int
        +add_animal(animal) int
        +adopt(animal_type, adopter) Dog|Cat|Bird|None
        +__str__() str
    }

    Shelter o-- "0..capacity" Kennel : contains
    Kennel o-- "0..1" Dog  : contains
    Kennel o-- "0..1" Cat  : contains
    Kennel o-- "0..1" Bird : contains
```

## ASCII fallback (containment connectors)

```
+---------------+   contains    +-----------+   contains   +-----------+
|    Shelter    |<>-------------|  Kennel   |<>------------|    Dog    |
|---------------| 0..capacity   |-----------|              +-----------+
| capacity      |               | animal    |   contains   +-----------+
| kennels       |               | isEmpty() |<>------------|    Cat    |
| waiting_list  |               | add()     |              +-----------+
| addAnimal()   |               | remove()  |   contains   +-----------+
| adopt()       |               | getType() |<>------------|   Bird    |
+---------------+               +-----------+              +-----------+
```

**Legend**
- `o--` / `<>----` : aggregation (containment) — Shelter HAS Kennels; a Kennel HAS-A animal.
- `0..capacity` / `0..1` : multiplicities — kennels are capped by capacity; a kennel holds at most one animal.
- No `--|>` arrows: there is **no inheritance** between any classes.
