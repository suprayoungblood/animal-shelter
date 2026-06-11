"""Animal base class — common attributes and behaviors for all animals.

Every shelter animal IS-AN Animal: the shared name and age live here,
along with the shared string formatting. Subclasses add only their own
unique attribute and extend __str__ via super().
"""


class Animal:
    """Base class holding the attributes every animal shares."""

    def __init__(self, name: str = "Unknown", age: int = 0):
        """Overloaded constructor via default arguments.

        :param name: Animal's name.
        :param age: Animal's age in years.
        """
        self.name = name
        self.age = age

    def __str__(self) -> str:
        """Overloaded string representation of the shared attributes.

        Uses the concrete subclass's __name__ so output reads
        'Dog: Name: ..., Age: ...' without subclasses repeating it.
        """
        return f"{type(self).__name__}: Name: {self.name}, Age: {self.age}"
