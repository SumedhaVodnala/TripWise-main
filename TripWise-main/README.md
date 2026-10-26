# TripWise: Intelligent Travel Planning Bot

TripWise is a beginner-friendly web application that helps travelers plan personalized trips using a rule-based recommendation engine, constraint filtering, and lightweight search techniques. The system suggests destinations, transport options, accommodation styles, and activities based on a traveler's budget, trip length, interests, and preferred travel style.

## Problem Statement
A traveler often has to compare many destinations, modes of transport, prices, and activity options manually. The goal of TripWise is to reduce that burden by automatically narrowing feasible options and ranking the best matches based on real constraints such as budget, duration, interest alignment, and destination category.

## Project Objectives
- Recommend destinations using user constraints
- Estimate total trip cost for each itinerary
- Filter impossible options early
- Rank the best itinerary alternatives using a heuristic score
- Explain recommendations in plain language
- Keep the logic readable and easy to extend for beginners

## System Architecture
The app uses a simple three-layer design:

1. Frontend: HTML, CSS, and JavaScript for the user experience
2. Backend: Python + Flask REST API for validation and recommendation logic
3. Knowledge base: JSON dataset of Indian destinations and their attributes

## Knowledge Representation
Travel knowledge is stored in structured JSON objects such as:

- destination name
- category
- state/region
- activities
- transport costs
- accommodation costs
- food expenses
- travel tags/interests
- approximate travel information

This representation makes it easy to add or edit destinations without changing the algorithm logic.

## Search Techniques
The backend uses several understandable search and reasoning methods:

- Constraint-based filtering: destinations that fail budget, category, or duration rules are rejected early
- Breadth-First Search (BFS): partial trip states are explored in a defined order such as destination -> transport -> accommodation -> activities
- Heuristic scoring: each itinerary is ranked using weighted factors like interest match, category fit, budget fit, duration suitability, and transport preference
- Sorting: valid plans are sorted by score so the strongest itinerary appears first

## BFS State Exploration
The BFS state space is modeled in this order:

Destination selected -> Transport selected -> Accommodation selected -> Activities chosen

This allows the engine to avoid exploring unnecessary combinations and maintain a clear, traceable recommendation process.

## Heuristic Scoring
Each itinerary is scored using a weighted formula. The demo weights are:

- Interest match: 0.40
- Category match: 0.20
- Budget fit: 0.15
- Duration suitability: 0.15
- Transport preference: 0.10

The system ranks higher-scoring plans first, rather than simply selecting the cheapest destination.

## Constraint-Based Pruning
Hard constraints are enforced before ranking:

- destination category must match the user request when specified
- trip duration must be within a reasonable range
- user budget must be large enough for the itinerary
- if no feasible result exists, the system returns an informative message

## Rule-Based Reasoning
The reasoning engine applies explicit rules such as:

- IF the destination category matches the user's preference, increase its score
- IF the user's interest tags overlap with destination tags, increase the interest score
- IF the total cost exceeds the budget, reject the itinerary
- IF the transport mode matches the user's preference, consider it more relevant
- IF the user requests a luxury hotel, use luxury accommodation costs

These rules live in a separate maintainable module rather than being embedded directly in the UI.

## Recommendation Workflow
The user enters:

- starting city
- budget
- duration
- destination type
- transport preference
- accommodation preference
- interests
- traveler count

The system then:

1. Validates the input
2. Loads the JSON destination knowledge base
3. Filters destinations by constraints
4. Builds feasible transport and accommodation combinations
5. Estimates itinerary costs
6. Rejects options over budget
7. Scores and ranks the remaining options
8. Returns the top results with explanations

## Example Input
Example user request:

- Starting city: Delhi
- Budget: INR 30,000
- Duration: 5 days
- Preferred destination type: nature
- Transport preference: train
- Accommodation: standard
- Interests: nature, photography
- Travelers: 2

The engine may recommend a destination like Ooty or Shimla if it matches the category, budget, and interests. It then chooses a train-based itinerary, calculates cost, and explains why that result ranked highest.

