# YouTube Defensie Video Fetcher

Haalt automatisch de laatste video op van 6 Nederlandse Defensie YouTube-kanalen en slaat ze op als CSV.

## Kanalen

| Key | Kanaal |
|-----|--------|
| kl | Koninklijke Landmacht |
| klu | Koninklijke Luchtmacht |
| km | Koninklijke Marine |
| kmar | Koninklijke Marechaussee |
| defensie | Defensie |
| werken_bij_def | Werken bij Defensie |

## Automatisch (GitHub Actions)

De workflow draait dagelijks om 07:00 UTC en commit de CSV-bestanden naar `yt_defensie/`.

Handmatig starten: **Actions** → **Fetch Defensie YouTube Videos** → **Run workflow**

## Lokaal draaien

```bash
pip install yt-dlp
python yt_video_defensie_fetcher.py        # alle kanalen
python yt_video_defensie_fetcher.py kl     # alleen Landmacht
```

## Output

Per kanaal een CSV in `yt_defensie/` met kolommen: Titel, URL, Publicatiedatum, Kanaal.
