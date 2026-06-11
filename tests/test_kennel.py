"""Unit tests for the Kennel class."""
import unittest

from animals import Bird, Cat, Dog
from kennel import Kennel


class TestKennel(unittest.TestCase):
    """Tests for the Kennel class and its behaviors."""

    def test_constructor_with_animal(self):
        """The overloaded constructor stores the animal it is given."""
        dog = Dog("Charlie", 7, "Golden Retriever")
        kennel = Kennel(dog)
        self.assertIs(kennel.animal, dog)

    def test_constructor_empty_by_default(self):
        """A kennel created with no argument starts empty."""
        kennel = Kennel()
        self.assertIsNone(kennel.animal)

    def test_get_animal_type_uses_name_attribute(self):
        """get_animal_type returns the class name via __name__."""
        self.assertEqual(Kennel(Dog()).get_animal_type(), "Dog")
        self.assertEqual(Kennel(Cat()).get_animal_type(), "Cat")
        self.assertEqual(Kennel(Bird()).get_animal_type(), "Bird")

    def test_get_animal_type_when_empty(self):
        """An empty kennel reports 'Empty'."""
        self.assertEqual(Kennel().get_animal_type(), "Empty")

    def test_add_animal_places_animal(self):
        """add_animal stores the animal in an empty kennel."""
        kennel = Kennel()
        cat = Cat("Luna", 5, "Orange Tabby")
        kennel.add_animal(cat)
        self.assertIs(kennel.animal, cat)

    def test_cannot_add_more_than_one_animal(self):
        """Adding a second animal raises ValueError."""
        kennel = Kennel()
        kennel.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        with self.assertRaises(ValueError):
            kennel.add_animal(Cat("Luna", 5, "Orange Tabby"))

    def test_constructor_rejects_invalid_type(self):
        """A non-animal object passed to the constructor raises TypeError."""
        with self.assertRaises(TypeError):
            Kennel("not an animal")

    def test_add_animal_rejects_invalid_type(self):
        """add_animal rejects objects that are not Dog, Cat, or Bird."""
        with self.assertRaises(TypeError):
            Kennel().add_animal(42)

    def test_str_format_matches_example(self):
        """__str__ matches the required 'Kennel Animal:' output format."""
        kennel = Kennel(Dog("Charlie", 7, "Golden Retriever"))
        self.assertEqual(
            str(kennel),
            "Kennel Animal: Dog: Name: Charlie, Age: 7, Breed: Golden Retriever",
        )

    def test_is_empty_reflects_occupancy(self):
        """is_empty is True with no animal and False once one is added."""
        kennel = Kennel()
        self.assertTrue(kennel.is_empty())
        kennel.add_animal(Dog())
        self.assertFalse(kennel.is_empty())

    def test_remove_animal_returns_and_empties(self):
        """remove_animal hands back the occupant and empties the kennel."""
        dog = Dog("Charlie", 7, "Golden Retriever")
        kennel = Kennel(dog)
        self.assertIs(kennel.remove_animal(), dog)
        self.assertTrue(kennel.is_empty())

    def test_remove_animal_from_empty_kennel_raises(self):
        """Removing from an empty kennel raises ValueError."""
        with self.assertRaises(ValueError):
            Kennel().remove_animal()

    def test_no_inheritance(self):
        """Kennel inherits only from object — containment, not inheritance."""
        self.assertEqual(Kennel.__bases__, (object,))


if __name__ == "__main__":
    unittest.main()
