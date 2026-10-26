const apiBaseUrl = "http://127.0.0.1:5000";

const form = document.getElementById("trip-form");
const messageBox = document.getElementById("message");
const recommendationsContainer = document.getElementById("recommendations");
const emptyState = document.getElementById("empty-state");
const summaryBadge = document.getElementById("summary-badge");
const tripSummary = document.getElementById("trip-summary");
const resetButton = document.getElementById("reset-button");
const submitButton = document.getElementById("submit-button");
const spinner = submitButton.querySelector(".spinner");
const buttonText = submitButton.querySelector(".button-text");
const destinationImages = {
  "leh-ladakh": "photo-1501785888041-af3ef285b470",
  goa: "photo-1507525428034-b723cf961d3e",
  jaipur: "photo-1605640840606-3ad7b7194ce8",
  varanasi: "photo-1561361513-2d000a50f0dc",
  rishikesh: "photo-1500530855697-b586d89ba3ee",
  ooty: "photo-1448375240586-882707db888b",
  "jim-corbett": "photo-1472396961693-142e6e269027",
  ranthambore: "photo-1549366021-9f761d450615",
  udaipur: "photo-1533105079780-92b9be482077",
  hampi: "photo-1518709268805-4e9042af9f23",
  pahalgam: "photo-1464822759023-fed622ff2c3b",
  munnar: "photo-1441974231531-c6227db76b6e",
  khajuraho: "photo-1564507592333-c60657eea523",
  "bodh-gaya": "photo-1605649487212-47bdab064df7",
  shimla: "photo-1500534623283-312aade485b7",
  "kerala-backwaters": "photo-1518509562904-e7ef99cdcc86",
  agra: "photo-1548013146-72479768bada",
};

function setMessage(text, type = "success") {
  messageBox.textContent = text;
  messageBox.className = `message ${type}`;
}

function showLoading(isLoading) {
  if (isLoading) {
    spinner.classList.remove("hidden");
    buttonText.textContent = "Searching...";
    submitButton.disabled = true;
  } else {
    spinner.classList.add("hidden");
    buttonText.textContent = "Find My Perfect Trip";
    submitButton.disabled = false;
  }
}

function getSelectedInterests() {
  return [...document.querySelectorAll("input[type='checkbox']:checked")].map((item) => item.value);
}

function updateSummary(itineraries) {
  if (!itineraries || itineraries.length === 0) {
    tripSummary.innerHTML = "<p>Complete your trip details to see a full budget summary and recommendation breakdown.</p>";
    return;
  }

  const top = itineraries[0];
  const total = top.estimated_cost.total_cost;
  const remaining = top.remaining_budget;

  tripSummary.innerHTML = `
    <div class="summary-item">
      <small>Top destination</small>
      <strong>${top.name}</strong>
    </div>
    <div class="summary-item">
      <small>Estimated total</small>
      <strong>₹${Number(total).toLocaleString('en-IN')}</strong>
    </div>
    <div class="summary-item">
      <small>Remaining budget</small>
      <strong>₹${Number(remaining).toLocaleString('en-IN')}</strong>
    </div>
    <div class="summary-item">
      <small>Suggested transport</small>
      <strong>${top.transport_mode}</strong>
    </div>
  `;
}

function createTripCard(itinerary) {
  const imageId = destinationImages[itinerary.destination_id];
  const imageUrl = imageId
    ? `https://images.unsplash.com/${imageId}?auto=format&fit=crop&w=900&q=80`
    : "";

  const budget = itinerary.estimated_cost;
  return `
    <article class="trip-card">
      <img src="${imageUrl}" alt="${itinerary.name} destination" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80';" />
      <div class="trip-body">
        <div class="trip-header">
          <h4>${itinerary.name}</h4>
          <span class="score-pill">Score ${itinerary.score}</span>
        </div>

        <div class="meta-row">
          <span class="meta-badge">${itinerary.category}</span>
          <span class="meta-badge">${itinerary.state}</span>
          <span class="meta-badge">${itinerary.duration} days</span>
        </div>

        <p>${itinerary.description}</p>

        <div class="budget-block">
          <span class="subtle">Estimated total</span>
          <strong>₹${Number(budget.total_cost).toLocaleString('en-IN')}</strong>
          <div class="subtle">Remaining: ₹${Number(itinerary.remaining_budget).toLocaleString('en-IN')}</div>
        </div>

        <ul class="points-list">
          <li>Transport: ${itinerary.transport_mode}</li>
          <li>Stay: ${itinerary.accommodation_type}</li>
          <li>Budget: ${itinerary.estimated_cost.transport_cost ? '₹'+Number(itinerary.estimated_cost.transport_cost).toLocaleString('en-IN') : 'N/A'}</li>
        </ul>

        <ul class="activity-list">
          ${(itinerary.activities || []).map((activity) => `<li>${activity}</li>`).join('') || '<li>Local experiences</li>'}
        </ul>

        <div class="reason-box">
          ${itinerary.explanation}
        </div>
      </div>
    </article>
  `;
}

function renderRecommendations(itineraries) {
  recommendationsContainer.innerHTML = itineraries.map(createTripCard).join("");
  emptyState.classList.toggle("hidden", itineraries.length > 0);
  summaryBadge.textContent = itineraries.length ? `${itineraries.length} matches` : "No matches";
  updateSummary(itineraries);
}

async function loadDestinations() {
  try {
    const response = await fetch(`${apiBaseUrl}/api/destinations`);
    if (!response.ok) {
      return;
    }
    const data = await response.json();
    summaryBadge.textContent = `${data.count} destinations available`;
  } catch (error) {
    summaryBadge.textContent = "Offline";
  }
}

resetButton.addEventListener("click", () => {
  form.reset();
  document.getElementById("budget").value = "30000";
  document.getElementById("duration").value = "5";
  document.getElementById("traveler-count").value = "2";
  document.getElementById("destination-type").value = "any";
  document.getElementById("transport-preference").value = "any";
  document.getElementById("accommodation-preference").value = "standard";
  recommendationsContainer.innerHTML = "";
  emptyState.classList.remove("hidden");
  tripSummary.innerHTML = "<p>Complete your trip details to see a full budget summary and recommendation breakdown.</p>";
  setMessage("Planner reset. Ready for a new trip idea.", "success");
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showLoading(true);
  setMessage("", "success");

  const payload = {
    starting_city: document.getElementById("starting-city").value.trim(),
    budget: Number(document.getElementById("budget").value),
    duration: Number(document.getElementById("duration").value),
    destination_type: document.getElementById("destination-type").value,
    transport_preference: document.getElementById("transport-preference").value,
    accommodation_preference: document.getElementById("accommodation-preference").value,
    interests: getSelectedInterests(),
    traveler_count: Number(document.getElementById("traveler-count").value),
  };

  try {
    const response = await fetch(`${apiBaseUrl}/api/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to generate recommendations.");
    }

    if (!data.itineraries || data.itineraries.length === 0) {
      renderRecommendations([]);
      setMessage(data.message || "No itinerary matches your current inputs.", "error");
      return;
    }

    renderRecommendations(data.itineraries);
    setMessage(data.message || "Here are your travel recommendations.", "success");
  } catch (error) {
    renderRecommendations([]);
    setMessage(error.message || "The server is unavailable. Please check the backend and try again.", "error");
  } finally {
    showLoading(false);
  }
});

window.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  emptyState.classList.remove("hidden");
  loadDestinations();
});
