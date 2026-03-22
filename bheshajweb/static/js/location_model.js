// static/js/location_modal.js

async function openLocationModal() {
    const modal = document.getElementById("location-modal");
    modal.style.display = "block";
    document.getElementById("place-search-input").focus();
}

function closeLocationModal() {
    document.getElementById("location-modal").style.display = "none";
}

async function searchPlaces() {
    const q = document.getElementById("place-search-input").value.trim();
    if (q.length < 1) return;

    const results = await API.searchPlaces(q);
    const container = document.getElementById("place-results");
    container.innerHTML = results.map(r => `
        <div class="place-item" onclick='selectPlace(${JSON.stringify(r)})'>
            ${r.label}
        </div>
    `).join("");
}

function selectPlace(r) {
    const place = {
        city: r.city,
        state: r.state,
        country: r.country,
        lat: r.lat,
        lon: r.lon,
        standard: r.standard,
        tz: r.tz,
    };
    State.savePlace(place);
    closeLocationModal();
    loadDaily(); // re-fetch
}
