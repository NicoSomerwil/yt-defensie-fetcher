# KVEO Defensie feeds

Deze repository onderhoudt de gegevensbronnen voor de actuele Defensie-video's
en -magazines op kveo.nl.

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

De videoworkflow draait dagelijks om 07:00 UTC en commit de CSV-bestanden naar
`yt_defensie/`. De magazineworkflow controleert om 05:17 en 17:17 UTC de zes
officiële magazine-overzichten en schrijft de nieuwste edities naar
`data/defensie-magazines.json`.

Beide workflows kunnen ook handmatig worden gestart via **Actions**.

## Lokaal draaien

```bash
python yt_video_defensie_fetcher.py        # alle kanalen
python yt_video_defensie_fetcher.py kl     # alleen Landmacht
python scripts/update_magazine_feed.py      # zes magazines
```

De videofetcher gebruikt de openbare YouTube Atom-feeds. Daardoor is geen
API-sleutel of `yt-dlp` nodig.

## Output

Per kanaal staat één CSV in `yt_defensie/` met de kolommen Titel, URL,
Publicatiedatum en Kanaal. De magazinefeed staat in
`data/defensie-magazines.json`.
