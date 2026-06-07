# ============================================================
# DATA PIPELINE EXTRACT & TRANSFORM CORE ENGINE
# ============================================================
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import requests


def get_station_data(station):
    """Extracts and parses geospatial XML observations from the FMI WFS API."""
    url = f"https://fmi.fi{station}"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        root = ET.fromstring(r.text)

        latest_time, latest_wind = None, None
        for elem in root.iter():
            if not elem.text:
                continue
            text = elem.text.strip()

            if "T" in text:
                try:
                    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
                    if latest_time is None or dt > latest_time:
                        latest_time = dt
                except ValueError:
                    pass

            try:
                v = float(text)
                if 0 <= v <= 60:
                    latest_wind = v
            except ValueError:
                pass

        return {"timestamp": latest_time, "wind": latest_wind}
    except Exception as e:
        print(f"Extraction error for station {station}: {e}")
        return None


# Note: Cloud Database Staging is handled via secure PostgreSQL UPSERT workflows.
# Full repository kept private for proprietary analytics security.
