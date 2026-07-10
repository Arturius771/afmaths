from pathlib import Path

import requests

SPACE_TRACK_BASE_URL = "https://www.space-track.org"
SECRETS_FILE = Path(__file__).with_name("secrets.txt")


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


def get_tle_from_norad_id(norad_id: int) -> str:
    secrets = load_secrets()

    username = secrets["SPACE_TRACK_USERNAME"]
    password = secrets["SPACE_TRACK_PASSWORD"]

    login_url = f"{SPACE_TRACK_BASE_URL}/ajaxauth/login"
    tle_url = (
        f"{SPACE_TRACK_BASE_URL}/basicspacedata/query"
        f"/class/gp"
        f"/NORAD_CAT_ID/{norad_id}"
        f"/format/tle"
    )

    with requests.Session() as session:
        login_response = session.post(
            login_url,
            data={
                "identity": username,
                "password": password,
            },
            timeout=30,
        )
        login_response.raise_for_status()

        tle_response = session.get(tle_url, timeout=30)
        tle_response.raise_for_status()

        if "You must be logged in" in tle_response.text:
            raise RuntimeError("Space-Track authentication failed")

        tle = tle_response.text.strip()

        if not tle:
            raise ValueError(f"No TLE found for NORAD ID {norad_id}")

        return tle


if __name__ == "__main__":
    print(get_tle_from_norad_id(25544))
