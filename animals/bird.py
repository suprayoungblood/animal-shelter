"""Bird class — inherits shared attributes from Animal."""
from animals.animal import Animal


class Bird(Animal):
    """A bird IS-AN Animal with a wingspan."""

    def __init__(self, name: str = "Unknown", age: int = 0, wingspan: float = 0.0):
        """Overloaded constructor via default arguments.

        :param name: Bird's name.
        :param age: Bird's age in years.
        :param wingspan: Bird's wingspan in inches.
        """
        super().__init__(name, age)
        self.wingspan = wingspan

    def __str__(self) -> str:
        """Extend the inherited representation with the wingspan."""
        return f"{super().__str__()}, Wingspan: {self.wingspan}"
