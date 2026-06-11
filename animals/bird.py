"""Bird class — standalone, no inheritance."""


class Bird:
    """Represents a bird with a name, age, and wingspan."""

    def __init__(self, name: str = "Unknown", age: int = 0, wingspan: float = 0.0):
        """Overloaded constructor via default arguments.

        :param name: Bird's name.
        :param age: Bird's age in years.
        :param wingspan: Bird's wingspan in inches.
        """
        self.name = name
        self.age = age
        self.wingspan = wingspan

    def __str__(self) -> str:
        """Overloaded string representation."""
        return (
            f"Bird: Name: {self.name}, Age: {self.age}, "
            f"Wingspan: {self.wingspan}"
        )
