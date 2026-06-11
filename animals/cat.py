"""Cat class — inherits shared attributes from Animal."""
from animals.animal import Animal


class Cat(Animal):
    """A cat IS-AN Animal with a fur color."""

    def __init__(self, name: str = "Unknown", age: int = 0, fur_color: str = "Tabby"):
        """Overloaded constructor via default arguments.

        :param name: Cat's name.
        :param age: Cat's age in years.
        :param fur_color: Cat's fur color.
        """
        super().__init__(name, age)
        self.fur_color = fur_color

    def __str__(self) -> str:
        """Extend the inherited representation with the fur color."""
        return f"{super().__str__()}, Fur Color: {self.fur_color}"
