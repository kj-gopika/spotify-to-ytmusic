# s2ytm: Spotify songs to YouTube Music

A free script that copies the saved songs in your Spotify data export (`YourLibrary.json`) to a **private** YouTube Music playlist. It runs on your own computer. No server, no sign-up, no fee.

Guide with a file checker: **https://kj-gopika.github.io/spotify-to-ytmusic/**

## Read the risks first

- **Your headers are your Google login.** The request headers you copy hold your login cookies. Anyone with them can use your account until you log out. Never paste them into a website, chat, issue or AI assistant. The script deletes `headers.txt` after it reads it and keeps the login in memory only.
- **Not an official API.** It uses [ytmusicapi](https://github.com/sigma67/ytmusicapi), which Google does not support. It can break at any time, can be against the YouTube Terms of Service, and Google can limit your account.
- **Some matches will be wrong.** Matching uses title and artist only. Check `matches.csv` before step 2.
- **Only download the script from this repository**, and read it before you run it. A changed copy can steal your cookies.
- **Song names go to YouTube** for the search. Do not share your Spotify export; it holds personal data.
- **Songs only.** Not playlists, albums, artists or podcasts.

## Steps

1. Request **Account data** at <https://www.spotify.com/account/privacy/>. Unzip it and find `YourLibrary.json`.
2. Install:
   ```sh
   python3 -m venv .venv && source .venv/bin/activate   # Windows: py -m venv .venv; .venv\Scripts\Activate.ps1
   pip install ytmusicapi
   ```
3. Find the songs (no login):
   ```sh
   python s2ytm.py match YourLibrary.json
   ```
   Check `matches.csv`. Delete rows you do not want. Rerun to continue after a stop.
4. Log in at music.youtube.com. Open developer tools → Network, filter `browse`, click **Library**, right-click a POST `browse` request → **Copy → Copy request headers**. Save them:
   ```sh
   pbpaste > headers.txt                                   # Mac
   Get-Clipboard | Set-Content -Encoding utf8 headers.txt  # Windows PowerShell
   ```
5. Make the playlist:
   ```sh
   python s2ytm.py create --name "My Spotify songs"
   ```
6. Log out of music.youtube.com in that browser so the copied cookies stop working.

## Free, always

MIT licence. No ads, no tracking, no paid version. Not made by, supported by or connected to Spotify, YouTube or Google.