## Limitations
- The data is illustrative and not live pricing data
- Destination distances and travel estimates are sample-based
- Recommendations are reasoned using a small knowledge base rather than full-scale optimization
- Some user inputs may still require manual adjustment for more specialized travel goals

## Future Enhancements
- Add real map and route APIs
- Support dynamic hotel and airline pricing
- Add user login and saved itineraries
- Expand destination data to all states and territories
- Add explainable recommendation charts and interactive filters

## Project Structure

TripWise/
- frontend/
  - index.html
  - style.css
  - script.js
- backend/
  - __init__.py
  - app.py
  - recommender.py
  - search_algorithms.py
  - knowledge_base.py
  - rules.py
- data/
  - destinations.json
- tests/
  - test_recommender.py
- requirements.txt
- README.md
- .gitignore

## How to Run on Windows

### 1. Open the project in VS Code
Open the folder:

C:\Users\Ramya Sri\Downloads\halo-fall-aware-home-simulator\TripWise

### 2. Open the VS Code terminal
Use Terminal -> New Terminal in VS Code.

### 3. Create a Python virtual environment
```powershell
cd "C:\Users\Ramya Sri\Downloads\halo-fall-aware-home-simulator\TripWise"
python -m venv .venv
```

### 4. Activate the environment
```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 5. Install project dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 6. Start the Flask backend
From the project root:
```powershell
cd "C:\Users\Ramya Sri\Downloads\halo-fall-aware-home-simulator\TripWise"
.\.venv\Scripts\python.exe .\backend\app.py
```

The backend runs on:
```text
http://127.0.0.1:5000
```

### 7. Open the frontend
Use VS Code Live Server or any local static server:

Option A: VS Code Live Server
- Open the `frontend` folder
- Right-click `index.html`
- Choose "Open with Live Server"

Option B: local static server from the terminal
```powershell
cd "C:\Users\Ramya Sri\Downloads\halo-fall-aware-home-simulator\TripWise\frontend"
python -m http.server 8000
```
Then open:
```text
http://127.0.0.1:8000
```

## Test the API Endpoints
Use the browser or a tool such as curl in PowerShell:

### Health check
```powershell
curl http://127.0.0.1:5000/api/health
```

### List destinations
```powershell
curl http://127.0.0.1:5000/api/destinations
```

### Example recommendation request
```powershell
curl -X POST http://127.0.0.1:5000/api/recommend -H "Content-Type: application/json" -d "{\"starting_city\":\"Delhi\",\"budget\":30000,\"duration\":5,\"destination_type\":\"nature\",\"transport_preference\":\"train\",\"accommodation_preference\":\"standard\",\"interests\":[\"nature\",\"photography\"],\"traveler_count\":2}"
```

## Troubleshooting

### Python not recognized
If `python` or `py` is not found:
```powershell
py --version
```
If Python is installed but not on PATH, install it again and make sure the Add Python to PATH option is enabled.

### Wrong working directory
Always run commands from the TripWise folder. Check the current folder with:
```powershell
Get-Location
```

### Package installation issues
If a dependency fails to install:
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Port already in use
If port 5000 is already in use, stop the current Flask process or change the port in `backend/app.py`.

### Frontend cannot fetch the backend
Make sure the backend is still running and the frontend code is calling:
```javascript
http://127.0.0.1:5000
```

## Testing and Reliability
The project includes an automated test suite for recommendation logic. To run tests:

```powershell
cd "C:\Users\Ramya Sri\Downloads\halo-fall-aware-home-simulator\TripWise"
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
```

The test suite checks:
- low-budget trip logic
- luxury trip logic
- beach trip logic
- short cultural stay logic
- interest-based trip matching
- impossible budget handling
- invalid input rejection
- multi-traveler planning

## Final Notes
TripWise is intentionally designed to be simple, readable, and beginner-friendly while still demonstrating real AI-style planning behavior using rule-based reasoning, search, filtering, and scoring.

The project is educational in nature and uses illustrative sample costs, not live travel pricing.
