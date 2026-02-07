import subprocess
import json
import csv
import sys
import os
import shutil

# Configuratie per kanaal
CHANNELS = {
    "kl": "https://www.youtube.com/@KoninklijkeLandmacht",
    "klu": "https://www.youtube.com/@KoninklijkeLuchtmachtNL",
    "km": "https://www.youtube.com/@Koninklijke-Marine",
    "kmar": "https://www.youtube.com/@koninklijkemarechaussee8093",
    "defensie": "https://www.youtube.com/@defensie",
    "werken_bij_def": "https://www.youtube.com/@werkenbijdefensie"
}

# Zoek yt-dlp: gebruik pad uit env var, of zoek automatisch
YT_DLP = os.environ.get("YT_DLP_PATH") or shutil.which("yt-dlp")

if not YT_DLP:
    print("yt-dlp niet gevonden. Installeer met: pip install yt-dlp")
    sys.exit(1)


def fetch_latest_video(channel_key):
    channel_url = CHANNELS[channel_key]

    result = subprocess.run([
        YT_DLP,
        "--dateafter", "now-1year",
        "--dump-json",
        "--playlist-end", "1",
        f"{channel_url}/videos"
    ], capture_output=True, text=True)

    if not result.stdout.strip():
        print(f"Geen video gevonden voor {channel_key}")
        return

    video_json = json.loads(result.stdout.strip())
    video_url = f"https://www.youtube.com/watch?v={video_json['id']}"

    # CSV opslaan
    csv_filename = f"yt_defensie/video_{channel_key}.csv"
    os.makedirs("yt_defensie", exist_ok=True)

    with open(csv_filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Titel", "URL", "Publicatiedatum", "Kanaal"])
        writer.writeheader()
        writer.writerow({
            "Titel": video_json.get("title"),
            "URL": video_url,
            "Publicatiedatum": video_json.get("upload_date"),
            "Kanaal": video_json.get("channel")
        })

    print(f"✅ {csv_filename} opgeslagen")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fetch_latest_video(sys.argv[1])
    else:
        for channel in CHANNELS.keys():
            fetch_latest_video(channel)
