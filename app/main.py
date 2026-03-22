from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from bheshajpatro.core.worldcities import all_cities

from bheshajpatro.config.settings import (
    APP_NAME,
    APP_DEBUG,
    SECRET_KEY,
    SESSION_COOKIE_NAME,
)
from bheshajpatro.app.settings_store import (
    load_user_settings,
    save_user_settings,
    clear_user_settings,
)
from bheshajpatro.pbuilder.service import get_panchanga_result

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title=APP_NAME, debug=APP_DEBUG)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie=SESSION_COOKIE_NAME,
)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    settings = load_user_settings(request)
    engine = settings["engine"]
    place = settings["place"]

    payload = get_panchanga_result(
        date_ce=date.today(),
        place=place,
        engine=engine,
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "engine": engine,
            "place": place,
            "panchanga": payload,
        },
    )


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    settings = load_user_settings(request)
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "engine": settings["engine"],
            "place": settings["place"],
        },
    )


@app.post("/settings")
def settings_save(
    request: Request,
    engine: str = Form(...),
    key: str = Form(""),
    name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    standard: float = Form(...),
    tz: str = Form(...),
    elevation: float = Form(0.0),
):
    place = {
        "key": key.strip(),
        "name": name.strip(),
        "latitude": latitude,
        "longitude": longitude,
        "standard": standard,
        "tz": tz.strip(),
        "elevation": elevation,
    }

    save_user_settings(request, engine=engine.strip().lower(), place=place)
    return RedirectResponse(url="/", status_code=303)


@app.post("/settings/clear")
def settings_clear(request: Request):
    clear_user_settings(request)
    return RedirectResponse(url="/settings", status_code=303)


@app.get("/api/panchanga/day")
def api_panchanga_day(request: Request, date_str: str):
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        return JSONResponse({"error": "invalid date"}, status_code=400)

    settings = load_user_settings(request)
    payload = get_panchanga_result(
        date_ce=d,
        place=settings["place"],
        engine=settings["engine"],
    )

    return JSONResponse(payload.model_dump())


@app.get("/api/cities/countries")
def api_countries():
    cities = all_cities()
    seen = {}
    for c in cities:
        if c.country_code not in seen:
            seen[c.country_code] = c.country
    countries = sorted(seen.items(), key=lambda x: x[1])
    return JSONResponse([{"code": cc, "name": name} for cc, name in countries])


@app.get("/api/cities/states")
def api_states(country_code: str):
    cities = all_cities()
    seen = {}
    for c in cities:
        if c.country_code.lower() == country_code.lower() and c.state_code:
            seen[c.state_code] = c.state
    states = sorted(seen.items(), key=lambda x: x[1])
    return JSONResponse([{"code": sc, "name": name} for sc, name in states])


@app.get("/api/cities/cities")
def api_cities(country_code: str, state_code: str = ""):
    cities = all_cities()
    filtered = [
        c for c in cities
        if c.country_code.lower() == country_code.lower()
        and (not state_code or c.state_code.lower() == state_code.lower())
    ]
    filtered = sorted(filtered, key=lambda c: c.city)
    return JSONResponse([{
        "key": c.location_key,
        "name": ", ".join(filter(None, [
            c.city.title(),
            c.state.title() if c.state.strip() else None,
            c.country,
        ])),
        "city_name": c.city.title(),
        "latitude": c.latitude,
        "longitude": c.longitude,
        "standard": c.standard,
        "tz": c.tz,
        "elevation": 0.0,
    } for c in filtered])