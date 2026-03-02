# nanobot Skills

This directory contains built-in skills that extend nanobot's capabilities.

## Skill Format

Each skill is a directory containing a `SKILL.md` file with:

- YAML frontmatter (name, description, metadata)
- Markdown instructions for the agent

## Attribution

These skills are adapted from [OpenClaw](https://github.com/openclaw/openclaw)'s skill system.
The skill format and metadata structure follow OpenClaw's conventions to maintain compatibility.

## Available Skills

| Skill           | Description                                             |
| --------------- | ------------------------------------------------------- |
| `memory`        | Two-layer memory system with grep-based recall          |
| `github`        | Interact with GitHub using the `gh` CLI                 |
| `weather`       | Get current weather and forecasts (no API key required) |
| `cron`          | Schedule reminders and recurring tasks                  |
| `clawhub`       | Search and install skills from ClawHub registry         |
| `skill-creator` | Create or update AgentSkills                            |
