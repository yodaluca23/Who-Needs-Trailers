import fastapi
from base64 import urlsafe_b64decode
import requests

app = fastapi.FastAPI()
session = requests.Session()

@app.get("/{base64_addon}/manifest.json")
def get_manifest(base64_addon: str) -> dict:

    try:
        urlsafe_b64decode(base64_addon.encode())
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail="Invalid base64 encoding")

    return {
        "id": "dev.yodaluca.who-needs-trailers",
        "version": "1.0.0",
        "name": "Who Needs Trailers",
        "description": "Trailer addon - Converts Movies and TV Shows into Trailers",
        "resources": [
            {"name": "meta", "types": ["movie", "series"], "idPrefixes": ["tt"]}
        ],
        "types": ["movie", "series"],
        "idPrefixes": ["tt"],
        "catalogs": [],
    }


@app.get("/{base64_addon}/meta/{type}/{imdb_id}.json")
def get_meta(base64_addon: str, type: str, imdb_id: str) -> dict:
    addon_url = urlsafe_b64decode(base64_addon.encode()).decode()
    streams = session.get(f"{addon_url.replace('/manifest.json', '')}/stream/{type}/{imdb_id}.json")
    if streams.status_code != 200:
        return fastapi.HTTPException(status_code=404, detail="Movie/show not found")
    
    streams = streams.json()

    links = []
    for link in streams.get("streams", []):
        if link.get("url", "").endswith(".mp4"):
            links.append({
                "trailers": link["url"],
                "provider": link.get("name", "Unknown"),
            })

    return {
        "meta": {
            "id": imdb_id,
            "type": type,
            "name": f"{type} {imdb_id}",
            "links": links,
        }
    }
