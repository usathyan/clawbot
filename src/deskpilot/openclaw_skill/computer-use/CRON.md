# DeskPilot Cron Configuration

> Cron defines scheduled tasks that run at specific times. Unlike heartbeat (periodic monitoring), cron tasks execute actions on a schedule regardless of conditions.

---

## Cron Format Reference

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, 0=Sunday)
│ │ │ │ │
* * * * * command
```

**Common Patterns:**
- `0 9 * * 1-5` = 9 AM, weekdays only
- `*/15 * * * *` = Every 15 minutes
- `0 0 * * 0` = Midnight on Sundays
- `30 8,17 * * *` = 8:30 AM and 5:30 PM daily

---

## Scheduled Tasks

### Morning Startup

```yaml
task: morning_startup
schedule: "0 9 * * 1-5"  # 9 AM weekdays
enabled: true
description: "Prepare workspace for the day"
actions:
  - name: "Launch primary apps"
    steps:
      - launch: "Slack"
      - launch: "VS Code"
      - launch: "Chrome"
      - wait: 5000  # Let apps fully load

  - name: "Arrange windows"
    steps:
      - hotkey: ["super", "left"]  # VS Code to left half
      - click_app: "Chrome"
      - hotkey: ["super", "right"]  # Chrome to right half

  - name: "Open daily standup"
    steps:
      - focus: "Chrome"
      - hotkey: ["ctrl", "t"]  # New tab
      - type: "jira.atlassian.net/board"
      - press: "enter"
```

### End of Day Cleanup

```yaml
task: end_of_day
schedule: "0 18 * * 1-5"  # 6 PM weekdays
enabled: false  # Enable when ready
description: "Daily cleanup and status save"
actions:
  - name: "Save work state"
    steps:
      - screenshot: "~/Desktop/screenshots/eod-{date}.png"
      - focus: "VS Code"
      - hotkey: ["ctrl", "shift", "s"]  # Save all

  - name: "Clear transient files"
    steps:
      - execute: "rm -f ~/Downloads/*.tmp"
      - execute: "rm -f ~/Desktop/Screenshot*.png"

  - name: "Status report"
    steps:
      - execute: "deskpilot status > ~/logs/status-{date}.txt"
```

### Periodic Screenshot Archive

```yaml
task: screenshot_archive
schedule: "0 */2 * * 1-5"  # Every 2 hours on weekdays
enabled: false
description: "Capture periodic screenshots for work log"
actions:
  - name: "Capture current state"
    steps:
      - screenshot: "~/archive/screenshots/{datetime}.png"
      - log: "Captured screenshot at {datetime}"
```

### Weekly Maintenance

```yaml
task: weekly_maintenance
schedule: "0 10 * * 0"  # Sunday 10 AM
enabled: false
description: "Weekly system maintenance tasks"
actions:
  - name: "Clear old logs"
    steps:
      - execute: "find ~/logs -mtime +30 -delete"

  - name: "Update memory archive"
    steps:
      - execute: "deskpilot memory-archive"

  - name: "Generate weekly summary"
    steps:
      - execute: "deskpilot summary --week > ~/reports/week-{week}.md"
```

---

## Custom Tasks

### Template

```yaml
task: custom_task_name
schedule: "cron expression"
enabled: false  # Set to true when tested
description: "What this task does"
timeout: 300  # Max seconds before task is killed
retry: 0  # Number of retries on failure
notify_on_failure: true  # Alert if task fails
actions:
  - name: "Step name"
    steps:
      - action: "parameter"
```

### Available Actions

| Action | Parameters | Description |
|--------|------------|-------------|
| `launch` | app name | Launch application |
| `focus` | app name | Bring app to foreground |
| `click` | x, y | Click at coordinates |
| `click_app` | app name | Click on app in taskbar/dock |
| `type` | text | Type text |
| `press` | key | Press single key |
| `hotkey` | [keys] | Press key combination |
| `screenshot` | path | Capture screenshot |
| `wait` | ms | Pause execution |
| `execute` | command | Run shell command |
| `log` | message | Write to log file |
| `notify` | message | Send notification |

### Path Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `{date}` | 2024-01-25 | Current date |
| `{datetime}` | 2024-01-25_14-30-00 | Date and time |
| `{week}` | 2024-W04 | ISO week number |
| `{user}` | john | Username |

---

## Task Dependencies

```yaml
task: dependent_task
schedule: "0 9 * * 1-5"
depends_on:
  - task: "morning_startup"
    status: "success"
actions:
  # Only runs if morning_startup succeeded
```

---

## Error Handling

### Per-Task Settings

```yaml
task: risky_task
on_error:
  action: notify  # notify | retry | ignore | stop_all
  max_retries: 3
  retry_delay: 60  # seconds between retries
  notify_channels: ["desktop", "slack"]  # where to send alerts
```

### Global Settings

```yaml
cron:
  global_timeout: 600  # Default max task duration
  log_file: "~/logs/deskpilot-cron.log"
  notify_on_any_failure: false  # Only notify for critical tasks
```

---

## Testing Cron Tasks

Before enabling a scheduled task, test it manually:

```bash
# Test a specific task
deskpilot cron run morning_startup --dry-run

# Test with actual execution
deskpilot cron run morning_startup

# Check cron log
deskpilot cron log --last 10
```

---

## Integration Notes

### With USER.md
- Tasks respect working hours unless explicitly marked `ignore_quiet_hours: true`
- Notifications follow USER.md preferences
- Sensitive apps trigger confirmation even in cron (can override with `force: true`)

### With MEMORY.md
- Task completions logged to session logs
- Failures recorded for pattern analysis
- Custom task results can be saved to memory

### With HEARTBEAT.md
- Cron handles scheduled execution
- Heartbeat handles conditional monitoring
- Don't duplicate: use cron for "do X at Y time", heartbeat for "alert me when Z happens"

---

## Disable All Cron Tasks

```yaml
cron:
  enabled: false
```

Or disable individual tasks by setting `enabled: false`.
