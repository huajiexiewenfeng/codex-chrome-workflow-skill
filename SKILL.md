---
name: codex-chrome-workflow-skill
description: Use when automating repetitive enterprise web workflows through the Codex Chrome plugin, especially when tasks depend on a real Chrome login session, Excel work plans, form filling, work-hour registration, duplicate-date checks, and reusable workflow rules.
---

# Codex Chrome Workflow Skill

## Overview

Use the Codex Chrome plugin to automate repetitive enterprise browser workflows that depend on a real logged-in Chrome session. The primary example is syncing Excel work-plan rows into an OA task/work-hour system, but the core pattern applies to other internal web tools.

The goal is not just browser clicking. The goal is to turn implicit human workflow rules into a reusable, correctable Skill.

## Configuration

Before running, read `config.json` in this skill directory. If it does not exist, copy `config.example.json` and fill in local values.

For first-time setup, guide the user to run the configuration workflow first. The user should provide local Excel paths, project/stage names, owner, reviewer, role, and monthly parent template through the agent. Do not require the user to manually edit files unless they prefer doing so.

Configuration should define:

- Excel work-plan glob/path
- Default year
- OA/project/stage names
- Monthly parent task template
- Default task type
- Resource role
- Owner/responsible person
- Reviewer/auditor
- Column names used by the Excel files

Never commit real internal URLs, employee IDs, project IDs, or private paths to a public repository. Keep real values in local `config.json`.

## Browser Automation

- Use the Codex Chrome plugin for enterprise browser workflows that require the user's real Chrome session, cookies, SSO login state, or extension-backed tab control.
- Do not silently fall back to an isolated in-app browser for internal systems. It may not have the required login state.
- If the Chrome extension connection fails, stop and ask the user to repair or enable the Codex Chrome Extension.
- Treat browser automation as token-consuming work. Prefer structured, reusable flows over repeated exploratory clicking.

## Extract Monthly Excel Tasks

The agent should run the helper script internally when it needs to extract monthly Excel rows:

```powershell
python scripts/extract_month_tasks.py --month <month> --year <year>
```

The script returns:

- `task_names`: de-duplicated task names in workbook order
- `rows`: source rows with file, sheet, dates, owner, reviewer, description, acceptance criteria, and status

Users normally do not run this command manually. It is part of the Skill workflow.

## Monthly Workflow Pattern

1. Extract target-month rows from Excel.
2. Filter out planning or forecast rows such as `下周计划`, `下周任务`, `后续计划`, or `后续任务`.
3. Use the next concrete Excel file as the source of truth when a previous file only listed future/planned work.
4. In the OA system, find or create the monthly parent task.
5. For each concrete Excel row:
   - Find or create the child task.
   - Fill default role, owner, and reviewer.
   - Register work hours if requested.
6. After processing, report:
   - Created tasks
   - Existing/skipped tasks
   - Registered work hours
   - Duplicate-date skips
   - Remaining missing dates

## Work-Hour Rules

- Completion/progress: `100%`
- Duration: `1` day per work-hour record
- Date: use the Excel row date range as the source of truth
- Description: use the Excel task description
- If estimated workload is greater than `8`, calculate expected work days as `estimated workload / 8`
- For multiple records, prefer the completion date first, then move backward within the Excel start/end date range
- Do not create work-hour records before the Excel start date or after the Excel completion date
- Saturday/Sunday is allowed if the Excel date range includes that date
- Before registering, check whether the same person already has work hours on that date
- If the system warns that the date is already filled, skip that date and continue

## Missing Work-Hour Backfill

After monthly sync, audit the target month for missing work-hour dates for the configured owner/person.

If missing dates are found:

1. List the exact missing dates.
2. Ask the user whether to auto-fill them.
3. Do not invent content silently.

If the user confirms:

- Choose content from nearby or thematically related Excel/OA tasks in the same month.
- Prefer concrete Excel task descriptions.
- Register completion/progress = `100%`, duration = `1`, and a concise description.
- Report which task/description was used for each filled date.

This is an explicit backfill mode. It may differ from strict Excel-row date ranges only after user confirmation or a direct user request for those exact dates.

## Safety

- Do not delete, publish, approve, submit final workflow states, or perform irreversible actions unless the user explicitly confirms.
- Stop for login, MFA, CAPTCHA, ambiguous project matches, missing required fields, or permission errors.
- Keep internal system names, employee IDs, URLs, and project identifiers out of public logs or published examples.

## Workflow Philosophy

Use every correction as a chance to improve the Skill.

When the user says:

- "This date rule is wrong"
- "Use Chrome plugin, not the in-app browser"
- "Do not process forecast tasks"
- "Ask before auto-filling missing dates"

Update the Skill so the correction becomes the next run's default behavior.
