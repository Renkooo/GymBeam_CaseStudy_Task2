import os
import sys
import csv
import json
import time
import argparse
import logging
import requests

API_BASE = "https://api.golemio.cz"
ENDPOINT = "/v2/municipallibraries"
DEFAULT_PAGE_SIZE = 100

OUTPUT_COLUMNS = [
    "id_kniznice", "nazov_kniznice", "ulica", "psc", "mesto",
    "kraj", "krajina", "zemepisna_sirka", "zemepisna_dlzka", "cas_otvorenia"
]

def parse_opening_hours(opening_hours):
    """Z listu otvaracich hodin vytvori retazec 'Po 09:00-12:00; Ut ...'."""
    if not isinstance(opening_hours, list):
        return json.dumps(opening_hours, ensure_ascii=False)

    weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    weekday_abbrev_sk = {
        "Monday": "Po", "Tuesday": "Ut", "Wednesday": "St",
        "Thursday": "Št", "Friday": "Pi", "Saturday": "So", "Sunday": "Ne",
    }

    formatted_slots = []
    for weekday in weekday_order:
        for slot in opening_hours:
            if isinstance(slot, dict) and slot.get("day_of_week") == weekday:
                opens_at = slot.get("opens")
                closes_at = slot.get("closes")
                if opens_at and closes_at:
                    formatted_slots.append(f"{weekday_abbrev_sk.get(weekday, weekday[:2])} {opens_at}-{closes_at}")

    return "; ".join(formatted_slots) if formatted_slots else json.dumps(opening_hours, ensure_ascii=False)

def normalize_library_feature(feature):
    """Prevedie GeoJSON feature kniznice na pozadovanych 10 poli."""
    properties = feature.get("properties", {}) if isinstance(feature.get("properties"), dict) else feature
    address = properties.get("address", {}) if isinstance(properties.get("address"), dict) else {}

    longitude, latitude = None, None
    geometry = feature.get("geometry", {})
    if isinstance(geometry, dict):
        coordinates = geometry.get("coordinates")
        if isinstance(coordinates, (list, tuple)) and len(coordinates) >= 2:
            longitude, latitude = coordinates[0], coordinates[1]

    opening_hours = properties.get("opening_hours")
    if isinstance(opening_hours, list):
        opening_hours = parse_opening_hours(opening_hours)
    elif isinstance(opening_hours, dict):
        opening_hours = json.dumps(opening_hours, ensure_ascii=False)

    return {
        "id_kniznice": properties.get("id"),
        "nazov_kniznice": properties.get("name"),
        "ulica": address.get("street_address"),
        "psc": address.get("postal_code"),
        "mesto": address.get("address_locality"),
        "kraj": address.get("address_region"),
        "krajina": address.get("address_country") or "Česko",
        "zemepisna_sirka": latitude,
        "zemepisna_dlzka": longitude,
        "cas_otvorenia": opening_hours,
    }

def fetch_all(http_session, page_size):
    """Vytahuje vsetky zaznamy pomocou strankovania limit+offset."""
    current_offset = 0
    while True:
        query_params = {"limit": page_size, "offset": current_offset}
        response = http_session.get(API_BASE + ENDPOINT, params=query_params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        features = payload.get("features") if isinstance(payload, dict) else None
        if not features:
            break

        for feature in features:
            yield feature

        if len(features) < page_size:
            break

        current_offset += page_size
        time.sleep(0.2)

def write_csv_file(file_path, records):
    os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
    with open(file_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

def write_jsonl_file(file_path, records):
    os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
    with open(file_path, "w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Extraktor dat o knizniciach")
    parser.add_argument("-o", "--out-prefix", dest="out_prefix", default="vystup_kniznice",
                        help="vystupny prefix suborov (CSV a JSONL)")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help="limit na dotaz")
    parser.add_argument("--verbose", action="store_true", help="zapne DEBUG logy")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s - %(message)s")

    access_token = os.getenv("GOLEMIO_API_KEY")
    # access_token = ""          # priprava pre testovanie, ak je potrebne pouzitie bez enviromentalnej premennej
    
    if not access_token:
        sys.exit("Chyba env premenna GOLEMIO_API_KEY.")

    http_session = requests.Session()
    http_session.headers.update({
        "X-Access-Token": access_token,
    })

    normalized_records = []
    try:
        for feature in fetch_all(http_session, args.page_size):
            normalized_records.append(normalize_library_feature(feature))
    except requests.RequestException as err:
        logging.error("HTTP chyba: %s", err)
        sys.exit(1)

    logging.info("Stiahnutých záznamov: %d", len(normalized_records))

    csv_output_path = f"{args.out_prefix}.csv"
    jsonl_output_path = f"{args.out_prefix}.jsonl"
    write_csv_file(csv_output_path, normalized_records)
    write_jsonl_file(jsonl_output_path, normalized_records)
    logging.info("Hotovo: %s, %s", csv_output_path, jsonl_output_path)

if __name__ == "__main__":
    main()
