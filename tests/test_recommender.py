import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from recommender import generate_recommendations, validate_preferences


class RecommendationTests(unittest.TestCase):
    def test_low_budget_nature_trip(self):
        payload = {
            "starting_city": "Delhi",
            "budget": 12000,
            "duration": 3,
            "destination_type": "nature",
            "transport_preference": "train",
            "accommodation_preference": "budget",
            "interests": ["nature", "photography"],
            "traveler_count": 2,
        }
        result = generate_recommendations(payload)
        self.assertEqual(result["status"], "success")
        self.assertTrue(len(result["itineraries"]) >= 1)

    def test_high_budget_luxury_trip(self):
        payload = {
            "starting_city": "Mumbai",
            "budget": 60000,
            "duration": 5,
            "destination_type": "beach",
            "transport_preference": "flight",
            "accommodation_preference": "luxury",
            "interests": ["beach", "relaxation"],
            "traveler_count": 2,
        }
        result = generate_recommendations(payload)
        self.assertEqual(result["status"], "success")
        self.assertTrue(len(result["itineraries"]) >= 1)

    def test_beach_trip_with_bus_preference(self):
        payload = {
            "starting_city": "Pune",
            "budget": 25000,
            "duration": 4,
            "destination_type": "beach",
            "transport_preference": "bus",
            "accommodation_preference": "standard",
            "interests": ["beach", "food"],
            "traveler_count": 2,
        }
        result = generate_recommendations(payload)
        self.assertEqual(result["status"], "success")
        self.assertTrue(any(item["name"] == "Goa" for item in result["itineraries"]))
        self.assertTrue(all(item["transport_mode"] == "bus" for item in result["itineraries"]))
        self.assertEqual(len({item["destination_id"] for item in result["itineraries"]}), len(result["itineraries"]))

    def test_recommendations_are_unique_and_honor_accommodation(self):
        payload = {
            "starting_city": "Mumbai",
            "budget": 80000,
            "duration": 4,
            "destination_type": "any",
            "transport_preference": "any",
            "accommodation_preference": "luxury",
            "interests": [],
            "traveler_count": 2,
        }
        result = generate_recommendations(payload)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len({item["destination_id"] for item in result["itineraries"]}), len(result["itineraries"]))
        self.assertTrue(all(item["accommodation_type"] == "luxury" for item in result["itineraries"]))

    def test_cultural_trip_for_short_duration(self):
        payload = {
            "starting_city": "Lucknow",
            "budget": 18000,
            "duration": 2,
            "destination_type": "historical",
            "transport_preference": "train",
            "accommodation_preference": "standard",
            "interests": ["culture", "history"],
            "traveler_count": 1,
        }
        result = generate_recommendations(payload)
        self.assertEqual(result["status"], "success")
        self.assertTrue(len(result["itineraries"]) >= 1)

    def test_interest_based_trip(self):
        payload = {
            "starting_city": "Delhi",
            "budget": 30000,
            "duration": 3,
            "destination_type": "any",
            "transport_preference": "any",
            "accommodation_preference": "standard",
            "interests": ["wildlife"],
            "traveler_count": 2,
        }
        result = generate_recommendations(payload)
        self.assertEqual(result["status"], "success")
        self.assertTrue(any(item["category"] == "wildlife" for item in result["itineraries"]))

    def test_impossible_budget(self):
        payload = {
            "starting_city": "Hyderabad",
            "budget": 3000,
            "duration": 2,
            "destination_type": "nature",
            "transport_preference": "flight",
            "accommodation_preference": "budget",
            "interests": ["nature"],
            "traveler_count": 1,
        }
        result = generate_recommendations(payload)
        self.assertEqual(result["status"], "no_results")

    def test_invalid_or_missing_input(self):
        with self.assertRaises(ValueError):
            validate_preferences({"budget": 1000})

    def test_multiple_travelers(self):
        payload = {
            "starting_city": "Bengaluru",
            "budget": 45000,
            "duration": 5,
            "destination_type": "any",
            "transport_preference": "train",
            "accommodation_preference": "standard",
            "interests": ["nature"],
            "traveler_count": 4,
        }
        result = generate_recommendations(payload)
        self.assertEqual(result["status"], "success")
        self.assertTrue(len(result["itineraries"]) >= 1)


if __name__ == "__main__":
    unittest.main()
