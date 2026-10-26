"""Rule-based reasoning used to score and explain trip recommendations."""

from __future__ import annotations

DEFAULT_WEIGHTS = {
    "interest_match": 0.40,
    "category_match": 0.20,
    "budget_fit": 0.15,
    "duration_suitability": 0.15,
    "transport_preference": 0.10,
}


def normalize_interests(value):
    """Convert user input into a set of lower-case interest tags."""
    if value is None:
        return []
    if isinstance(value, str):
        values = [part.strip() for part in value.split(",")]
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        values = [str(value)]

    normalized = []
    for item in values:
        cleaned = str(item).strip().lower()
        if cleaned:
            normalized.append(cleaned)
    return normalized


def category_match_score(destination_category, preferred_category):
    """IF the destination category matches the user's preference, raise the score."""
    if not preferred_category or preferred_category.lower() == "any":
        return 0.75
    if not destination_category:
        return 0.2
    return 1.0 if destination_category.lower() == preferred_category.lower() else 0.25


def interest_match_score(destination, user_interests):
    """Count overlaps between user interests and destination tags."""
    destination_tags = {str(tag).strip().lower() for tag in destination.get("tags", [])}
    user_interests = {str(tag).strip().lower() for tag in normalize_interests(user_interests)}
    if not user_interests:
        return 0.6
    overlap = len(destination_tags & user_interests)
    return min(1.0, overlap / max(1, len(user_interests)))


def budget_fit_score(total_cost, budget):
    """Reward itineraries that stay within budget and penalize over-budget cases."""
    if budget is None or budget <= 0:
        return 0.1
    if total_cost <= budget:
        slack_ratio = 1 - (total_cost / max(1, budget))
        return max(0.4, 0.9 + slack_ratio * 0.2)
    excess_ratio = (total_cost - budget) / max(1, budget)
    return max(0.0, 1.0 - excess_ratio)


def duration_suitability_score(destination, trip_duration):
    """Reject or penalize destinations whose ideal duration differs too much from the request."""
    ideal_duration = destination.get("recommended_trip_duration", 3)
    delta = abs(int(trip_duration) - int(ideal_duration))
    if delta == 0:
        return 1.0
    return max(0.2, 1.0 - (delta / max(3, ideal_duration + 1)))


def transport_preference_score(user_transport, transport_mode):
    """Respect the user's transport preference when feasible."""
    if not user_transport or str(user_transport).lower() == "any":
        return 0.8
    if str(transport_mode).lower() == str(user_transport).lower():
        return 1.0
    return 0.45


def compute_itinerary_score(destination, user_request, total_cost, transport_mode, accommodation_type):
    """Combine scoring components into a final ranking weight."""
    interest_score = interest_match_score(destination, user_request.get("interests", []))
    category_score = category_match_score(destination.get("category"), user_request.get("destination_type"))
    budget_score = budget_fit_score(total_cost, user_request.get("budget"))
    duration_score = duration_suitability_score(destination, user_request.get("duration", 3))
    transport_score = transport_preference_score(user_request.get("transport_preference"), transport_mode)

    total = (
        interest_score * DEFAULT_WEIGHTS["interest_match"]
        + category_score * DEFAULT_WEIGHTS["category_match"]
        + budget_score * DEFAULT_WEIGHTS["budget_fit"]
        + duration_score * DEFAULT_WEIGHTS["duration_suitability"]
        + transport_score * DEFAULT_WEIGHTS["transport_preference"]
    )
    return round(total, 4)


def build_explanation(destination, user_request, transport_mode, accommodation_type, activities, total_cost):
    """Return a readable explanation for each recommendation."""
    reasons = []
    preferred_category = user_request.get("destination_type")
    if preferred_category and preferred_category.lower() != "any":
        if destination.get("category", "").lower() == preferred_category.lower():
            reasons.append(f"It matches your preferred {preferred_category} itinerary.")
        else:
            reasons.append(f"It is a strong alternative within a nearby travel style.")

    matching_interests = [tag for tag in normalize_interests(user_request.get("interests", [])) if tag in {str(item).lower() for item in destination.get("tags", [])}]
    if matching_interests:
        reasons.append(f"It aligns with your interests in {', '.join(matching_interests[:2])}.")
    else:
        reasons.append("It offers a balanced mix of scenery, local culture, and relaxation.")

    if total_cost <= user_request.get("budget", float("inf")):
        reasons.append(f"The itinerary stays within your budget of INR {user_request.get('budget', 0):,}.")
    else:
        reasons.append("This option is close to your budget and still feasible with minor adjustments.")

    if transport_mode:
        reasons.append(f"Transport is set to {transport_mode.title()} to match your travel preference.")

    if accommodation_type:
        reasons.append(f"Accommodation uses a {accommodation_type.title()} plan with comfortable daily cost assumptions.")

    if activities:
        reasons.append(f"Suggested activities include {', '.join(activities[:3])}.")

    return " ".join(reasons)
