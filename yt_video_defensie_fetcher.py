import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request, urlopen


CHANNELS = {
    "kl": "UCHiehyVZFy4mlNas4g3HCrQ",
    "klu": "UCXlJaY7qJcoyNUnrfTvfV5Q",
    "km": "UCXDl9qGTjAwhF2pvFPzaHOA",
    "kmar": "UCRUc0CWOU3fFF_A20A6BN4g",
    "defensie": "UC2Sxy2Y43M79hKw-nmJl1YQ",
    "werken_bij_def": "UCKvLISFSRyOe6WS_Yrmphfw",
}
OUTPUT_DIR = Path(__file__).resolve().parent / "yt_defensie"
ATOM = "http://www.w3.org/2005/Atom"
YT = "http://www.youtube.com/xml/schemas/2015"


def fetch_latest_video(channel_key: str) -> None:
    channel_id = CHANNELS[channel_key]
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    request = Request(feed_url, headers={"User-Agent": "KVEO video feed updater/2.0 (+https://kveo.nl)"})
    with urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())

    entry = root.find(f"{{{ATOM}}}entry")
    if entry is None:
        raise RuntimeError(f"Geen video gevonden voor {channel_key} ({channel_id})")

    video_id = entry.findtext(f"{{{YT}}}videoId")
    title = entry.findtext(f"{{{ATOM}}}title")
    published = entry.findtext(f"{{{ATOM}}}published")
    author = entry.find(f"{{{ATOM}}}author")
    channel = author.findtext(f"{{{ATOM}}}name") if author is not None else ""
    if not video_id or not title or not published:
        raise RuntimeError(f"Onvolledige feed voor {channel_key} ({channel_id})")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"video_{channel_key}.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Titel", "URL", "Publicatiedatum", "Kanaal"])
        writer.writeheader()
        writer.writerow(
            {
                "Titel": title,
                "URL": f"https://www.youtube.com/watch?v={video_id}",
                "Publicatiedatum": published[:10].replace("-", ""),
                "Kanaal": channel,
            }
        )
    print(f"{output.relative_to(Path(__file__).resolve().parent)} opgeslagen")


def main() -> None:
    requested = sys.argv[1:] or list(CHANNELS)
    unknown = [key for key in requested if key not in CHANNELS]
    if unknown:
        raise SystemExit(f"Onbekende kanaalsleutel(s): {', '.join(unknown)}")
    for channel_key in requested:
        fetch_latest_video(channel_key)


if __name__ == "__main__":
    main()
