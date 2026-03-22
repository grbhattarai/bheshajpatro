// static/js/api.js

async function fetchJSON(url) {
  try {
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.error("API error:", err);
    throw err;
  }
}

const API = {
  async fetchDaily({ date, place, engine }) {
    const params = new URLSearchParams({
      date_ce: date,
      city: place.city,
      state: place.state ?? "",
      country: place.country,
      lat: place.lat,
      lon: place.lon,
      standard: place.standard,
      tz: place.tz,
      engine: engine,
    });

    const url = `/panchanga/daily?${params.toString()}`;
    return fetchJSON(url);
  },

  async fetchMonth({ year, month, place, engine }) {
    const params = new URLSearchParams({
      year,
      month,
      city: place.city,
      state: place.state ?? "",
      country: place.country,
      lat: place.lat,
      lon: place.lon,
      standard: place.standard,
      tz: place.tz,
      engine,
    });

    const url = `/panchanga/month?${params.toString()}`;
    return fetchJSON(url);
  },

  async searchPlaces(query) {
    const url = `/panchanga/places?q=${encodeURIComponent(query)}`;
    return fetchJSON(url);
  },
};
