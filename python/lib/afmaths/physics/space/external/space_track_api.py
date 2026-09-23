from __future__ import annotations

import os
import time
from pathlib import Path

import requests

from afmaths.constants import SECONDS_PER_HOUR
from afmaths.physics.space.external.http_helpers import build_url, send_request

SPACE_TRACK_BASE_URL = "https://www.space-track.org"

LOGIN_URL = build_url(
    SPACE_TRACK_BASE_URL,
    "ajaxauth",
    "login",
)

SPACE_TRACK_QUERY_URL = build_url(
    SPACE_TRACK_BASE_URL,
    "basicspacedata",
    "query",
)

# Newest GP TLE for each active object with an epoch within the last
# 10 days and a catalogue number representable by the TLE/Alpha-5 format.
GP_UPDATES_URL = build_url(
    SPACE_TRACK_QUERY_URL,
    "class",
    "gp",
    "NORAD_CAT_ID",
    "%3C340000",
    "decay_date",
    "null-val",
    "epoch",
    "%3Enow-10",
    "format",
    "tle",
)

SECRETS_FILE = Path(__file__).with_name("secrets.txt")
TLE_CACHE_FILE = Path(__file__).with_name("tle_cache.tle")
LAST_GP_REQUEST_FILE = Path(__file__).with_name("last_gp_request.txt")
LAST_REFRESH_FILE = Path(__file__).with_name("last_tle_cache_refresh.txt")

MINIMUM_GP_REQUEST_INTERVAL_SECONDS = SECONDS_PER_HOUR
MINIMUM_REFRESH_INTERVAL_SECONDS = SECONDS_PER_HOUR * 2

# Alpha-5 omits I and O.
ALPHA_5_PREFIXES = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def load_secrets() -> dict[str, str]:
    secrets: dict[str, str] = {}

    for line in SECRETS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        key, separator, value = line.partition("=")

        if not separator:
            raise ValueError(f"Invalid secrets line: {line!r}")

        secrets[key.strip()] = value.strip()

    return secrets


def norad_id_from_tle_field(field: str) -> int:
    """
    Parse a NORAD catalogue field.

    Examples:
        "25544" -> 25544
        "602" -> 602
        "A0000" -> 100000
        "J0000" -> 180000
    """
    field = field.strip()

    if field.isdigit():
        return int(field)

    if len(field) != 5:
        raise ValueError(f"Invalid NORAD catalogue field: {field!r}")

    prefix = field[0]
    suffix = field[1:]

    if prefix not in ALPHA_5_PREFIXES or not suffix.isdigit():
        raise ValueError(f"Invalid Alpha-5 NORAD field: {field!r}")

    prefix_value = ALPHA_5_PREFIXES.index(prefix) + 10

    return prefix_value * 10_000 + int(suffix)


def norad_id_from_tle_line(line: str) -> int:
    """
    Extract the NORAD catalogue number from a TLE line.

    The catalogue number is parsed from whitespace-separated fields rather
    than relying on a fixed character slice, since Space-Track may return
    unpadded numeric catalogue numbers.
    """
    fields = line.split()

    if len(fields) < 2:
        raise ValueError(f"Invalid TLE data line: {line!r}")

    if line.startswith("1 "):
        catalogue_and_classification = fields[1]

        if len(catalogue_and_classification) < 2:
            raise ValueError(f"Invalid TLE line 1: {line!r}")

        # TLE line 1 stores the classification immediately after the
        # catalogue number, e.g. "25544U" or "A0000U".
        catalogue_field = catalogue_and_classification[:-1]

    elif line.startswith("2 "):
        catalogue_field = fields[1]

    else:
        raise ValueError(f"Not a TLE data line: {line!r}")

    return norad_id_from_tle_field(catalogue_field)


def parse_tles(tle_text: str) -> dict[int, str]:
    """
    Parse Space-Track TLE output into:

        {norad_id: "line 1\\nline 2"}

    Non-TLE lines, such as optional object-name lines, are ignored.
    """
    lines = [line.rstrip() for line in tle_text.splitlines() if line.strip()]

    parsed: dict[int, str] = {}
    index = 0

    while index < len(lines):
        line_1 = lines[index]

        if not line_1.startswith("1 "):
            index += 1
            continue

        if index + 1 >= len(lines):
            raise ValueError("TLE line 1 has no corresponding line 2")

        line_2 = lines[index + 1]

        if not line_2.startswith("2 "):
            raise ValueError(f"Expected TLE line 2 after {line_1!r}, found {line_2!r}")

        line_1_norad_id = norad_id_from_tle_line(line_1)
        line_2_norad_id = norad_id_from_tle_line(line_2)

        if line_1_norad_id != line_2_norad_id:
            raise ValueError(
                "TLE catalogue numbers do not match: "
                f"{line_1_norad_id} != {line_2_norad_id}"
            )

        parsed[line_1_norad_id] = f"{line_1}\n{line_2}"
        index += 2

    if tle_text.strip() and not parsed:
        raise ValueError("Response contained no valid TLE pairs")

    return parsed


