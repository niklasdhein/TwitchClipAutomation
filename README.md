# TwitchClipAutomation

Automatisierte End-to-End Pipeline in Python, um Twitch-Clips (16:9) mit Computer Vision und automatischer Spracherkennung in modernes 9:16 Vertical Video (TikTok / YouTube Shorts / Reels) umzuwandeln.

---

## Features

- **Clip-Downloader:** Abruf und Download Clips ausgewählter Twitch-Kanäle via `twitch-dl`.
- **Computer Vision Face Tracking:** Erkennt Gesichter und Augenpositionen mittels Haar-Cascade-Klassifikatoren (`OpenCV`), um den relevanten Bereich im Bild zu verfolgen.
- **Smart Cropping (9:16):** Schneidet das 16:9-Ausgangsmaterial zentriert auf das getrackte Gesicht zu und hält das Motiv im vertikalen Fokus (`MoviePy`).
- **Modulare Pipeline:** Alle Schritte können eigenständig oder als zusammenhängende Pipeline ausgeführt werden.

---

## Pipeline-Architektur

```text
[ Twitch Channel ]
        │
        ▼ (twitch_clip_downloader.py)
[ Heruntergeladene Clips (16:9) ]
        │
        ├──► [ face_tracker.py ] ──► Gesichts- & Augenkoordinaten (XML)
        │                                       │
        ▼                                       ▼
 [ pipeline.py ] ◄────────────────── [ cropper.py ] (9:16 Zuschnitt)
        │
        ▼
[ Fertiges Kurzvideo (9:16 MP4) in exported_clips/ ]
```

---

## Voraussetzungen

- **Python 3.10+**
- **FFmpeg** (für Video- und Audiokomposition durch MoviePy)
- **twitch-dl** CLI-Tool (`pip install twitch-dl`)
- **AssemblyAI Account:** Kostenloser API-Key für die Spracherkennung

---

## Installation & Setup

1. **Repository klonen:**
   ```bash
   git clone https://github.com/niklasdhein/TwitchClipAutomation.git
   cd TwitchClipAutomation
   ```

2. **Virtuelle Umgebung anlegen & Abhängigkeiten installieren:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **API-Key konfigurieren:**
   Setze AssemblyAI API-Key als Umgebungsvariable:
   ```bash
   export ASSEMBLYAI_API_KEY="dein_assemblyai_api_key"
   ```
   *Alternativ kann der Key direkt in `subtitle_creator.py` als Fallback eingetragen werden.*

---

## Verwendung

### Gesamte Pipeline starten:
```bash
python pipeline.py
```
1. Gib den/die Twitch-Kanalnamen ein (getrennt durch Leerzeichen).
2. Die Pipeline lädt die Clips herunter, analysiert die Gesichter, schneidet die Videos auf 9:16 zu und speichert die finalen Videos in `exported_clips/`.

### Einzelne Module ausführen:
- **Nur Clips herunterladen:** `python twitch_clip_downloader.py`
- **Face-Tracking manuell anwenden:** `tracker.face_tracker_handler()`
- **Zuschnitt oder Untertitel testen:** Siehe jeweilige Handler-Funktionen in `cropper.py` und `subtitle_creator.py`.

---

## Projektstruktur

```text
.
├── cropper.py                 # Berechnet und schneidet 9:16 Subclips anhand der Trackingdaten
├── face_tracker.py            # OpenCV-basiertes Face- & Eye-Tracking zur Koordinatenerfassung
├── pipeline.py                # Haupt-Orchestrator der gesamten Automatisierungspipeline
├── subtitle_creator.py        # AssemblyAI-Transkription & Erzeugung visueller Untertitel
├── twitch_clip_downloader.py  # Abruf & Download von Twitch-Clips
├── requirements.txt           # Python-Abhängigkeiten
└── README.md                  # Projektdokumentation
```
