import requests

SHEET_ID = "1iuzDTOAvdoNe8Ne8i461qGNucg5OuEoF-Ikqs8aUQZw"
TAB_NAME = "Playable Worlds"

# Open-ended range - Sheets returns everything from row 3 to the
# last populated row automatically, no need to know the exact count.
RANGE = f"'{TAB_NAME}'!A3:I"

FIELDS = "sheets.data.rowData.values(formattedValue,textFormatRuns,hyperlink)"

# Only these two schemes are ever rendered as a real <a href>. This is
# a public, community-editable spreadsheet - anyone with edit access
# could type javascript: or data: into a "link" cell, which would be
# a real XSS vector if we ever rendered it unchecked.
_ALLOWED_URL_SCHEMES = ("http://", "https://")


class SheetFetchError(Exception):
    """Raised for any failure talking to the Sheets API."""


def _extract_cell(cell: dict) -> tuple[str, list[tuple[str, str]]]:
    """
    Returns (visible_text, [(link_text, url), ...]) for one cell.

    Handles both cases the Sheets API can return:
    - A single whole-cell hyperlink -> cell["hyperlink"]
    - Multiple independently-linked words -> cell["textFormatRuns"],
      each marking where a new format (possibly incl. a link) starts;
      a run's text extends to the next run's startIndex, or the end
      of the string for the last run.
    """
    text = cell.get("formattedValue", "")
    links: list[tuple[str, str]] = []

    runs = cell.get("textFormatRuns")
    if runs:
        for i, run in enumerate(runs):
            start = run.get("startIndex", 0)
            end = runs[i + 1]["startIndex"] if i + 1 < len(runs) else len(text)
            link = run.get("format", {}).get("link")
            uri = link.get("uri") if link else None
            if uri and uri.startswith(_ALLOWED_URL_SCHEMES):
                links.append((text[start:end], uri))
    else:
        uri = cell.get("hyperlink")
        if uri and uri.startswith(_ALLOWED_URL_SCHEMES):
            links.append((text, uri))

    return text, links


def _row_values(row: dict, num_cols: int = 9) -> list[dict]:
    """Pads a row out to num_cols cells - trailing empty cells are
    just absent from the API response, same as the CSV export did."""
    values = row.get("values", [])
    return values + [{}] * (num_cols - len(values))


def fetch_dev_games(api_key: str) -> list[dict]:
    """
    Fetches and parses the Playable Worlds sheet.

    Returns a list of dicts:
        {
            "name": str,
            "stability": str,
            "notes": str,
            "is_18_plus": bool,              # column D
            "links": [(label, url), ...],   # from columns E, F, G combined
        }

    Skips any row with an empty Game name, and any row whose PR
    Status (column C) is "Core" - those are already covered by the
    real supported-games page and shouldn't be duplicated here.
    """
    if not api_key:
        raise SheetFetchError("Google Sheets API key is not configured.")

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
    params = {
        "ranges": RANGE,
        "includeGridData": "true",
        "fields": FIELDS,
        "key": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
    except requests.HTTPError as e:
        # Google's actual JSON error body has a specific reason
        # (SERVICE_DISABLED, API_KEY_SERVICE_BLOCKED, PERMISSION_DENIED,
        # etc.) - surface that instead of just the generic HTTP status,
        # which tells us nothing on its own.
        detail = None
        try:
            detail = e.response.json().get("error", {}).get("message")
        except Exception:
            pass
        raise SheetFetchError(detail or f"Could not reach Google Sheets API: {e}")
    except requests.RequestException as e:
        raise SheetFetchError(f"Could not reach Google Sheets API: {e}")

    data = response.json()

    try:
        row_data = data["sheets"][0]["data"][0].get("rowData", [])
    except (KeyError, IndexError):
        raise SheetFetchError("Unexpected response shape from Sheets API.")

    games = []

    for row in row_data:
        cells = _row_values(row)

        name, _ = _extract_cell(cells[0])
        name = name.strip()
        if not name:
            continue

        pr_status, _ = _extract_cell(cells[2])
        if pr_status.strip().lower() == "core":
            continue

        stability, _ = _extract_cell(cells[1])
        notes, _ = _extract_cell(cells[8])

        rating_text, _ = _extract_cell(cells[3])
        is_18_plus = rating_text.strip().upper() == "TRUE"

        links: list[tuple[str, str]] = []

        # Column E - Links & Downloads: keep the cell's own label(s).
        _, e_links = _extract_cell(cells[4])
        links.extend(e_links)

        # Column F - Setup Guide(s): always shown as "Setup Guide",
        # regardless of the cell's actual visible text (e.g. "Github",
        # "Website", "AP.gg").
        _, f_links = _extract_cell(cells[5])
        links.extend([("Setup Guide", url) for _, url in f_links])

        # Column G - Support: keep the cell's own label(s).
        _, g_links = _extract_cell(cells[6])
        links.extend(g_links)

        games.append({
            "name": name,
            "stability": stability.strip(),
            "notes": notes.strip(),
            "is_18_plus": is_18_plus,
            "links": links,
        })

    return games