# DeskPilot Heartbeat Configuration

> Heartbeat defines periodic checks where DeskPilot proactively monitors conditions and alerts you when something warrants attention. This is different from cron (scheduled tasks) - heartbeat is about awareness, not execution.

---

## Heartbeat Settings

**Interval:** 15 minutes (during working hours)
**Quiet Hours:** Outside USER.md working hours
**Notification Method:** Desktop notification (or configured channel)

---

## Active Monitors

### System Health

```yaml
monitor: system_resources
enabled: true
conditions:
  - cpu_usage > 90% for 5 minutes
  - memory_usage > 85%
  - disk_space < 10GB on primary drive
action: notify
priority: high
message_template: "System alert: {condition} - consider closing unused apps"
```

### Application State

```yaml
monitor: application_state
enabled: true
checks:
  - name: "Ollama running"
    command: "pgrep ollama"
    expected: "process exists"
    on_failure: "Ollama is not running. DeskPilot automation will fail."
    priority: high

  - name: "Docker healthy"
    command: "docker info"
    expected: "no errors"
    on_failure: "Docker is not responding. Container-based tasks unavailable."
    priority: medium
```

### Workspace State

```yaml
monitor: workspace_state
enabled: true
checks:
  - name: "Too many browser tabs"
    condition: "chrome tab count > 30"
    action: notify
    message: "You have {count} Chrome tabs open. Consider closing unused tabs."
    priority: low

  - name: "Unsaved work detection"
    condition: "VS Code has unsaved files for > 30 minutes"
    action: notify
    message: "You have unsaved changes in VS Code: {files}"
    priority: medium
```

---

## Workflow Monitors

### Communication

```yaml
monitor: communication
enabled: false  # Enable in USER.md if desired
checks:
  - name: "Unread Slack DMs"
    condition: "slack dm badge > 0"
    cooldown: 30 minutes  # Don't re-notify within this period
    action: notify
    message: "You have unread Slack DMs"
    priority: medium

  - name: "Email requiring response"
    condition: "email flagged and older than 4 hours"
    action: notify
    message: "Flagged email from {sender} waiting for response"
    priority: low
```

### Development

```yaml
monitor: development
enabled: false  # Enable based on USER.md context
checks:
  - name: "Build failed"
    condition: "terminal shows build error"
    action: notify
    message: "Build failure detected. Check terminal output."
    priority: high

  - name: "Long-running process"
    condition: "process running > 30 minutes without output"
    action: notify
    message: "Process may be stuck: {process_name}"
    priority: medium
```

---

## Custom Monitors

<!-- Add your own monitors here -->

```yaml
# Template for custom monitor
monitor: custom_example
enabled: false
checks:
  - name: "Descriptive name"
    condition: "what triggers this check"
    action: notify | log | execute
    command: "optional command to run on trigger"
    message: "notification message with {variables}"
    priority: low | medium | high
    cooldown: "time between repeated notifications"
```

---

## Priority Levels

| Level | Behavior | Example |
|-------|----------|---------|
| **high** | Immediate notification, sound alert | System resource critical |
| **medium** | Notification, no sound | Unread messages |
| **low** | Log only, batch with daily summary | Minor workspace notes |

---

## Integration Notes

### With SOUL.md
Heartbeat alerts use the communication style defined in SOUL.md. Alerts will be:
- Precise and actionable
- Without unnecessary pleasantries
- Including relevant context

### With USER.md
Heartbeat respects:
- Working hours (no alerts during quiet hours)
- Notification preferences
- Sensitive application boundaries

### With MEMORY.md
Heartbeat logs are recorded in MEMORY.md session logs when:
- A high-priority alert is triggered
- User takes action on an alert
- Patterns emerge (same alert 3+ times in a day)

---

## Tuning Tips

1. **Start conservative**: Enable few monitors, add more as needed
2. **Adjust cooldowns**: If an alert feels spammy, increase cooldown
3. **Review weekly**: Check which alerts were useful vs. ignored
4. **Use quiet hours**: Protect focus time from low-priority interruptions

---

## Disable All Heartbeats

To completely disable heartbeat monitoring:

```yaml
heartbeat:
  enabled: false
```

Or set working hours to zero in USER.md.
