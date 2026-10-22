# Watchtower Status

Generated: `2026-10-22T04:16:28+00:00` (UTC)

**Summary:** 4 degraded, 9 operational, 1 paused

| Service | State | Cadence | Note |
|---|---|---|---|
| inbox-triage-scan | 🟢 operational | every 30m | enabled interval@30m — runs every 30 minutes |
| inbox-morning-briefing | 🟢 operational | daily 08:15 | enabled daily@08:00:00 — runs daily at 08:00 ET |
| dr-bot-daily-briefing | 🟢 operational | daily 07:11 | enabled daily@12:11:00 — runs daily |
| dr-bot-anomaly-watch | 🟢 operational | daily 21:11 | enabled daily@21:11:00 — scheduled, awaiting evening run |
| dr-bot-weekly-report | 🟢 operational | weekly Mon 08:11 | enabled weekly Mon 12:11 — runs Mondays |
| gameday-nfl-pregame | 🔴 degraded | daily 08:00 | cron job MISSING from scheduler — absent from live schedules, cron.d definition files, and _archive; no removal ordered on record |
| gameday-teams-today | 🔴 degraded | daily 09:00 | cron job MISSING from scheduler — absent from live schedules, cron.d definition files, and _archive; no removal ordered on record |
| gameday-finals | 🔴 degraded | daily 23:00 | cron job MISSING from scheduler — absent from live schedules, cron.d definition files, and _archive; no removal ordered on record |
| gameday-nfl-weekly | 🔴 degraded | weekly Tue 08:00 | cron job MISSING from scheduler — absent from live schedules, cron.d definition files, and _archive; no removal ordered on record |
| fz1073-investigation-watch | 🟢 operational | daily 08:11 | enabled daily@08:11:00 — runs daily |
| neptunesbag-poll-watch | ⏸️ paused | daily 17:11 | disabled by operator — poll closed 2026-10-11, jobs stay disabled |
| heartbeat | 🟢 operational | every 30m | enabled interval@30m, mode=heartbeat — scheduler heartbeat alive |
| estate-skills | 🟢 operational | continuous | present on disk |
| estate-memory | 🟢 operational | continuous | present on disk |

_Paused means the operator deliberately paused the service — a decision, not an outage._
