# static/js/month_grid.js

const DEFAULT_ENGINE = typeof INITIAL_METHOD !== "undefined" ? INITIAL_METHOD : "ketaki";

let currentYear;
let currentMonth;
let currentEngine = DEFAULT_ENGINE;

function ensureStateForMonth() {
  const s = State.load();
  if (!s.place || !s.place.city) {
    s.place = { ...DEFAULT_PLACE };
    State.savePlace(s.place);
  }
  if (!s.date) {
    s.date = todayISO();
    State.saveDate(s.date);
  }
  return s;
}

async function loadMonthGrid() {
  const state = ensureStateForMonth();

  if (!currentYear || !currentMonth) {
    const d = new Date(state.date);
    currentYear = d.getFullYear();
    currentMonth = d.getMonth() + 1;
  }

  const headerEl = document.getElementById("month-label");
  if (headerEl) {
    headerEl.textContent = `${monthName(currentMonth)} ${currentYear} — ${state.place.city}, ${state.place.country} (${currentEngine})`;
  }

  const data = await API.fetchMonth({
    year: currentYear,
    month: currentMonth,
    place: state.place,
    engine: currentEngine,
  });

  renderGrid(data);
}

function renderGrid(data) {
  const grid = document.getElementById("month-grid");
  if (!grid) return;
  grid.innerHTML = "";

  const firstDate = new Date(data.year, data.month - 1, 1);
  const firstDow = firstDate.getDay(); // 0=Sun..6=Sat
  const numDays = data.days.length;

  const byDate = {};
  data.days.forEach((d) => {
    byDate[d.date] = d;
  });

  let html = "<table class='month-table'><thead><tr>";
  ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].forEach((d) => {
    html += `<th>${d}</th>`;
  });
  html += "</tr></thead><tbody>";

  let day = 1;

  for (let week = 0; week < 6; week++) {
    if (day > numDays) break;
    html += "<tr>";
    for (let dow = 0; dow < 7; dow++) {
      if ((week === 0 && dow < firstDow) || day > numDays) {
        html += "<td class='empty'></td>";
      } else {
        const yyyy = data.year.toString().padStart(4, "0");
        const mm = data.month.toString().padStart(2, "0");
        const dd = day.toString().padStart(2, "0");
        const iso = `${yyyy}-${mm}-${dd}`;
        const entry = byDate[iso] || {};
        const tithi = entry.tithi_name || "";
        const nak = entry.nakshatra_name || "";

        html += `
          <td class="day-cell" onclick="gotoDaily('${iso}')">
            <div class="day-number">${day}</div>
            <div class="day-tithi">${tithi}</div>
            <div class="day-nak">${nak}</div>
          </td>
        `;
        day++;
      }
    }
    html += "</tr>";
  }

  html += "</tbody></table>";
  grid.innerHTML = html;
}

function gotoDaily(isoDate) {
  State.saveDate(isoDate);
  const url = currentEngine === "drik" ? "/drik" : "/";
  window.location.href = url;
}

function changeMonth(delta) {
  currentMonth += delta;
  if (currentMonth < 1) {
    currentMonth = 12;
    currentYear -= 1;
  } else if (currentMonth > 12) {
    currentMonth = 1;
    currentYear += 1;
  }
  loadMonthGrid();
}

function monthName(m) {
  const names = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  return names[m - 1] || "";
}

window.addEventListener("load", loadMonthGrid);
