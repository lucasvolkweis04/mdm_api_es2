from dem_service.transform import clean_countries_full
import os, json, requests
from datetime import datetime
from sqlalchemy.orm import Session
from dem_service import crud, models
from dotenv import load_dotenv
from types import SimpleNamespace

load_dotenv()
MDM_URL = os.getenv("MDM_URL")

BASE_STORAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
RAW_DIR = os.path.join(BASE_STORAGE, "raw")
PROCESSED_DIR = os.path.join(BASE_STORAGE, "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def transform(data):
    result = []
    rejected = []
    seen_cca3 = set()

    for country in data:
        try:
            cca3 = country.get("cca3")
            name = country.get("name", {}).get("common")

            if not cca3 or not name or cca3 in seen_cca3:
                rejected.append(country)
                continue

            capital = country.get("capital", [])
            if isinstance(capital, str):
                capital = [capital]
            elif capital is None:
                capital = []

            result.append({
                "cca3": cca3,
                "name": name,
                "region": country.get("region"),
                "subregion": country.get("subregion"),
                "population": country.get("population", 0),
                "area": country.get("area", 0.0),
                "capital": capital
            })

            seen_cca3.add(cca3)
        except Exception:
            rejected.append(country)

    return result, rejected

