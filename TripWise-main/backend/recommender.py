"""Main logic for validating input and generating ranked trip recommendations."""

from __future__ import annotations

from knowledge_base import load_destinations
from rules import build_explanation, compute_itinerary_score, normalize_interests
from search_algorithms import bfs_trip_states


def validate_preferences(payload):
    """Validate and normalize incoming travel preferences."""
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    required_fields = ["starting_city", "budget", "duration", "destination_type", "transport_preference", "accommodation_preference", "traveler_count"]
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    starting_city = str(payload.get("starting_city", "")).strip()
    if not starting_city:
        raise ValueError("Starting city is required.")

    try:
        budget = float(payload.get("budget"))
        duration = int(payload.get("duration"))
        traveler_count = int(payload.get("traveler_count"))
    except (TypeError, ValueError):
        raise ValueError("Budget, duration, and traveler count must be numeric values.")

    if budget <= 0:
        raise ValueError("Budget must be greater than zero.")
    if duration <= 0:
        raise ValueError("Trip duration must be at least 1 day.")
    if traveler_count <= 0:
        raise ValueError("Traveler count must be at least 1.")

    interests = normalize_interests(payload.get("interests", []))
    normalized = {
        "starting_city": starting_city,
        "budget": budget,
        "duration": duration,
        "destination_type": str(payload.get("destination_type", "Any")).strip() or "Any",
        "transport_preference": str(payload.get("transport_preference", "Any")).strip() or "Any",
        "accommodation_preference": str(payload.get("accommodation_preference", "Standard")).strip() or "Standard",
        "traveler_count": traveler_count,
        "interests": interests,
    }
    return normalized


def _match_destination_filters(destination, user_request):
    """Apply hard constraints before ranking destinations."""
    preferred_category = str(user_request.get("destination_type", "Any")).lower()
    destination_category = str(destination.get("category", "")).lower()

    if preferred_category not in ["any", "all"] and preferred_category != destination_category:
        return False

    duration = int(user_request.get("duration", 3))
    recommended_duration = int(destination.get("recommended_trip_duration", 3))
    if duration > recommended_duration + 4:
        return False

    user_interest_tags = normalize_interests(user_request.get("interests", []))
    destination_tags = {str(tag).strip().lower() for tag in destination.get("tags", [])}
    if user_interest_tags and not any(tag in destination_tags for tag in user_interest_tags):
        # This rule remains strict for explicit category pins, but for general interest matching we allow
        # broader exploration so that the recommendation engine still produces useful alternatives.
        if preferred_category in ["any", "all"]:
            return True
        return False

    return True


def _pick_activities(destination, activity_names):
    """Return activity dictionaries matching the selected names."""
    available = destination.get("activities", [])
    selected = []
    for entry in available:
        if isinstance(entry, dict):
            name = str(entry.get("name", ""))
        else:
            name = str(entry)
        if name in activity_names:
            selected.append(entry)
    return selected


def calculate_trip_cost(destination, transport_mode, accommodation_type, activity_names, trip_duration, traveler_count):
    """Estimate trip total using shared-room assumptions for accommodation and a traveler-aware
    scaling factor for transport, food, and local transfers. This keeps the model realistic for
    couples and families without double-counting hotel rooms.
    """
    travel_group_size = max(1, round(traveler_count / 2))

    transport_costs = destination.get("transport_costs", {})
    chosen_transport = transport_costs.get(str(transport_mode).lower(), 0)
    transport_cost = chosen_transport * travel_group_size

    accommodation_costs = destination.get("accommodation_costs", {})
    nightly_rate = accommodation_costs.get(str(accommodation_type).lower(), accommodation_costs.get("standard", 0))
    accommodation_cost = nightly_rate * trip_duration

    food_cost = float(destination.get("food_per_day", 0)) * trip_duration * travel_group_size
    local_transport = float(destination.get("local_transport_allowance", 0)) * travel_group_size

    selected_activities = _pick_activities(destination, activity_names)
    activity_cost = 0
    for item in selected_activities:
        if isinstance(item, dict):
            activity_cost += float(item.get("cost", 0))
    
    total_cost = transport_cost + accommodation_cost + food_cost + local_transport + activity_cost
    return {
        "transport_cost": round(transport_cost, 2),
        "accommodation_cost": round(accommodation_cost, 2),
        "food_cost": round(food_cost, 2),
        "local_transport_cost": round(local_transport, 2),
        "activity_cost": round(activity_cost, 2),
        "total_cost": round(total_cost, 2),
    }


def generate_recommendations(payload):
    """Create top-ranked feasible itineraries for the given user preference set."""
    user_request = validate_preferences(payload)
    destinations = load_destinations()
    filtered_destinations = [destination for destination in destinations if _match_destination_filters(destination, user_request)]

    if not filtered_destinations:
        return {
            "status": "no_results",
            "message": "No destinations satisfy your criteria. Try relaxing the budget, broadening the category, or increasing the trip duration.",
            "itineraries": [],
        }

    candidate_states = bfs_trip_states(filtered_destinations, user_request)
    ranked_results = []

    for state in candidate_states:
        destination = state["destination"]
        transport_mode = state["transport_mode"] or user_request.get("transport_preference", "train")
        accommodation_type = state["accommodation_type"] or user_request.get("accommodation_preference", "standard")
        activity_names = state["activities"] or []

        cost_breakdown = calculate_trip_cost(
            destination,
            transport_mode,
            accommodation_type,
            activity_names,
            user_request["duration"],
            user_request["traveler_count"],
        )
        if cost_breakdown["total_cost"] > user_request["budget"]:
            continue

        score = compute_itinerary_score(
            destination,
            user_request,
            cost_breakdown["total_cost"],
            transport_mode,
            accommodation_type,
        )

        ranked_results.append({
            "destination_id": destination["id"],
            "name": destination["name"],
            "state": destination["state"],
            "category": destination["category"],
            "description": destination["description"],
            "best_season": destination.get("best_season", "Flexible"),
            "duration": destination.get("recommended_trip_duration", user_request["duration"]),
            "transport_mode": transport_mode,
            "accommodation_type": accommodation_type,
            "activities": activity_names,
            "estimated_cost": cost_breakdown,
            "score": score,
            "explanation": build_explanation(destination, user_request, transport_mode, accommodation_type, activity_names, cost_breakdown["total_cost"]),
            "recommended_for": destination.get("interests", [])[:3],
        })

    if not ranked_results:
        return {
            "status": "no_results",
            "message": "Your budget or constraints eliminate every feasible destination. Consider raising the budget or selecting a different destination type.",
            "itineraries": [],
        }

    ranked_results = sorted(
        ranked_results,
        key=lambda item: (
            item["score"],
            -item["estimated_cost"]["total_cost"],
        ),
        reverse=True,
    )
    best_by_destination = {}
    for result in ranked_results:
        best_by_destination.setdefault(result["destination_id"], result)
    top_results = list(best_by_destination.values())[:5]
    for result in top_results:
        result["remaining_budget"] = round(user_request["budget"] - result["estimated_cost"]["total_cost"], 2)

    return {
        "status": "success",
        "message": f"Found {len(top_results)} strong trip matches for your preferences.",
        "itineraries": top_results,
        "search_summary": {
            "destinations_considered": len(filtered_destinations),
            "candidate_states": len(candidate_states),
            "weights": {
                "interest_match": 0.40,
                "category_match": 0.20,
                "budget_fit": 0.15,
                "duration_suitability": 0.15,
                "transport_preference": 0.10,
            },
        },
    }