def ensure_tle_cache_exists() -> None:
    """
    Create an empty cache file if it does not yet exist.
    """
    TLE_CACHE_FILE.touch(exist_ok=True)


def load_tle_cache() -> dict[int, str]:
    ensure_tle_cache_exists()
    return parse_tles(TLE_CACHE_FILE.read_text(encoding="utf-8"))


def write_tle_cache(tles: dict[int, str]) -> None:
    """
    Atomically replace the cache so readers never see a partially written
    file.
    """
    cache_contents = "\n".join(tle for _, tle in sorted(tles.items()))

    if cache_contents:
        cache_contents += "\n"

    temporary_file = TLE_CACHE_FILE.with_suffix(".tmp")
    temporary_file.write_text(cache_contents, encoding="utf-8")
    os.replace(temporary_file, TLE_CACHE_FILE)


def timestamp_from_file(timestamp_file: Path) -> float | None:
    if not timestamp_file.exists():
        return None

    try:
        return float(timestamp_file.read_text(encoding="utf-8").strip())
    except ValueError as error:
        raise ValueError(f"Invalid timestamp in {timestamp_file}") from error


def write_timestamp(timestamp_file: Path, timestamp: float) -> None:
    timestamp_file.write_text(
        str(timestamp),
        encoding="utf-8",
    )


def last_gp_request_time() -> float | None:
    return timestamp_from_file(LAST_GP_REQUEST_FILE)


def last_refresh_time() -> float | None:
    return timestamp_from_file(LAST_REFRESH_FILE)


def gp_request_is_allowed(now: float) -> bool:
    """
    Return whether another Space-Track GP request may be made.
    """
    last_request = last_gp_request_time()

    if last_request is None:
        return True

    return now - last_request >= MINIMUM_GP_REQUEST_INTERVAL_SECONDS


def refresh_is_due(now: float) -> bool:
    last_refresh = last_refresh_time()

    if last_refresh is None:
        return True

    return now - last_refresh >= MINIMUM_REFRESH_INTERVAL_SECONDS


def record_gp_request_time(request_time: float) -> None:
    write_timestamp(LAST_GP_REQUEST_FILE, request_time)


def record_refresh_time(refresh_time: float) -> None:
    write_timestamp(LAST_REFRESH_FILE, refresh_time)


def authenticated_session() -> requests.Session:
    secrets = load_secrets()
    session = requests.Session()

    try:
        send_request(
            "POST",
            LOGIN_URL,
            session=session,
            data={
                "identity": secrets["SPACE_TRACK_USERNAME"],
                "password": secrets["SPACE_TRACK_PASSWORD"],
            },
            timeout=30,
        )
    except Exception:
        session.close()
        raise

    return session


def refresh_tle_cache() -> int:
    """
    Fetch current GP TLEs and merge them into the local cache.

    If the cache does not need refreshing, or another Space-Track GP request
    is not yet permitted, no request is made and zero is returned.

    The existing cache therefore remains usable between refreshes.
    """
    ensure_tle_cache_exists()

    request_time = time.time()

    if not refresh_is_due(request_time):
        return 0

    if not gp_request_is_allowed(request_time):
        return 0

    with authenticated_session() as session:
        # Record the request before sending it. This prevents an immediate
        # retry from violating the API limit if the request, response parsing,
        # or cache update later fails.
        record_gp_request_time(request_time)

        response = send_request(
            "GET",
            GP_UPDATES_URL,
            session=session,
            timeout=60,
        )

        if "You must be logged in" in response.text:
            raise RuntimeError("Space-Track authentication failed")

        updated_tles = parse_tles(response.text)

    cached_tles = load_tle_cache()
    cached_tles.update(updated_tles)
    write_tle_cache(cached_tles)

    # Only mark the refresh as completed after the cache has been
    # successfully written.
    record_refresh_time(time.time())

    return len(updated_tles)


def get_tle_from_norad_id(norad_id: int) -> str:
    """
    Return a TLE from the local cache.

    This function performs no network request.
    """
    cached_tles = load_tle_cache()

    try:
        return cached_tles[norad_id]
    except KeyError as error:
        raise ValueError(f"No cached TLE found for NORAD ID {norad_id}") from error


if __name__ == "__main__":
    updated_count = refresh_tle_cache()

    print(f"Merged {updated_count} updated TLE(s) into {TLE_CACHE_FILE}")
