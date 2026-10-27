@echo off
rem Password comes from VLC Preferences (Lua HTTP), set by HgX.
start "" "C:\Program Files\VideoLAN\VLC\vlc.exe" --extraintf http --http-host 127.0.0.1 --http-port 8090 %*
