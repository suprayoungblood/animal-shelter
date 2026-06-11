"""Unit tests for the Dog, Cat, and Bird classes."""
import unittest

from animals import Bird, Cat, Dog


class TestDog(unittest.TestCase):
    """Tests for the Dog class."""

    def test_overloaded_constructor_sets_attributes(self):
        """The constructor stores name, age, and breed."""
        dog = Dog("Charlie", 7, "Golden Retriever")
        self.assertEqual(dog.name, "Charlie")
        self.assertEqual(dog.age, 7)
        self.assertEqual(dog.breed, "Golden Retriever")

    def test_constructor_defaults(self):
        """Calling Dog() with no arguments uses the default values."""
        dog = Dog()
        self.assertEqual(dog.name, "Unknown")
        self.assertEqual(dog.age, 0)
        self.assertEqual(dog.breed, "Mixed")

    def test_str_format(self):
        """__str__ matches the required output format."""
        dog = Dog("Charlie", 7, "Golden Retriever")
        self.assertEqual(
            str(dog), "Dog: Name: Charlie, Age: 7, Breed: Golden Retriever"
        )

    def test_no_inheritance(self):
        """Dog inherits only from object — no shared animal base class."""
        self.assertEqual(Dog.__bases__, (object,))


class TestCat(unittest.TestCase):
    """Tests for the Cat class."""

    def test_overloaded_constructor_sets_attributes(self):
        """The constructor stores name, age, and fur color."""
        cat = Cat("Luna", 5, "Orange Tabby")
        self.assertEqual(cat.name, "Luna")
        self.assertEqual(cat.age, 5)
        self.assertEqual(cat.fur_color, "Orange Tabby")

    def test_constructor_defaults(self):
        """Calling Cat() with no arguments uses the default values."""
        cat = Cat()
        self.assertEqual(cat.name, "Unknown")
        self.assertEqual(cat.age, 0)
        self.assertEqual(cat.fur_color, "Tabby")

    def test_str_format(self):
        """__str__ matches the required output format."""
        cat = Cat("Luna", 5, "Orange Tabby")
        self.assertEqual(
            str(cat), "Cat: Name: Luna, Age: 5, Fur Color: Orange Tabby"
        )

    def test_no_inheritance(self):
        """Cat inherits only from object."""
        self.assertEqual(Cat.__bases__, (object,))


class TestBird(unittest.TestCase):
    """Tests for the Bird class."""

    def test_overloaded_constructor_sets_attributes(self):
        """The constructor stores name, age, and wingspan."""
        bird = Bird("Tweety", 1, 6.5)
        self.assertEqual(bird.name, "Tweety")
        self.assertEqual(bird.age, 1)
        self.assertEqual(bird.wingspan, 6.5)

    def test_constructor_defaults(self):
        """Calling Bird() with no arguments uses the default values."""
        bird = Bird()
        self.assertEqual(bird.name, "Unknown")
        self.assertEqual(bird.age, 0)
        self.assertEqual(bird.wingspan, 0.0)

    def test_str_format(self):
        """__str__ matches the required output format."""
        bird = Bird("Tweety", 1, 6.5)
        self.assertEqual(
            str(bird), "Bird: Name: Tweety, Age: 1, Wingspan: 6.5"
        )

    def test_no_inheritance(self):
        """Bird inherits only from object."""
        self.assertEqual(Bird.__bases__, (object,))


if __name__ == "__main__":
    unittest.main()
