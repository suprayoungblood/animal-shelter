"""Unit tests for the Animal base class and the Dog, Cat, Bird subclasses."""
import unittest

from animals import Animal, Bird, Cat, Dog


class TestAnimal(unittest.TestCase):
    """Tests for the Animal base class."""

    def test_constructor_sets_shared_attributes(self):
        """The base constructor stores name and age."""
        animal = Animal("Generic", 4)
        self.assertEqual(animal.name, "Generic")
        self.assertEqual(animal.age, 4)

    def test_constructor_defaults(self):
        """Calling Animal() with no arguments uses the default values."""
        animal = Animal()
        self.assertEqual(animal.name, "Unknown")
        self.assertEqual(animal.age, 0)

    def test_str_outputs_shared_data(self):
        """__str__ reports the class name, name, and age."""
        self.assertEqual(str(Animal("Generic", 4)), "Animal: Name: Generic, Age: 4")


class TestInheritance(unittest.TestCase):
    """Tests that every concrete type properly extends Animal."""

    def test_subclasses_inherit_from_animal(self):
        """Dog, Cat, and Bird all have Animal as their base class."""
        for cls in (Dog, Cat, Bird):
            self.assertEqual(cls.__bases__, (Animal,))

    def test_instances_are_animals(self):
        """Every concrete instance IS-AN Animal."""
        for instance in (Dog(), Cat(), Bird()):
            self.assertIsInstance(instance, Animal)

    def test_shared_attributes_come_from_base(self):
        """name and age are stored by Animal.__init__, not redefined."""
        for cls in (Dog, Cat, Bird):
            animal = cls("Sam", 2)
            self.assertEqual((animal.name, animal.age), ("Sam", 2))


class TestDog(unittest.TestCase):
    """Tests for the Dog subclass."""

    def test_constructor_adds_breed(self):
        """The constructor stores the inherited fields plus breed."""
        dog = Dog("Charlie", 7, "Golden Retriever")
        self.assertEqual(dog.name, "Charlie")
        self.assertEqual(dog.age, 7)
        self.assertEqual(dog.breed, "Golden Retriever")

    def test_constructor_defaults(self):
        """Calling Dog() with no arguments uses the default values."""
        dog = Dog()
        self.assertEqual((dog.name, dog.age, dog.breed), ("Unknown", 0, "Mixed"))

    def test_str_extends_base_format(self):
        """__str__ composes the inherited format with the breed."""
        dog = Dog("Charlie", 7, "Golden Retriever")
        self.assertEqual(
            str(dog), "Dog: Name: Charlie, Age: 7, Breed: Golden Retriever"
        )


class TestCat(unittest.TestCase):
    """Tests for the Cat subclass."""

    def test_constructor_adds_fur_color(self):
        """The constructor stores the inherited fields plus fur color."""
        cat = Cat("Luna", 5, "Orange Tabby")
        self.assertEqual(cat.name, "Luna")
        self.assertEqual(cat.age, 5)
        self.assertEqual(cat.fur_color, "Orange Tabby")

    def test_constructor_defaults(self):
        """Calling Cat() with no arguments uses the default values."""
        cat = Cat()
        self.assertEqual((cat.name, cat.age, cat.fur_color), ("Unknown", 0, "Tabby"))

    def test_str_extends_base_format(self):
        """__str__ composes the inherited format with the fur color."""
        cat = Cat("Luna", 5, "Orange Tabby")
        self.assertEqual(
            str(cat), "Cat: Name: Luna, Age: 5, Fur Color: Orange Tabby"
        )


class TestBird(unittest.TestCase):
    """Tests for the Bird subclass."""

    def test_constructor_adds_wingspan(self):
        """The constructor stores the inherited fields plus wingspan."""
        bird = Bird("Tweety", 1, 6.5)
        self.assertEqual(bird.name, "Tweety")
        self.assertEqual(bird.age, 1)
        self.assertEqual(bird.wingspan, 6.5)

    def test_constructor_defaults(self):
        """Calling Bird() with no arguments uses the default values."""
        bird = Bird()
        self.assertEqual((bird.name, bird.age, bird.wingspan), ("Unknown", 0, 0.0))

    def test_str_extends_base_format(self):
        """__str__ composes the inherited format with the wingspan."""
        bird = Bird("Tweety", 1, 6.5)
        self.assertEqual(
            str(bird), "Bird: Name: Tweety, Age: 1, Wingspan: 6.5"
        )


if __name__ == "__main__":
    unittest.main()
