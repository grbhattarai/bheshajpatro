# bheshaj_web/static/js/daily.js

// ---------- Simple localStorage state -------------------------

const STORAGE_KEY = "bheshaj-panchanga-state-v2";

const DEFAULT_PLACE = {
  city: "Raleigh",
  state: "NC",
  country: "USA",
  lat: 35.78774,
  lon: -78.64426,
  standard: -75.0,
  tz: "America/New_York",
};

const DEFAULT_METHOD =
  typeof INITIAL_ENGINE !== "undefined" && INITIAL_ENGINE
    ? INITIAL_ENGINE
    : "ketaki";

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear().toString().padStart(4, "0");
  const mm = (d.getMonth() + 1).toString().padStart(2, "0");
  const dd = d.getDate().toString().padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return { date: todayISO(), place: DEFAULT_PLACE, method: DEFAULT_METHOD };
    }
    const parsed = JSON.parse(raw);
    return {
      date: parsed.date || todayISO(),
      place: parsed.place || DEFAULT_PLACE,
      method: parsed.method || DEFAULT_METHOD,
    };
  } catch (_) {
    return { date: todayISO(), place: DEFAULT_PLACE, method: DEFAULT_METHOD };
  }
}

function saveState(partial) {
  const cur = loadState();
  const next = { ...cur, ...partial };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
}

function isoToDate(iso) {
  const [y, m, d] = iso.split("-").map((x) => parseInt(x, 10));
  return new Date(y, m - 1, d);
}

