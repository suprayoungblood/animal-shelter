"""Animal package: Animal base class with Dog, Cat, and Bird subclasses.

ANIMAL_TYPES is the single source of truth for every concrete animal type
the shelter system supports. Shelter waiting lists and both UIs derive
their type lists from it — add a new Animal subclass here and the whole
application picks it up.
"""
from animals.animal import Animal
from animals.dog import Dog
from animals.cat import Cat
from animals.bird import Bird

ANIMAL_TYPES: dict[str, type[Animal]] = {
    cls.__name__: cls for cls in (Dog, Cat, Bird)
}

__all__ = ["Animal", "Dog", "Cat", "Bird", "ANIMAL_TYPES"]
