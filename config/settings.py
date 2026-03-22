from __future__ import annotations

import os

APP_NAME = "BheshajPatro"
APP_ENV = os.getenv("APP_ENV", "development")
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-before-production")
SESSION_COOKIE_NAME = "bheshajpatro_session"