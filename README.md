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

Spotify can take up to 5 days to send your data, so start step 1 first.

### 1. Get your Spotify data

Use a web browser, not the Spotify app.

1. Go to <https://www.spotify.com/account/privacy/> and log in.
2. Scroll down to **Download your data**.
3. Select **Account data** only. You do not need "Extended streaming history" or "Technical log information".
4. Click **Request data**.
5. Open the email from Spotify and click **Confirm**. If you do not confirm, Spotify does not start.
6. Wait for a second email with the download link (up to 5 days). Download it soon, because the link stops working after some days.
7. Unzip the download (usually `my_spotify_data.zip`) and find `YourLibrary.json`.

Your export also holds your email address and listening history. Do not share it.

### 2. Install

Make a new folder, put `YourLibrary.json` in it, and open a terminal in that folder. Run one command at a time.

**Mac or Linux**

```sh
python3 -m venv .venv
```
```sh
source .venv/bin/activate
```
```sh
pip install ytmusicapi
```
```sh
curl -O https://raw.githubusercontent.com/kj-gopika/spotify-to-ytmusic/main/s2ytm.py
```

**Windows PowerShell**

```powershell
py -m venv .venv
```
```powershell
.venv\Scripts\Activate.ps1
```

If Windows blocks the last command, run this and then run the last command again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
```powershell
pip install ytmusicapi
```
```powershell
curl.exe -O https://raw.githubusercontent.com/kj-gopika/spotify-to-ytmusic/main/s2ytm.py
```

Read `s2ytm.py` before you run it. It is about 170 lines.

### 3. Find the songs (no login)

```sh
python s2ytm.py match YourLibrary.json
```

Check `matches.csv`. An empty `videoId` means no match. Delete rows you do not want. Run it again to continue after a stop.

### 4. Copy your login headers

Log in at music.youtube.com. Open developer tools → **Network**, type `browse` in the filter, and click **Library** on the page.

A copy button replaces your clipboard, so do this in order:

1. Copy the command for your computer below and paste it in the terminal. **Do not press Enter yet.**
2. In developer tools, right-click a POST `browse` request → **Copy → Copy request headers**.
3. Go back to the terminal and press Enter. This saves the headers to `headers.txt`.

**Mac**

```sh
pbpaste > headers.txt
```

**Windows PowerShell**

```powershell
Get-Clipboard | Set-Content -Encoding utf8 headers.txt
```

### 5. Make the playlist

```sh
python s2ytm.py create --name "My Spotify songs"
```

### 6. Log out

Log out of music.youtube.com in that browser so the copied cookies stop working.

## Free, always

MIT licence. No ads, no tracking, no paid version. Not made by, supported by or connected to Spotify, YouTube or Google.