function dateToISO(d) {
  const yyyy = d.getFullYear().toString().padStart(4, "0");
  const mm = (d.getMonth() + 1).toString().padStart(2, "0");
  const dd = d.getDate().toString().padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

// clamp year to [2020, 2030]
function clampDateToRange(d) {
  let year = d.getFullYear();
  if (year < 2020) {
    d.setFullYear(2020);
  } else if (year > 2030) {
    d.setFullYear(2030);
  }
  return d;
}

// ---------- Small helpers -------------------------------------

function prettyCode(label) {
  if (!label) return "";
  const trimmed = String(label).trim();
  if (trimmed.length <= 3) {
    return trimmed.toUpperCase();
  }
  return trimmed;
}

// English names for rashis (1..12)
const RASHI_EN = {
  1: "Aries",
  2: "Taurus",
  3: "Gemini",
  4: "Cancer",
  5: "Leo",
  6: "Virgo",
  7: "Libra",
  8: "Scorpio",
  9: "Sagittarius",
  10: "Capricorn",
  11: "Aquarius",
  12: "Pisces",
};

// Convert "HH:MM" (HH may be >= 24) into a display string.
function normalizeTimeWithNextDay(hm) {
  if (!hm || typeof hm !== "string") return hm;

  const trimmed = hm.trim();
  if (!trimmed) return trimmed;

  const parts = trimmed.split(":");
  if (parts.length !== 2) return trimmed;

  const hRaw = parseInt(parts[0], 10);
  const mRaw = parseInt(parts[1], 10);
  if (Number.isNaN(hRaw) || Number.isNaN(mRaw)) return trimmed;

  const m = Math.max(0, Math.min(59, mRaw));

  if (hRaw < 24) {
    const hStr = String(hRaw).padStart(2, "0");
    const mStr = String(m).padStart(2, "0");
    return `${hStr}:${mStr}`;
  }

  const extraDays = Math.floor(hRaw / 24);
  const h = hRaw % 24;
  const hStr = String(h).padStart(2, "0");
  const mStr = String(m).padStart(2, "0");

  if (extraDays === 1) {
    return `${hStr}:${mStr} next day`;
  }
  return `${hStr}:${mStr} +${extraDays} days`;
}

// Format a multi-line "limb" block (tithi/nakshatra/yoga/karana/sign)
function formatLimbBlockFromArrays(names, ends) {
  const lines = [];

  for (let i = 0; i < names.length; i++) {
    const name = names[i];
    let end = ends[i];

    if (!name) continue;

    if (!end || end === "ahoratra") {
      lines.push(`<div>${name}</div>`);
    } else {
      const disp = normalizeTimeWithNextDay(end);
      lines.push(`<div>${name} upto ${disp}</div>`);
    }
  }

  if (lines.length === 0) return "";
  return lines.join("");
}

// Moonsign block using moon_rashi1/2, optional change time
function formatMoonSignBlock(p) {
  const idx1 = p.moon_rashi1;
  const idx2 = p.moon_rashi2;
  const name1 = p.moon_rashi1_name || p.moon_rashi1 || "";
  const name2 = p.moon_rashi2_name || p.moon_rashi2 || "";
  const eng1 = idx1 ? RASHI_EN[idx1] : undefined;
  const eng2 = idx2 ? RASHI_EN[idx2] : undefined;

  const line1 = eng1 ? `${name1} (${eng1})` : name1;
  const line2 = eng2 ? `${name2} (${eng2})` : name2;

  const names = [];
  const ends = [];

  if (line1) {
    names.push(line1);
    ends.push(p.moon_rashi1_hm || null);
  }
  if (line2) {
    names.push(line2);
    ends.push(null);
  }

  return formatLimbBlockFromArrays(names, ends);
}

// Sunsign block (single line)
function formatSunSignBlock(p) {
  const idx = p.sun_rashi;
  const name = p.sun_rashi_name || p.sun_rashi || "";
  const eng = idx ? RASHI_EN[idx] : undefined;
  if (!name && !eng) return "";
  const line = eng ? `${name} (${eng})` : name;
  return `<div>${line}</div>`;
}

// four-column grid row: label1 | value1 | label2 | value2
function fourColRow(label1, value1, label2, value2) {
  const l1 = label1 ? `<span class="p-grid-label">${label1}</span>` : "";
  const v1 = value1 ? `<span class="p-grid-value">${value1}</span>` : "";
  const l2 = label2 ? `<span class="p-grid-label">${label2}</span>` : "";
  const v2 = value2 ? `<span class="p-grid-value">${value2}</span>` : "";
  return `<div class="p-grid-row">${l1}${v1}${l2}${v2}</div>`;
}

// ---------- DOM refs ------------------------------------------

const dayHeaderEl = document.getElementById("day-header");
const placeLineEl = document.getElementById("place-line");
const dailyOutputEl = document.getElementById("daily-output");
const errorBoxEl = document.getElementById("error-box");
const monthGridLink = document.getElementById("month-grid-link");
const printableMonthlyLink = document.getElementById("printable-monthly-link");

// header lines
const gregDateLineEl = document.getElementById("greg-date-line");
const bsDateLineEl = document.getElementById("bs-date-line");
const pakshaLineEl = document.getElementById("paksha-line");
const tithiMainLineEl = document.getElementById("tithi-main-line");
const monthNameLabelEl = document.getElementById("month-name-label");

// method / subtitle
const subtitleEl = document.getElementById("subtitle-line");

// local time display
const localTimeMainEl = document.getElementById("local-time-main");
const localTimeAmPmEl = document.getElementById("local-time-ampm");

// top nav buttons
const homeBtn = document.getElementById("home-btn");
const setLocationBtn = document.getElementById("set-location-btn");
const setMethodBtn = document.getElementById("set-method-btn");
const monthlyPatroBtn = document.getElementById("monthly-patro-btn");
const settingsBtn = document.getElementById("settings-btn");
const settingsSubmenu = document.getElementById("settings-submenu");

// method modal
const methodModal = document.getElementById("method-modal");
const methodKetakiRadio = document.getElementById("method-ketaki");
const methodDrikRadio = document.getElementById("method-drik");

// location modal DOM
const modalBackdrop = document.getElementById("location-modal");
const countrySelect = document.getElementById("country-select");
const stateSelect = document.getElementById("state-select");
const stateField = document.getElementById("state-field");
const citySelect = document.getElementById("city-select");

// calendar DOM
const calYearSelect = document.getElementById("calendar-year-select");
const calMonthButtons = document.querySelectorAll(".calendar-month-btn");
const calDayButtons = document.querySelectorAll(".calendar-day-btn");
const calPrevDayBtn = document.getElementById("calendar-prev-day");
const calNextDayBtn = document.getElementById("calendar-next-day");
const calTodayBtn = document.getElementById("calendar-today-btn");
const calPrevYearBtn = document.getElementById("calendar-prev-year");
const calNextYearBtn = document.getElementById("calendar-next-year");

// all cities payload from backend
const ALL = typeof ALL_CITIES !== "undefined" ? ALL_CITIES : [];

// ---------- Backend calls -------------------------------------

async function fetchDaily(dateStr, place, method) {
  const params = new URLSearchParams({
    date_ce: dateStr,
    city: place.city,
    state: place.state || "",
    country: place.country,
    lat: place.lat,
    lon: place.lon,
    standard: place.standard,
    tz: place.tz,
    engine: method,
  });

  const resp = await fetch(`/panchanga/daily?${params.toString()}`);
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status}`);
  }
  return resp.json();
}

// ---------- Method UI -----------------------------------------

function applyMethodUI(method) {
  if (subtitleEl) {
    subtitleEl.textContent =
      method === "drik" ? "Modern Drik Method" : "Traditional Ketaki Method";
  }

  if (methodKetakiRadio && methodDrikRadio) {
    if (method === "drik") {
      methodDrikRadio.checked = true;
      methodKetakiRadio.checked = false;
    } else {
      methodKetakiRadio.checked = true;
      methodDrikRadio.checked = false;
    }
  }
}

// ---------- Local time clock ----------------------------------

let clockTimerId = null;

function startLocalClock(place) {
  if (!localTimeMainEl || !localTimeAmPmEl) return;

  const tz = place && place.tz ? place.tz : undefined;
  if (!tz) {
    localTimeMainEl.textContent = "--:--";
    localTimeAmPmEl.textContent = "";
    if (clockTimerId) clearInterval(clockTimerId);
    clockTimerId = null;
    return;
  }

  function tick() {
    const now = new Date();
    try {
      const fmt = new Intl.DateTimeFormat("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
        timeZone: tz,
      });
      const parts = fmt.formatToParts(now);
      const hour = parts.find((p) => p.type === "hour")?.value ?? "--";
      const minute = parts.find((p) => p.type === "minute")?.value ?? "--";
      const dayPeriod =
        parts.find((p) => p.type === "dayPeriod")?.value.toUpperCase() ?? "";
      localTimeMainEl.textContent = `${hour}:${minute}`;
      localTimeAmPmEl.textContent = dayPeriod;
    } catch (e) {
      localTimeMainEl.textContent = "--:--";
      localTimeAmPmEl.textContent = "";
    }
  }

  if (clockTimerId) clearInterval(clockTimerId);
  tick();
  clockTimerId = setInterval(tick, 30000);
}

// ---------- Calendar helpers ----------------------------------

function daysInMonth(year, month) {
  return new Date(year, month, 0).getDate();
}

function syncCalendar(dateStr) {
  if (!calYearSelect) return;

  const d0 = isoToDate(dateStr);
  const d = clampDateToRange(d0);
  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();

  if (!calYearSelect.options.length) {
    for (let y = 2020; y <= 2030; y++) {
      const opt = document.createElement("option");
      opt.value = String(y);
      opt.textContent = String(y);
      calYearSelect.appendChild(opt);
    }
  }
  calYearSelect.value = String(year);

  const dim = daysInMonth(year, month);
  calMonthButtons.forEach((btn) => {
    const m = parseInt(btn.getAttribute("data-month"), 10);
    btn.classList.toggle("selected", m === month);
  });

  calDayButtons.forEach((btn) => {
    const dnum = parseInt(btn.getAttribute("data-day"), 10);
    btn.classList.remove("selected", "disabled");
    if (dnum === day) btn.classList.add("selected");
    if (dnum > dim) btn.classList.add("disabled");
  });
}

// ---------- Rendering -----------------------------------------

function renderDaily(dateStr, place, p) {
  const d = isoToDate(dateStr);

  // --- HEADER: Sunday / November 23, 2025 / BS line ---

  const weekdayName = d.toLocaleDateString(undefined, { weekday: "long" });
  const fullDate = d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  dayHeaderEl.textContent = weekdayName;

  if (gregDateLineEl) gregDateLineEl.textContent = fullDate;

  const sunDay = p.sun_day;
  const sunMonthName = p.month_name || "";
  const bsYear = p.bs_year;
  let bsLine = "";
  if (sunDay && sunMonthName && bsYear) {
    const dayStr = String(sunDay).padStart(2, "0");
    bsLine = `${dayStr} ${sunMonthName} ${bsYear} BS`;
  } else {
    const vikramaDate = p.date_bs || p.vikram_date || p.vikrama_date || "";
    bsLine = vikramaDate;
  }
  if (bsDateLineEl) bsDateLineEl.textContent = bsLine;

  // --- PLACE LINE -------------------------------------------------

  const stateLabel = place.state ? prettyCode(place.state) : "";
  const countryLabel = prettyCode(place.country);
  const basePlace = `${place.city}${
    stateLabel ? ", " + stateLabel : ""
  }, ${countryLabel}`;

  let coordPart = "";
  if (
    place &&
    place.lat !== undefined &&
    place.lon !== undefined &&
    place.lat !== null &&
    place.lon !== null
  ) {
    const latNum = Number(place.lat);
    const lonNum = Number(place.lon);
    if (isFinite(latNum) && isFinite(lonNum)) {
      function toDM(value, isLat) {
        const dir = isLat ? (value >= 0 ? "N" : "S") : value >= 0 ? "E" : "W";
        const abs = Math.abs(value);
        const deg = Math.floor(abs);
        const min = Math.round((abs - deg) * 60);
        const minStr = String(min).padStart(2, "0");
        return `${deg}°${minStr}' ${dir}`;
      }

      const latStr = toDM(latNum, true);
      const lonStr = toDM(lonNum, false);
      coordPart = ` (${latStr}, ${lonStr})`;
    }
  }

  placeLineEl.textContent = basePlace + coordPart;

  // --- CORE FIELDS FROM PANCHANGA RESULT --------------------------

  const sunrise =
    p.sunrise_hm || p.sunrise || p.sunrise_time || p.Sunrise || "";
  const sunset = p.sunset_hm || p.sunset || p.sunset_time || p.Sunset || "";

  const lunarMonth = p.month_name || p.lunar_month || p.LunarMonth || "";
  const paksha = p.paksha || "";

  const tithiNames = [p.tithi1_name, p.tithi2_name, p.tithi3_name];
  const tithiEnds = [p.tithi1_hm, p.tithi2_hm, p.tithi3_hm];

  const nakshatraNames = [
    p.nakshatra1_name,
    p.nakshatra2_name,
    p.nakshatra3_name,
  ];
  const nakshatraEnds = [
    p.nakshatra1_hm,
    p.nakshatra2_hm,
    p.nakshatra3_hm,
  ];

  const yogaNames = [p.yoga1_name, p.yoga2_name, p.yoga3_name];
  const yogaEnds = [p.yoga1_hm, p.yoga2_hm, p.yoga3_hm];

  const karanaNames = [
    p.karana1_name,
    p.karana2_name,
    p.karana3_name,
    p.karana4_name,
  ];
  const karanaEnds = [
    p.karana1_hm,
    p.karana2_hm,
    p.karana3_hm,
    p.karana4_hm,
  ];

  const dinamana = p.dinamana_hm || p.dinamana_gp || p.dinamana_dec || "";

  const pakshaDisplay =
    typeof paksha === "string" && paksha
      ? paksha.charAt(0).toUpperCase() + paksha.slice(1)
      : "";

  if (monthNameLabelEl) {
    monthNameLabelEl.textContent = lunarMonth || "";
  }
  if (pakshaLineEl) {
    pakshaLineEl.textContent = pakshaDisplay;
  }
  if (tithiMainLineEl) {
    tithiMainLineEl.textContent = p.tithi1_name || tithiNames[0] || "";
  }

  const rows = [];

  // Row 1: Sunrise / Sunset
  rows.push(fourColRow("Sunrise", sunrise, "Sunset", sunset));

  // Row 2: Tithi / Nakshatra
  const tithiBlock = formatLimbBlockFromArrays(tithiNames, tithiEnds);
  const nakshatraBlock = formatLimbBlockFromArrays(
    nakshatraNames,
    nakshatraEnds
  );
  if (tithiBlock || nakshatraBlock) {
    rows.push(fourColRow("Tithi", tithiBlock, "Nakshatra", nakshatraBlock));
  }

  // Row 3: Yoga / Karana
  const yogaBlock = formatLimbBlockFromArrays(yogaNames, yogaEnds);
  const karanaBlock = formatLimbBlockFromArrays(karanaNames, karanaEnds);
  if (yogaBlock || karanaBlock) {
    rows.push(fourColRow("Yoga", yogaBlock, "Karana", karanaBlock));
  }

  // Row 4: Moonsign / Sunsign
  const moonBlock = formatMoonSignBlock(p);
  const sunBlock = formatSunSignBlock(p);
  if (moonBlock || sunBlock) {
    rows.push(fourColRow("Moonsign", moonBlock, "Sunsign", sunBlock));
  }

  // Row 5: Dinamana
  if (dinamana) {
    rows.push(fourColRow("Dinamana", dinamana, "", ""));
  }

  dailyOutputEl.innerHTML =
    rows.length === 0
      ? "<em>No Panchanga fields available.</em>"
      : rows.join("\n");
}

