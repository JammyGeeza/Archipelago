import re
from urllib.parse import urlparse

import requests
from flask import current_app, jsonify, request
from pony.orm import db_session, select

from .. import cache
from . import api_endpoints
from ..steam_games import SteamGame  # note: this is your Postgres db, not WebHostLib/models.py's

STEAM_API_BASE = "https://api.steampowered.com"
STEAM_STORE_BASE = "https://store.steampowered.com"
STEAM_COUNTRY_CODE = "gb"

# How long a game's price/discount info is cached for, in seconds.
# This is *pricing only* - ownership is always checked live, never cached.
PRICE_CACHE_SECONDS = 1800


class SteamLookupError(Exception):
    """Raised for any Steam-side failure we want to surface to the user."""


def steam_request(url, params=None):
    try:
        response = requests.get(
            url,
            params=params,
            timeout=20,
            headers={"User-Agent": "Archipelago-SupportedGames/1.0"},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise SteamLookupError(f"Steam request failed: {e}")
    except ValueError:
        raise SteamLookupError("Steam returned an invalid JSON response.")


def resolve_user_id(user_id, api_key):
    """
    Accept:
    76561197960287930
    gaben
    https://steamcommunity.com/id/gaben
    https://steamcommunity.com/profiles/76561197960287930
    """

    user_id = str(user_id).strip()

    if re.fullmatch(r"\d{17}", user_id):
        return user_id

    if user_id.startswith("http://") or user_id.startswith("https://"):
        parsed = urlparse(user_id)

        profile_match = re.match(r"^/profiles/(\d{17})/?$", parsed.path)
        if profile_match:
            return profile_match.group(1)

        vanity_match = re.match(r"^/id/([^/]+)/?$", parsed.path)
        if vanity_match:
            user_id = vanity_match.group(1)

    vanity = user_id.strip("/")

    data = steam_request(
        f"{STEAM_API_BASE}/ISteamUser/ResolveVanityURL/v1/",
        params={"key": api_key, "vanityurl": vanity, "url_type": 1},
    )

    response = data.get("response", {})

    if response.get("success") != 1 or not response.get("steamid"):
        raise SteamLookupError("Profile not found, check your profile is public")

    return response["steamid"]


def get_owned_app_ids(steam_id, wanted_appids, api_key):
    """
    Live, uncached ownership check - fetches the account's full
    owned-games list and filters locally against wanted_appids.
    (appids_filter on Steam's side is unreliable for free-to-play
    titles, so we deliberately don't rely on it.)
    """

    data = steam_request(
        f"{STEAM_API_BASE}/IPlayerService/GetOwnedGames/v1/",
        params={
            "key": api_key,
            "steamid": steam_id,
            "include_appinfo": 1,
            "include_played_free_games": 1,
            "include_free_sub": 1,
        },
    )

    games = data.get("response", {}).get("games", [])
    owned_ids = {int(g["appid"]) for g in games if "appid" in g}

    return owned_ids & set(wanted_appids)


def _fetch_app_price_info(appid):
    """Uncached Steam Store lookup for a single AppID. Callers should
    go through get_app_price_info() instead, which adds caching."""

    data = steam_request(
        f"{STEAM_STORE_BASE}/api/appdetails",
        params={"appids": appid, "cc": STEAM_COUNTRY_CODE, "l": "english"},
    )

    app_data = data.get(str(appid))
    if not app_data or not app_data.get("success"):
        return {"is_free": False, "price_overview": None}

    details = app_data.get("data", {})
    return {
        "is_free": bool(details.get("is_free")),
        "price_overview": details.get("price_overview"),
    }


def get_app_price_info(appid):
    """Cached wrapper - pricing is identical for every visitor, so
    there's no reason to hit Steam's Store API on every single request."""

    cache_key = f"steam_price_info_{appid}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    info = _fetch_app_price_info(appid)
    cache.set(cache_key, info, timeout=PRICE_CACHE_SECONDS)
    return info


def format_price_and_sort_value(price_info):
    """
    Returns (display_price, sort_price) e.g.
    ("£19.99", 19.99)
    ("£19.99 — SALE! (-50%)", 19.99)
    ("£0.00", 0.0)
    ("Price unavailable", float("inf"))
    """

    if price_info.get("is_free"):
        return "£0.00", 0.0

    price = price_info.get("price_overview")
    if not price:
        return "Price unavailable", float("inf")

    if price.get("currency") != "GBP":
        currency = price.get("currency") or "unknown currency"
        return f"Price unavailable (Steam returned {currency})", float("inf")

    final_price = price.get("final")
    if final_price is None:
        return "Price unavailable", float("inf")

    pounds = final_price / 100
    display = f"£{pounds:,.2f}"

    discount = price.get("discount_percent", 0)
    if discount and discount > 0:
        display += f" — SALE! (-{discount}%)"

    return display, pounds


def steam_store_url(appid):
    return f"{STEAM_STORE_BASE}/app/{appid}/"


@db_session
def get_game_records():
    """Returns {game_name: {"platform": ..., "steam_appid": ...}} for
    every mapped AP world (Steam, emulator, or itch.io)."""
    return {
        row.game_name: {"platform": row.platform, "steam_appid": row.steam_appid}
        for row in select(g for g in SteamGame)
    }


@api_endpoints.route("/steam_ownership", methods=["POST"])
def steam_ownership():
    api_key = current_app.config.get("STEAM_API_KEY")
    if not api_key:
        return jsonify(success=False, error="Steam integration is not configured on this server."), 500

    body = request.get_json(silent=True) or {}
    user = (body.get("user") or "").strip()

    if not user:
        return jsonify(success=False, error="No Steam UserID or vanity name provided."), 400

    game_records = get_game_records()

    # Only 'steam' platform rows ever need a live Steam call -
    # emulator/itch rows are resolved from the DB alone.
    unique_appids = {
        record["steam_appid"]
        for record in game_records.values()
        if record["platform"] == "steam" and record["steam_appid"] is not None
    }

    try:
        steam_id = resolve_user_id(user, api_key)
        owned_appids = get_owned_app_ids(steam_id, unique_appids, api_key)
    except SteamLookupError as e:
        return jsonify(success=False, error=str(e)), 200

    results = {}

    for game_name, record in game_records.items():
        platform = record["platform"]

        if platform == "emulator":
            results[game_name] = {"status": "emulator"}
            continue

        if platform == "itch":
            results[game_name] = {"status": "itch"}
            continue

        if platform == "native":
            # Free AP-community download (e.g. APdoku) - anyone can
            # grab it, so it belongs in the same group as owned/
            # free-to-play Steam games, not its own tier.
            results[game_name] = {"status": "owned"}
            continue

        # platform == "steam"
        appid = record["steam_appid"]

        if appid in owned_appids:
            results[game_name] = {"status": "owned"}
            continue

        # Free-to-play games don't generate a normal ownership
        # record - anyone can install and play them, so treat them
        # as owned rather than showing a price for something free.
        price_info = get_app_price_info(appid)
        if price_info.get("is_free"):
            results[game_name] = {"status": "owned"}
            continue

        display_price, sort_price = format_price_and_sort_value(price_info)
        results[game_name] = {
            "status": "not_owned",
            "price": display_price,
            "sortPrice": sort_price,
            "url": steam_store_url(appid),
        }

    return jsonify(success=True, games=results)