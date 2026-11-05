#!/usr/bin/env python3
"""Cautious updater for the public Epoch ECI CSV.

If an upstream schema changes, the update fails CLOSED and keeps the last valid
snapshot. Never fill missing benchmark values with estimates or fake dates.
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "snapshot.json"
ECI_URL = "https://epoch.ai/data/eci_scores.csv"
UTC = dt.timezone.utc


def now():
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def choose(fields, options):
    normal = {re.sub(r"[^a-z0-9]+", "", x.lower()): x for x in fields}
    for option in options:
        key = re.sub(r"[^a-z0-9]+", "", option.lower())
        if key in normal:
            return normal[key]
    return None


def numeric(value):
    if value is None:
        return None
    try:
        v = float(str(value).replace(",", "").strip())
        if 0 < v < 500 and v == v:
            return round(v, 2)
    except (ValueError, TypeError):
        pass
    return None


def extract(text):
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    fields = reader.fieldnames or []
    model_key = choose(fields, ["model", "model name", "model_name", "name"])
    lab_key = choose(fields, ["organization", "organisation", "developer", "lab", "organization name"])
    value_key = choose(fields, ["eci", "eci score", "eci_score", "general eci", "general_eci"])
    low_key = choose(fields, ["eci lower", "eci low", "eci_ci_lower", "eci_ci_low", "eci lower bound", "eci_lower", "eci 90% lower", "lower 90%", "eci 90% ci lower"])
    high_key = choose(fields, ["eci upper", "eci high", "eci_ci_upper", "eci_ci_high", "eci upper bound", "eci_upper", "eci 90% upper", "upper 90%", "eci 90% ci upper"])
    date_key = choose(fields, ["release date", "release_date", "model release date"])
    if not model_key or not value_key:
        raise ValueError("CSV column names changed; model and ECI score columns are required. Found: " + ", ".join(fields[:35]))
    found = {}
    history = []
    for row in reader:
        model = str(row.get(model_key) or "").strip()
        value = numeric(row.get(value_key))
        if not model or value is None:
            continue
        low = numeric(row.get(low_key)) if low_key else None
        high = numeric(row.get(high_key)) if high_key else None
        # Do not pretend an unreported confidence interval is real.
        if low is None or high is None or low > value or high < value:
            continue
        lab = str(row.get(lab_key) or "Not specified").strip() if lab_key else "Not specified"
        record = {"model": model, "lab": lab, "score": value, "low": low, "high": high}
        if model not in found or value > found[model]["score"]:
            found[model] = record
        if date_key:
            date_string = str(row.get(date_key) or "").strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_string):
                try:
                    if dt.date.fromisoformat(date_string) <= dt.datetime.now(UTC).date():
                        history.append({"model": model, "date": date_string, "score": value})
                except ValueError:
                    pass
    models = sorted(found.values(), key=lambda m: (-m["score"], m["model"]))
    if len(models) < 20:
        raise ValueError(f"Only {len(models)} ECI records with valid 90% intervals; refusing incomplete feed")
    scores = [r["score"] for r in models]
    if min(scores) < 1 or max(scores) > 350 or max(scores) < 100:
        raise ValueError("ECI values outside plausibility envelope; refusing update")
    unique_dates = {h["date"] for h in history}
    if len(history) < 20 or len(unique_dates) < 4:
        history = []  # Don't turn snapshot dates into a trend.
    return models, history


def main():
    original = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    data = json.loads(json.dumps(original))
    data.setdefault("ingestion", {})
    data["ingestion"]["last_attempt"] = now()
    request = urllib.request.Request(
        ECI_URL,
        headers={"User-Agent": "FrontierObservatory/1.0 (public source attribution; GitHub Actions)", "Accept": "text/csv"},
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            content_type = response.headers.get("Content-Type", "")
            size = response.headers.get("Content-Length")
            if size and int(size) > 12_000_000:
                raise ValueError("Feed unexpectedly large")
            payload = response.read(12_000_001)
            if len(payload) > 12_000_000:
                raise ValueError("Feed exceeds 12MB limit")
            if "html" in content_type:
                raise ValueError("Upstream returned HTML rather than CSV")
            raw = payload.decode("utf-8-sig")
        models, history = extract(raw)
        data["eci"]["models"] = models[:80]
        data["eci"]["history"] = history
        data["eci"]["last_successful_ingest"] = now()
        data["eci"]["last_source_date"] = dt.datetime.now(UTC).date().isoformat()
        data["eci"]["source_data_url"] = ECI_URL
        data["eci"]["source_data_license"] = "Epoch AI CC BY; verify linked external benchmark licenses for reuse"
        data["ingestion"]["last_success"] = now()
        data["ingestion"]["status"] = "success"
        data["ingestion"]["notes"] = f"Imported {len(models)} valid ECI model rows and {len(history)} release-dated observations from the linked CSV. Only the top 80 model comparisons are displayed."
        for item in data.get("sources", []):
            if item.get("name") == "Epoch Capabilities Index":
                item["last_source_date"] = dt.datetime.now(UTC).date().isoformat()
                item["mode"] = "daily official CSV"
        print(data["ingestion"]["notes"])
    except Exception as exc:
        # Keep all previously validated observations intact.
        data["ingestion"]["status"] = "failed_preserved_prior_data"
        data["ingestion"]["notes"] = "Scheduled Epoch CSV check failed; previous valid observations preserved. Reason: " + str(exc)[:260]
        print(data["ingestion"]["notes"], file=sys.stderr)
    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
