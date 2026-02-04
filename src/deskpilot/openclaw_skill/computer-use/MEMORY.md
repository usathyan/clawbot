# DeskPilot Persistent Memory

> This file stores long-term knowledge that should persist across sessions. DeskPilot reads this at startup and updates it when instructed.

---

## Corrections & Learned Behaviors

<!-- When DeskPilot makes a mistake and you correct it, log it here so it doesn't repeat -->

### Click Behavior
```
Example entries:
- [2024-01-15] User prefers double-click to open files, not single-click
- [2024-01-20] On macOS, user wants Cmd+click for new tab, not right-click menu
```

### Typing Preferences
```
Example entries:
- [2024-01-18] Add 500ms delay after typing in search boxes before pressing Enter
- [2024-01-22] User's keyboard layout is US International, not US Standard
```

### Application-Specific
```
Example entries:
- [2024-01-16] VS Code: User uses Cmd+P for file search, not Cmd+Shift+P
- [2024-01-19] Chrome: Wait for page load before clicking (check for spinner)
- [2024-01-21] Slack: User prefers thread replies over channel messages
```

---

## Project Context

<!-- Ongoing projects that affect automation decisions -->

### Active Projects

```
Example:
Project: Database Migration
- Started: 2024-01-10
- Target: 2024-02-15
- Key files: ~/code/migration/
- Related apps: pgAdmin, VS Code, Terminal
- Notes: Don't restart PostgreSQL service during migration windows
```

### Completed Projects

```
Example:
Project: Q4 Release
- Completed: 2024-01-05
- Archived to: ~/archive/q4-release/
- Lessons: Always run smoke tests after deployment script
```

---

## Established Shortcuts

<!-- Custom shortcuts or workflows that work well -->

### Quick Actions
```
Example:
- "standup" = Open Jira board + Slack #standup channel + yesterday's git log
- "review mode" = Arrange VS Code left, Chrome right, hide Slack
- "focus" = Enable DND on Slack, minimize email, full-screen current app
```

### Keyboard Shortcuts Discovered
```
Example:
- Custom app XYZ uses Ctrl+Shift+R for refresh (not F5)
- IntelliJ on this machine uses Alt+Enter for suggestions
```

---

## Environmental Notes

<!-- Things about this specific machine/setup -->

### Hardware
```
Example:
- External monitor on right side (extended display)
- Mouse is slightly miscalibrated - add +5px to X coordinates
- Touchpad gestures enabled - avoid edge swipes
```

### Software Quirks
```
Example:
- Antivirus sometimes delays app launches by 2-3 seconds
- Docker Desktop takes 30s to start, check status before operations
- VPN must be connected before accessing internal tools
```

---

## Session Logs

<!-- Important decisions and outcomes from recent sessions -->
<!-- Keep last 7 days, archive older to MEMORY_ARCHIVE.md -->

### 2024-01-25
```
- Completed: Automated PR review workflow
- Issue: GitHub page layout changed, updated selectors
- User feedback: "Faster screenshots would be nice" - investigate parallel capture
```

### 2024-01-24
```
- Completed: Set up Slack notification monitoring
- Note: User only wants alerts for @mentions and DMs, not all channel activity
```

---

## Memory Scoring Rules

<!-- Criteria for what gets logged vs. discarded -->

**Always Log (Score 8-10):**
- Corrections to DeskPilot behavior
- New project context affecting multiple sessions
- User preference changes
- Discovered application shortcuts or quirks

**Sometimes Log (Score 5-7):**
- Significant task completions
- Recurring patterns observed
- Minor environmental notes

**Never Log (Score 1-4):**
- One-off task details
- Temporary UI states
- Routine operations that succeeded normally
- Casual conversation

---

## Maintenance

**Last Cleaned:** [Date]
**Next Review:** [Date + 30 days]

<!--
Maintenance tasks:
1. Archive session logs older than 7 days
2. Review corrections - are they still relevant?
3. Update project status - complete or remove stale projects
4. Verify environmental notes still accurate
-->
