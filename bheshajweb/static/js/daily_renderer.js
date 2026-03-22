// static/js/daily_renderer.js

function renderDailyPanchanga(data) {
    const root = document.getElementById("panchanga-output");
    if (!root) return;

    const p = data.data;

    root.innerHTML = `
        <div class="panchanga-card">

            <h2>${data.date} — ${data.place.city}, ${data.place.country}</h2>
            <h3>Method: ${data.engine.toUpperCase()}</h3>

            <section>
                <h4>Sun</h4>
                <div>Sunrise: ${p.sunrise ?? ""}</div>
                <div>Sunset: ${p.sunset ?? ""}</div>
            </section>

            <section>
                <h4>Lunar</h4>
                <div>Tithi: ${p.tithi_name ?? ""} (ends ${p.tithi_hm ?? ""})</div>
                <div>Nakshatra: ${p.nakshatra_name ?? ""} (ends ${p.naksha_hm ?? ""})</div>
                <div>Yoga: ${p.yoga_name ?? ""} (ends ${p.yoga_hm ?? ""})</div>
                <div>Rashi: Sun ${p.sun_rashi}, Moon ${p.moon_rashi}</div>
            </section>

        </div>
    `;
}
