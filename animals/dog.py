"""Dog class — inherits shared attributes from Animal."""
from animals.animal import Animal


class Dog(Animal):
    """A dog IS-AN Animal with a breed."""

    def __init__(self, name: str = "Unknown", age: int = 0, breed: str = "Mixed"):
        """Overloaded constructor via default arguments.

        :param name: Dog's name.
        :param age: Dog's age in years.
        :param breed: Dog's breed.
        """
        super().__init__(name, age)
        self.breed = breed

    def __str__(self) -> str:
        """Extend the inherited representation with the breed."""
        return f"{super().__str__()}, Breed: {self.breed}"
