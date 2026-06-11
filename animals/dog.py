"""Dog class — standalone, no inheritance."""


class Dog:
    """Represents a dog with a name, age, and breed."""

    def __init__(self, name: str = "Unknown", age: int = 0, breed: str = "Mixed"):
        """Overloaded constructor via default arguments.

        :param name: Dog's name.
        :param age: Dog's age in years.
        :param breed: Dog's breed.
        """
        self.name = name
        self.age = age
        self.breed = breed

    def __str__(self) -> str:
        """Overloaded string representation."""
        return f"Dog: Name: {self.name}, Age: {self.age}, Breed: {self.breed}"
