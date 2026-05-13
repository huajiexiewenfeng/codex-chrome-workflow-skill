# Codex Chrome Workflow Skill

中文说明见：[README.zh-CN.md](README.zh-CN.md)

A Codex Skill for Chrome-backed workflow automation.

This repository is intended to be installed by `npx skills add`:

```bash
npx skills add https://github.com/huajiexiewenfeng/codex-chrome-workflow-skill
```

Before first use, ask the Agent to run the configuration workflow and create a local `config.json`.

Users should not manually run the helper scripts during normal use. Scripts such as `scripts/extract_month_tasks.py` are internal helpers for the Agent workflow.

Do not commit real internal URLs, employee IDs, project IDs, or private configuration.

