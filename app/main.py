from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

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


@app.get("/api/panchanga/today")
def api_panchanga_today(request: Request):
    settings = load_user_settings(request)
    engine = settings["engine"]
    place = settings["place"]

    payload = get_panchanga_result(
        date_ce=date.today(),
        place=place,
        engine=engine,
    )

    if hasattr(payload, "model_dump"):
        return JSONResponse(payload.model_dump())

    return JSONResponse(payload.dict())