// keep monthly links pointing to same year/month/place/method
function updateMonthLinks(dateStr, place, method) {
  if (!monthGridLink && !printableMonthlyLink) return;
  const d = isoToDate(dateStr);
  const year = d.getFullYear();
  const month = d.getMonth() + 1;

  const baseParams = new URLSearchParams({
    year: String(year),
    month: String(month).padStart(2, "0"),
    city: place.city,
    state: place.state || "",
    country: place.country,
    lat: String(place.lat),
    lon: String(place.lon),
    standard: String(place.standard),
    tz: place.tz,
    method,
  });

  if (monthGridLink) {
    const params = new URLSearchParams(baseParams);
    params.set("mode", "grid");
    monthGridLink.href = `/month?${params.toString()}`;
  }
  if (printableMonthlyLink) {
    const params = new URLSearchParams(baseParams);
    params.set("mode", "print");
    printableMonthlyLink.href = `/month?${params.toString()}`;
  }
}

// ---------- Main load ----------------------------------------

async function loadDaily() {
  const { date, place, method } = loadState();

  applyMethodUI(method);
  syncCalendar(date);
  startLocalClock(place);

  dayHeaderEl.textContent = "Loading…";
  dailyOutputEl.innerHTML = "";
  errorBoxEl.style.display = "none";
  errorBoxEl.textContent = "";

  updateMonthLinks(date, place, method);

  try {
    const data = await fetchDaily(date, place, method);
    const p = data.panchanga_result || data.result || data.data || data;
    renderDaily(date, place, p);
  } catch (err) {
    console.error("loadDaily error:", err);
    dayHeaderEl.textContent = "Error loading Panchanga";
    errorBoxEl.style.display = "block";
    errorBoxEl.textContent =
      "Could not load Panchanga for this date. Please try again.";
  }
}

