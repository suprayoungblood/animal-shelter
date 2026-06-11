"""Unit tests for the Shelter class."""
import unittest

from animals import Bird, Cat, Dog
from shelter import Shelter


class TestShelterConstruction(unittest.TestCase):
    """Tests for the constructor and capacity rule."""

    def test_constructor_sets_capacity(self):
        """The constructor stores the kennel capacity."""
        self.assertEqual(Shelter(5).capacity, 5)

    def test_constructor_starts_with_no_kennels(self):
        """A new shelter has no kennels until animals arrive."""
        self.assertEqual(Shelter(5).kennels, [])

    def test_constructor_rejects_non_positive_capacity(self):
        """Zero or negative capacities raise ValueError."""
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                Shelter(bad)

    def test_constructor_rejects_non_integer_capacity(self):
        """Non-integer capacities raise ValueError."""
        for bad in ("5", 2.5, True, None):
            with self.assertRaises(ValueError):
                Shelter(bad)


class TestShelterIntake(unittest.TestCase):
    """Tests for adding animals and kennel reuse."""

    def test_add_animal_builds_kennel_when_none_empty(self):
        """A kennel is created when an animal arrives and none are empty."""
        shelter = Shelter(3)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        self.assertEqual(len(shelter.kennels), 1)

    def test_add_animal_reuses_empty_kennel(self):
        """An empty kennel is filled before a new kennel is built."""
        shelter = Shelter(3)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        shelter.adopt("Dog", "Avery")
        result = shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        self.assertEqual(result.kennel_number, 1)
        self.assertEqual(len(shelter.kennels), 1)

    def test_add_animal_rejected_at_capacity(self):
        """Once capacity is reached and all kennels are full, intake fails."""
        shelter = Shelter(1)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        with self.assertRaises(ValueError):
            shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))

    def test_add_animal_rejects_invalid_type(self):
        """Objects that are not registered animals raise TypeError."""
        with self.assertRaises(TypeError):
            Shelter(1).add_animal("not an animal")


class TestShelterAdoption(unittest.TestCase):
    """Tests for adoption and the waiting list."""

    def setUp(self):
        """Create a shelter housing one dog and one bird."""
        self.shelter = Shelter(3)
        self.dog = Dog("Charlie", 7, "Golden Retriever")
        self.shelter.add_animal(self.dog)
        self.shelter.add_animal(Bird("Tweety", 1, 6.5))

    def test_adopt_returns_the_animal(self):
        """Adopting an available type returns that animal."""
        self.assertIs(self.shelter.adopt("Dog", "Avery"), self.dog)

    def test_adopt_keeps_the_kennel(self):
        """The kennel stays in the shelter after its animal is adopted."""
        self.shelter.adopt("Dog", "Avery")
        self.assertEqual(len(self.shelter.kennels), 2)
        self.assertTrue(self.shelter.kennels[0].is_empty())

    def test_adopt_is_case_insensitive(self):
        """Type matching uses a lookup table, not exact casing."""
        self.assertIs(self.shelter.adopt("dog", "Avery"), self.dog)

    def test_adopt_missing_type_joins_waiting_list(self):
        """Requesting an absent type waitlists the adopter and returns None."""
        self.assertIsNone(self.shelter.adopt("Cat", "Blake"))
        self.assertEqual(self.shelter.waiting_list["Cat"], ["Blake"])

    def test_waiting_list_preserves_order(self):
        """Adopters queue in first-come, first-served order."""
        self.shelter.adopt("Cat", "Blake")
        self.shelter.adopt("Cat", "Casey")
        self.assertEqual(self.shelter.waiting_list["Cat"], ["Blake", "Casey"])

    def test_adopt_rejects_unknown_type(self):
        """An unregistered animal type raises ValueError."""
        with self.assertRaises(ValueError):
            self.shelter.adopt("Dragon", "Avery")

    def test_adopt_rejects_blank_adopter(self):
        """A blank adopter name raises ValueError."""
        with self.assertRaises(ValueError):
            self.shelter.adopt("Dog", "   ")


class TestWaitingListFulfillment(unittest.TestCase):
    """Tests for arriving animals fulfilling the waiting list."""

    def setUp(self):
        """Create a shelter with one adopter waiting for a Cat."""
        self.shelter = Shelter(2)
        self.shelter.adopt("Cat", "Blake")

    def test_arrival_goes_to_first_waiting_adopter(self):
        """An arriving animal is adopted on arrival by the first waiter."""
        result = self.shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        self.assertEqual(result.adopter, "Blake")
        self.assertIsNone(result.kennel_number)

    def test_fulfilled_arrival_uses_no_kennel(self):
        """An animal adopted on arrival never occupies a kennel."""
        self.shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        self.assertEqual(len(self.shelter.kennels), 0)

    def test_fulfillment_dequeues_in_fifo_order(self):
        """Waiting adopters are served first-come, first-served."""
        self.shelter.adopt("Cat", "Casey")
        first = self.shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        second = self.shelter.add_animal(Cat("Milo", 2, "Gray"))
        self.assertEqual(first.adopter, "Blake")
        self.assertEqual(second.adopter, "Casey")
        self.assertEqual(self.shelter.waiting_list["Cat"], [])

    def test_other_types_still_get_housed(self):
        """A type with no waiters is housed normally."""
        result = self.shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        self.assertEqual(result.kennel_number, 1)
        self.assertIsNone(result.adopter)


class TestAdoptionLog(unittest.TestCase):
    """Tests for the shelter's adoption history."""

    def setUp(self):
        """Create a shelter housing one dog."""
        self.shelter = Shelter(3)
        self.shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))

    def test_kennel_adoption_is_logged(self):
        """Adopting from a kennel appends a record with on_arrival False."""
        self.shelter.adopt("Dog", "Avery")
        record = self.shelter.adoptions[0]
        self.assertEqual(
            (record.animal_type, record.animal_name, record.adopter),
            ("Dog", "Charlie", "Avery"),
        )
        self.assertFalse(record.on_arrival)

    def test_arrival_adoption_is_logged(self):
        """A waitlist-fulfilled intake appends a record with on_arrival True."""
        self.shelter.adopt("Cat", "Blake")
        self.shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        record = self.shelter.adoptions[0]
        self.assertEqual(record.adopter, "Blake")
        self.assertTrue(record.on_arrival)

    def test_waitlisting_is_not_logged(self):
        """Joining the waiting list is not an adoption."""
        self.shelter.adopt("Cat", "Blake")
        self.assertEqual(self.shelter.adoptions, [])

    def test_log_preserves_order(self):
        """Records accumulate in the order the adoptions happened."""
        self.shelter.adopt("Dog", "Avery")
        self.shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        self.shelter.adopt("Cat", "Casey")
        adopters = [record.adopter for record in self.shelter.adoptions]
        self.assertEqual(adopters, ["Avery", "Casey"])


class TestShelterReporting(unittest.TestCase):
    """Tests for occupancy reporting helpers."""

    def test_occupied_count_ignores_empty_kennels(self):
        """occupied_count only counts kennels holding an animal."""
        shelter = Shelter(3)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        shelter.add_animal(Cat("Luna", 5, "Orange Tabby"))
        shelter.adopt("Cat", "Avery")
        self.assertEqual(shelter.occupied_count(), 1)

    def test_str_summarizes_occupancy(self):
        """__str__ reports animals, kennels, and capacity."""
        shelter = Shelter(3)
        shelter.add_animal(Dog("Charlie", 7, "Golden Retriever"))
        self.assertEqual(str(shelter), "Shelter: 1 animals in 1/3 kennels")


if __name__ == "__main__":
    unittest.main()
