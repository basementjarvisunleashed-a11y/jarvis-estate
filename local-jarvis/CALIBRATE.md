# Voice-gate calibration — steps for HgX (about 10 minutes)
Threshold today: 0.45 (provisional). Nothing here changes it automatically.
1. Open a terminal in C:\Jarvis. Make sure the voice loop is not running.
2. `py -3.13 calibrate.py record me 8` — speak 8 normal commands: 3 close to the mic, 3 across the room, 2 quietly.
3. `py -3.13 calibrate.py record other 8` — 8 clips of other people (family/friends), a TV, and a YouTube clip of someone talking.
   Optional replay test: play a recording of your own voice from your phone for 2 of them.
4. `py -3.13 calibrate.py score` — read the HgX min, others max and the suggested threshold.
5. If happy, set `"threshold"` in C:\Jarvis\voice_gate.json to the suggestion and change `"status"` to "calibrated <date>".
   Ask Grok Bot to do step 5 if you prefer.
Clips stay in C:\Jarvis\voiceprint\calib\ and never leave the laptop.
