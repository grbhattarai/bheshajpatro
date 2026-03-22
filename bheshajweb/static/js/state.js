// static/js/state.js

const STATE_KEY = "bheshaj_panchanga_state_v1";

const DEFAULT_PLACE = {
  city: "Raleigh",
  state: "NC",
  country: "USA",
  lat: 35.78774,
  lon: -78.64426,
  standard: -75.0,
  tz: "America/New_York",
};

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear().toString().padStart(4, "0");
  const mm = (d.getMonth() + 1).toString().padStart(2, "0");
  const dd = d.getDate().toString().padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

const State = {
  load() {
    try {
      const raw = localStorage.getItem(STATE_KEY);
      if (!raw) {
        return {
          date: todayISO(),
          place: { ...DEFAULT_PLACE },
        };
      }
      const parsed = JSON.parse(raw);
      if (!parsed.date) parsed.date = todayISO();
      if (!parsed.place) parsed.place = { ...DEFAULT_PLACE };
      return parsed;
    } catch (e) {
      console.warn("State.load error:", e);
      return {
        date: todayISO(),
        place: { ...DEFAULT_PLACE },
      };
    }
  },

  save(state) {
    try {
      localStorage.setItem(STATE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn("State.save error:", e);
    }
  },

  saveDate(dateStr) {
    const s = this.load();
    s.date = dateStr;
    this.save(s);
  },

  savePlace(place) {
    const s = this.load();
    s.place = place;
    this.save(s);
  },
};
