@echo off
rem Password comes from VLC Preferences (Lua HTTP), set by the operator.
start "" "C:\Program Files\VideoLAN\VLC\vlc.exe" --extraintf http --http-host localhost --http-port 8090 %*
