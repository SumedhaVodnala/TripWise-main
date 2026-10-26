from __future__ import annotations

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "destinations.json"


def load_destinations():
    """Load all destinations from the JSON knowledge base."""
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_destination_by_id(destination_id):
    """Return a single destination object by unique id."""
    for destination in load_destinations():
        if destination["id"] == destination_id:
            return destination
    return None
