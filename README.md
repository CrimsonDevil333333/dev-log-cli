# DevLog CLI 🦞

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**DevLog** is a minimalist developer journaling CLI tool designed to help you keep track of your daily work, bugs, and ideas without leaving your terminal. Built with ❤️ by **Satyaa & Clawdy**.

## Features 🚀

*   **Fast Logging:** Add logs quickly with a single command.
*   **Interactive Mode:** Don't like flags? Just run `devlog add` and type away.
*   **Tagging:** Organize entries with tags (e.g., `bug`, `feature`, `meeting`).
*   **Powerful Search:** Full-text search to find that one command you forgot.
*   **Stats & Analytics:** View your logging habits and top tags.
*   **Export:** Export your data to Markdown or JSON for backups or reports.
*   **Beautiful TUI:** Powered by `rich` for a pleasant visual experience.

## Installation 📦

You can install DevLog directly from the source:

```bash
git clone https://github.com/satyaa/dev-log-cli.git
cd dev-log-cli
pip install .
```

Or if you are developing:

```bash
pip install -e .
```

## Usage 🛠️

### 1. Add a Log
Quick one-liner:
```bash
devlog add "Fixed the infinite loop in the login module" --tags bug,fix
```

Or interactive mode:
```bash
devlog add
# Prompts you for content and tags
```

### 2. List Logs
View recent entries:
```bash
devlog list
```

Filter by tag:
```bash
devlog list --tag bug
```

### 3. Search
Find something specific:
```bash
devlog search "login"
```

### 4. Stats
See your productivity stats:
```bash
devlog stats
```

### 5. Export
Backup your logs:
```bash
devlog export --format markdown --output my_journal.md
devlog export --format json --output backup.json
```

## TUI Example

```text
╭─────────────────────────────── Dev Logs (Last 3) ────────────────────────────────╮
│ Time             Content                                           Tags          │
│ ──────────────────────────────────────────────────────────────────────────────── │
│ 2026-02-05 01:20 Refactored the database schema for better perf... refactor,db   │
│ 2026-02-04 14:15 Initial commit of the new CLI structure           init,feat     │
│ 2026-02-04 10:00 Meeting with the design team regarding UI         meeting       │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Maintained by Satyaa & Clawdy*