// ---------- Date helpers used by calendar & Home -------------

function today() {
  const t = todayISO();
  saveState({ date: t });
  loadDaily();
}

// ---------- Method modal logic --------------------

function openMethodModal() {
  if (!methodModal) return;
  const st = loadState();
  applyMethodUI(st.method || DEFAULT_METHOD);
  methodModal.style.display = "flex";
}

function closeMethodModal() {
  if (!methodModal) return;
  methodModal.style.display = "none";
}

function saveMethodFromModal() {
  if (!methodKetakiRadio || !methodDrikRadio) {
    closeMethodModal();
    return;
  }
  let newMethod = DEFAULT_METHOD;
  if (methodDrikRadio.checked) newMethod = "drik";
  if (methodKetakiRadio.checked) newMethod = "ketaki";

  saveState({ method: newMethod });
  closeMethodModal();
  loadDaily();
}

// ---------- Location modal logic ------------------------------

function uniqueSorted(list) {
  return Array.from(new Set(list.filter((x) => x && x.trim() !== ""))).sort();
}

function buildCountryOptions() {
  if (!countrySelect) return;
  const countries = uniqueSorted(ALL.map((c) => c.country));
  countrySelect.innerHTML = countries
    .map((c) => {
      const label = prettyCode(c);
      return `<option value="${c}">${label}</option>`;
    })
    .join("");

  const st = loadState();
  const current = st.place;
  if (current && current.country) {
    const idx = countries.indexOf(current.country);
    if (idx >= 0) countrySelect.value = current.country;
  }
  buildStateOptions();
}

