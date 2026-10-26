# Watchtower Status

Generated: `2026-10-26T05:14:45+00:00` (UTC)

**Summary:** 13 operational, 1 paused

| Service | State | Cadence | Note |
|---|---|---|---|
| inbox-triage-scan | 🟢 operational | every 30m | cron enabled, interval@30m |
| inbox-morning-briefing | 🟢 operational | daily 08:15 | cron enabled, daily@08:00:00 |
| dr-bot-daily-briefing | 🟢 operational | daily 07:11 | cron enabled, daily@12:11:00 |
| dr-bot-anomaly-watch | 🟢 operational | daily 21:11 | cron enabled, daily@21:11:00 |
| dr-bot-weekly-report | 🟢 operational | weekly Mon 08:11 | cron enabled, weekly@Mon-12:11:00 |
| gameday-nfl-pregame | 🟢 operational | daily 08:00 | cron enabled, daily@08:11:00 |
| gameday-teams-today | 🟢 operational | daily 09:00 | cron enabled, daily@09:11:00 |
| gameday-finals | 🟢 operational | daily 23:00 | cron enabled, daily@23:11:00 |
| gameday-nfl-weekly | 🟢 operational | weekly Tue 08:00 | cron enabled, weekly@Tue-08:11:00 |
| fz1073-investigation-watch | 🟢 operational | daily 08:11 | cron enabled, daily@08:11:00 |
| neptunesbag-poll-watch | ⏸️ paused | daily 17:11 | cron disabled — paused by operator; poll closed 2026-10-11 |
| heartbeat | 🟢 operational | every 30m | cron enabled, interval@30m |
| estate-skills | 🟢 operational | continuous | present on disk |
| estate-memory | 🟢 operational | continuous | present on disk |

_Paused means the operator deliberately paused the service — a decision, not an outage._
