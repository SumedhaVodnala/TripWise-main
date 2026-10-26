from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from backend.knowledge_base import get_destination_by_id, load_destinations
    from backend.recommender import generate_recommendations
except ImportError:
    from knowledge_base import get_destination_by_id, load_destinations
    from recommender import generate_recommendations

app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok", "message": "TripWise API is running."})


@app.get("/api/destinations")
def list_destinations():
    destinations = load_destinations()
    return jsonify({"count": len(destinations), "destinations": destinations})


@app.get("/api/destination/<destination_id>")
def get_destination(destination_id):
    destination = get_destination_by_id(destination_id)
    if not destination:
        return jsonify({"error": "Destination not found."}), 404
    return jsonify(destination)


@app.post("/api/recommend")
def recommend_trips():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        result = generate_recommendations(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - defensive fallback
        return jsonify({"error": f"Recommendation engine failed: {exc}"}), 500

    if result.get("status") == "success":
        return jsonify(result)
    return jsonify(result), 404


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