function buildStateOptions() {
  if (!countrySelect || !stateSelect || !stateField) return;
  const country = countrySelect.value;
  const states = uniqueSorted(
    ALL.filter((c) => c.country === country).map((c) => c.state)
  );
  if (states.length === 0) {
    stateField.style.display = "none";
    stateSelect.innerHTML = "";
  } else {
    stateField.style.display = "block";
    stateSelect.innerHTML = states
      .map((s) => {
        const label = prettyCode(s);
        return `<option value="${s}">${label}</option>`;
      })
      .join("");

    const st = loadState();
    const current = st.place;
    if (current && current.country === country && current.state) {
      const idx = states.indexOf(current.state);
      if (idx >= 0) stateSelect.value = current.state;
    }
  }
  buildCityOptions();
}

function buildCityOptions() {
  if (!countrySelect || !citySelect) return;
  const country = countrySelect.value;
  const state =
    stateField && stateField.style.display !== "none" ? stateSelect.value : "";

  let filtered = ALL.filter((c) => c.country === country);
  if (state) {
    filtered = filtered.filter((c) => c.state === state);
  }
  citySelect.innerHTML = filtered
    .map((c) => `<option value="${c.index}">${c.city}</option>`)
    .join("");

  const st = loadState();
  const cur = st.place;
  if (cur) {
    const match = filtered.find(
      (c) =>
        c.city === cur.city &&
        c.country === cur.country &&
        (c.state || "") === (cur.state || "")
    );
    if (match) {
      citySelect.value = String(match.index);
    }
  }
}

