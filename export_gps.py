import json
import urllib.request
import urllib.parse
from pathlib import Path

AUTH_FILE = Path.home() / ".config/immich/auth.yml"

def load_auth():
    cfg = {}
    for line in AUTH_FILE.read_text().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            cfg[k.strip()] = v.strip()
    return cfg["url"].rstrip("/"), cfg["key"]

def api_post(base_url, api_key, path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        headers={"x-api-key": api_key, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def export_gps_data(out_file="gps_data.json"):
    base_url, api_key = load_auth()
    points = []
    next_page = None

    while True:
        body = {"size": 1000, "withExif": True}
        if next_page:
            body["page"] = next_page
        data = api_post(base_url, api_key, "/search/metadata", body)

        items = data.get("assets", {}).get("items", [])
        for a in items:
            exif = a.get("exifInfo") or {}
            lat = exif.get("latitude")
            lng = exif.get("longitude")
            if lat is None or lng is None:
                continue
            points.append({
                "lat": lat,
                "lng": lng,
                "date": (a.get("fileCreatedAt") or "")[:10],
                "city": exif.get("city") or "",
                "state": exif.get("state") or "",
                "country": exif.get("country") or "",
                "id": a["id"],
            })

        next_page = data.get("assets", {}).get("nextPage")
        if not next_page:
            break

    Path(out_file).write_text(json.dumps(points, ensure_ascii=False, indent=2))
    print(f"Exported {len(points)} GPS points → {out_file}")
    return points

if __name__ == "__main__":
    export_gps_data()
