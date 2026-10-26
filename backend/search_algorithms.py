"""Search algorithms for exploring travel states and selecting feasible plans."""

from __future__ import annotations

from collections import deque


def recommended_transport_order(destination, user_request):
    """Respect a requested mode when available; otherwise compare all available modes."""
    preferred = str(user_request.get("transport_preference", "Any")).lower()
    options = list(destination.get("transport_costs", {}).keys())
    if preferred and preferred != "any":
        if preferred in options:
            return [preferred]
    return options


def choose_activities(destination, user_request):
    """Use the destination's activities list and user interests to pick likely matches."""
    user_interests = {str(item).strip().lower() for item in user_request.get("interests", [])}
    selected = []
    for activity in destination.get("activities", []):
        if isinstance(activity, dict):
            name = str(activity.get("name", "")).strip()
            tags = {str(tag).strip().lower() for tag in activity.get("tags", [])}
        else:
            name = str(activity).strip()
            tags = set()

        if not name:
            continue
        if user_interests and (tags & user_interests):
            selected.append(name)
        elif not selected:
            selected.append(name)

    return selected[:3]


def bfs_trip_states(destinations, user_request):
    """Explore destination -> transport -> accommodation -> activities states using BFS.

    This deliberately models a simple state-space search. Each node holds the partial plan
    so we can prune invalid combinations early before ranking.
    """
    queue = deque()
    for destination in destinations:
        queue.append({
            "destination": destination,
            "transport_mode": None,
            "accommodation_type": None,
            "activities": [],
            "path": [destination["id"]],
        })

    explored = set()
    result_states = []

    accommodation_preference = str(user_request.get("accommodation_preference", "standard")).lower()
    accommodation_options = [accommodation_preference]

    while queue:
        current = queue.popleft()
        destination = current["destination"]
        key = (
            destination["id"],
            current["transport_mode"],
            current["accommodation_type"],
            tuple(sorted(current["activities"])),
        )
        if key in explored:
            continue
        explored.add(key)

        if current["transport_mode"] and current["accommodation_type"]:
            if current["activities"]:
                result_states.append(current)
            else:
                for activity_name in choose_activities(destination, user_request):
                    next_state = {
                        **current,
                        "activities": [activity_name],
                        "path": current["path"] + [activity_name],
                    }
                    queue.append(next_state)
            continue

        if not current["transport_mode"]:
            for transport_mode in recommended_transport_order(destination, user_request):
                queue.append({
                    **current,
                    "transport_mode": transport_mode,
                    "path": current["path"] + [transport_mode],
                })
            continue

        if not current["accommodation_type"]:
            for accommodation_type in accommodation_options:
                queue.append({
                    **current,
                    "accommodation_type": accommodation_type,
                    "path": current["path"] + [accommodation_type],
                })
            continue

        for activity_name in choose_activities(destination, user_request):
            next_state = {
                **current,
                "activities": list(current["activities"]) + [activity_name],
                "path": current["path"] + [activity_name],
            }
            queue.append(next_state)

    return result_states