function openLocationModal() {
  if (!modalBackdrop) return;
  if (!ALL || ALL.length === 0) {
    alert("City list not available.");
    return;
  }
  buildCountryOptions();
  modalBackdrop.style.display = "flex";
}

function closeLocationModal() {
  if (!modalBackdrop) return;
  modalBackdrop.style.display = "none";
}

function saveLocationFromModal() {
  if (!citySelect) return;
  const idx = parseInt(citySelect.value, 10);
  if (Number.isNaN(idx)) {
    closeLocationModal();
    return;
  }
  const c = ALL.find((row) => row.index === idx);
  if (!c) {
    closeLocationModal();
    return;
  }
  const place = {
    city: c.city,
    state: c.state || "",
    country: c.country,
    lat: c.latitude,
    lon: c.longitude,
    standard: c.standard,
    tz: c.tz,
  };
  saveState({ place });
  closeLocationModal();
  loadDaily();
}

if (countrySelect) countrySelect.addEventListener("change", buildStateOptions);
if (stateSelect) stateSelect.addEventListener("change", buildCityOptions);

// ---------- Calendar interactions ----------------------------

if (calYearSelect) {
  calYearSelect.addEventListener("change", () => {
    const st = loadState();
    const baseDate = isoToDate(st.date || todayISO());
    const newYear = Math.min(
      2030,
      Math.max(2020, parseInt(calYearSelect.value, 10))
    );
    const month = baseDate.getMonth() + 1;
    let day = baseDate.getDate();
    const dim = daysInMonth(newYear, month);
    if (day > dim) day = dim;
    const newDate = clampDateToRange(new Date(newYear, month - 1, day));
    const iso = dateToISO(newDate);
    saveState({ date: iso });
    loadDaily();
  });
}

calMonthButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const st = loadState();
    const baseDate = isoToDate(st.date || todayISO());
    const year = baseDate.getFullYear();
    const month = parseInt(btn.getAttribute("data-month"), 10);
    let day = baseDate.getDate();
    const dim = daysInMonth(year, month);
    if (day > dim) day = dim;
    const newDate = clampDateToRange(new Date(year, month - 1, day));
    const iso = dateToISO(newDate);
    saveState({ date: iso });
    loadDaily();
  });
});

calDayButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    if (btn.classList.contains("disabled")) return;
    const st = loadState();
    const baseDate = isoToDate(st.date || todayISO());
    const year = baseDate.getFullYear();
    const month = baseDate.getMonth() + 1;
    const day = parseInt(btn.getAttribute("data-day"), 10);
    const newDate = clampDateToRange(new Date(year, month - 1, day));
    const iso = dateToISO(newDate);
    saveState({ date: iso });
    loadDaily();
  });
});

if (calPrevDayBtn) {
  calPrevDayBtn.addEventListener("click", () => {
    const st = loadState();
    const baseDate = isoToDate(st.date || todayISO());
    baseDate.setDate(baseDate.getDate() - 1);
    const newDate = clampDateToRange(baseDate);
    const iso = dateToISO(newDate);
    saveState({ date: iso });
    loadDaily();
  });
}

if (calNextDayBtn) {
  calNextDayBtn.addEventListener("click", () => {
    const st = loadState();
    const baseDate = isoToDate(st.date || todayISO());
    baseDate.setDate(baseDate.getDate() + 1);
    const newDate = clampDateToRange(baseDate);
    const iso = dateToISO(newDate);
    saveState({ date: iso });
    loadDaily();
  });
}

if (calPrevYearBtn) {
  calPrevYearBtn.addEventListener("click", () => {
    const st = loadState();
    const baseDate = isoToDate(st.date || todayISO());
    let year = baseDate.getFullYear() - 1;
    year = Math.min(2030, Math.max(2020, year));
    const month = baseDate.getMonth() + 1;
    let day = baseDate.getDate();
    const dim = daysInMonth(year, month);
    if (day > dim) day = dim;
    const newDate = clampDateToRange(new Date(year, month - 1, day));
    const iso = dateToISO(newDate);
    saveState({ date: iso });
    loadDaily();
  });
}

if (calNextYearBtn) {
  calNextYearBtn.addEventListener("click", () => {
    const st = loadState();
    const baseDate = isoToDate(st.date || todayISO());
    let year = baseDate.getFullYear() + 1;
    year = Math.min(2030, Math.max(2020, year));
    const month = baseDate.getMonth() + 1;
    let day = baseDate.getDate();
    const dim = daysInMonth(year, month);
    if (day > dim) day = dim;
    const newDate = clampDateToRange(new Date(year, month - 1, day));
    const iso = dateToISO(newDate);
    saveState({ date: iso });
    loadDaily();
  });
}

if (calTodayBtn) {
  calTodayBtn.addEventListener("click", () => {
    today();
  });
}

// ---------- Top nav: Home / Settings / Monthly Patro ----------

if (homeBtn) {
  homeBtn.addEventListener("click", () => {
    // only reset the date, keep last known place & method
    saveState({
      date: todayISO(),
    });
    loadDaily();
  });
}

if (settingsBtn && settingsSubmenu) {
  settingsBtn.addEventListener("click", () => {
    settingsSubmenu.classList.toggle("open");
  });
}

if (setLocationBtn) {
  setLocationBtn.addEventListener("click", () => {
    openLocationModal();
  });
}

if (setMethodBtn) {
  setMethodBtn.addEventListener("click", () => {
    openMethodModal();
  });
}

if (monthlyPatroBtn && monthGridLink) {
  monthlyPatroBtn.addEventListener("click", () => {
    // navigate to same URL as "Monthly grid view"
    window.location.href = monthGridLink.href;
  });
}

// ---------- Startup -------------------------------------------

window.onload = loadDaily;

window.openLocationModal = openLocationModal;
window.closeLocationModal = closeLocationModal;
window.saveLocationFromModal = saveLocationFromModal;

window.openMethodModal = openMethodModal;
window.closeMethodModal = closeMethodModal;
window.saveMethodFromModal = saveMethodFromModal;
