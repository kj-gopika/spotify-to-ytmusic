"""Copy the saved songs in your Spotify data export to a private YouTube Music playlist.

Step 1 (no login):  python s2ytm.py match YourLibrary.json
Step 2 (login):     python s2ytm.py create

Free and open source (MIT). Runs only on your computer.
"""
import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

try:
    import ytmusicapi
    from ytmusicapi import YTMusic
except ImportError:
    sys.exit("Install the one dependency first:  pip install ytmusicapi")

MATCHES = Path("matches.csv")
HEADERS = Path("headers.txt")
FIELDS = ["artist", "track", "album", "videoId", "yt_title", "yt_artist"]


# ---------- matching ----------

def norm(s):
    return re.sub(r"[^\w]", "", s.lower())


def core_title(t):
    """'Song (From "Film") - Remastered' -> 'song'"""
    return norm(re.split(r" - |\(|\[", t)[0]) or norm(t)


def is_match(track, artist, result):
    title = result.get("title") or ""
    yt_artists = ", ".join(a["name"] for a in result.get("artists") or [])
    c, y = core_title(track), norm(title)
    title_ok = bool(c) and (c in y or (core_title(title) and core_title(title) in c))
    a = norm(artist.split(",")[0])
    artist_ok = bool(a) and a in norm(yt_artists + title)
    return title_ok and artist_ok and bool(result.get("videoId"))


def find(yt, track, artist):
    for kind in ("songs", "videos"):
        for r in yt.search(f"{track} {artist}", filter=kind, limit=10)[:10]:
            if is_match(track, artist, r):
                names = ", ".join(a["name"] for a in r.get("artists") or [])
                return r["videoId"], r.get("title", ""), names
        time.sleep(0.3)
    return None


def load_songs(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    tracks = data.get("tracks") if isinstance(data, dict) else None
    if not tracks:
        sys.exit(f"No 'tracks' list in {path}. Use YourLibrary.json from your Spotify export.")
    seen, songs = set(), []
    for t in tracks:
        if not str(t.get("uri", "")).startswith("spotify:track:"):
            continue  # only songs: skip episodes, local files
        key = (t["artist"].lower(), t["track"].lower())
        if key not in seen:
            seen.add(key)
            songs.append(t)
    return songs


def save(rows):
    with MATCHES.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)


def match(library):
    songs = load_songs(library)
    done = {}
    if MATCHES.exists():  # resume an earlier run
        done = {(r["artist"], r["track"]): r for r in csv.DictReader(MATCHES.open(encoding="utf-8"))}
    print(f"{len(songs)} songs. Searching YouTube Music (no login needed)...")
    yt, rows = YTMusic(), []
    for i, s in enumerate(songs, 1):
        old = done.get((s["artist"], s["track"]))
        if old is not None:
            rows.append(old)
            continue
        row = dict(artist=s["artist"], track=s["track"], album=s.get("album", ""),
                   videoId="", yt_title="", yt_artist="")
        try:
            hit = find(yt, s["track"], s["artist"])
        except Exception as e:  # network hiccup: leave it empty, rerun later
            print(f"  error on {s['track']}: {e}")
            hit = None
        if hit:
            row["videoId"], row["yt_title"], row["yt_artist"] = hit
        rows.append(row)
        print(f"[{i}/{len(songs)}] {s['track']} - {s['artist']}  ->  {row['yt_title'] or 'not found'}")
        if i % 25 == 0:
            save(rows)
    save(rows)
    found = sum(1 for r in rows if r["videoId"])
    print(f"\nFound {found} of {len(rows)}. Check {MATCHES} (empty videoId = not found).")
    print("Next: python s2ytm.py create")


# ---------- login + playlist ----------

def parse_headers(text):
    """Accept Chrome's 'name' / 'value' on separate lines, or 'name: value' lines."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    pairs = {}
    if sum(": " in l for l in lines) > len(lines) / 2:
        for l in lines:
            k, _, v = l.partition(": ")
            pairs[k.strip().lower()] = v.strip()
    else:
        for k, v in zip(lines[0::2], lines[1::2]):
            pairs[k.rstrip(":").lower()] = v
    keep = ("cookie", "authorization", "x-goog-authuser", "accept-language")
    missing = [k for k in ("cookie", "x-goog-authuser") if k not in pairs]
    if missing:
        sys.exit(f"headers.txt is missing: {', '.join(missing)}. Copy the headers of a 'browse' POST request.")
    pairs.setdefault("authorization", "SAPISIDHASH x")  # ytmusicapi recomputes it from the cookie
    return "\n".join(f"{k}: {pairs[k]}" for k in keep if k in pairs)


def create(name):
    if not MATCHES.exists():
        sys.exit("Run step 1 first:  python s2ytm.py match YourLibrary.json")
    if not HEADERS.exists():
        sys.exit("Save your request headers in headers.txt first (see the guide).")
    try:
        auth = json.loads(ytmusicapi.setup(headers_raw=parse_headers(HEADERS.read_text(encoding="utf-8-sig"))))
        yt = YTMusic(auth)  # kept in memory only, never written to disk
        yt.get_library_playlists(limit=1)  # fails fast if the login is wrong
    finally:
        HEADERS.unlink(missing_ok=True)
        print("Deleted headers.txt.")

    ids = [r["videoId"] for r in csv.DictReader(MATCHES.open(encoding="utf-8")) if r["videoId"]]
    ids = list(dict.fromkeys(ids))
    pid = yt.create_playlist(name, "Copied from my Spotify library with s2ytm", privacy_status="PRIVATE")
    if not isinstance(pid, str):
        sys.exit(f"Could not create the playlist: {pid}")
    for i in range(0, len(ids), 50):
        yt.add_playlist_items(pid, ids[i:i + 50], duplicates=False)
        print(f"Added {min(i + 50, len(ids))}/{len(ids)}")
        time.sleep(1)
    print(f"\nDone. Private playlist: https://music.youtube.com/playlist?list={pid}")
    print("Now log out of music.youtube.com in the browser you copied the headers from.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("match", help="find each song on YouTube Music (no login)")
    m.add_argument("library", help="path to YourLibrary.json")
    c = sub.add_parser("create", help="make the private playlist (needs headers.txt)")
    c.add_argument("--name", default="Spotify Liked Songs")
    a = p.parse_args()
    match(a.library) if a.cmd == "match" else create(a.name)


if __name__ == "__main__":
    main()
