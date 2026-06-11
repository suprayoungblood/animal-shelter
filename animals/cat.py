"""Cat class — standalone, no inheritance."""


class Cat:
    """Represents a cat with a name, age, and fur color."""

    def __init__(self, name: str = "Unknown", age: int = 0, fur_color: str = "Tabby"):
        """Overloaded constructor via default arguments.

        :param name: Cat's name.
        :param age: Cat's age in years.
        :param fur_color: Cat's fur color.
        """
        self.name = name
        self.age = age
        self.fur_color = fur_color

    def __str__(self) -> str:
        """Overloaded string representation."""
        return f"Cat: Name: {self.name}, Age: {self.age}, Fur Color: {self.fur_color}"
