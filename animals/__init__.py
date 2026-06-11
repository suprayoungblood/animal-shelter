"""Animal package: standalone Dog, Cat, and Bird classes (no inheritance).

ANIMAL_TYPES is the single source of truth for every animal type the
shelter system supports. Kennel validation, shelter waiting lists, and
both UIs derive their type lists from it — add a new animal class here
and the whole application picks it up.
"""
from animals.dog import Dog
from animals.cat import Cat
from animals.bird import Bird

ANIMAL_TYPES: dict[str, type] = {cls.__name__: cls for cls in (Dog, Cat, Bird)}

__all__ = ["Dog", "Cat", "Bird", "ANIMAL_TYPES"]
