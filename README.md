# DevLog CLI 🦞 v3.0

![PyPI - Version](https://img.shields.io/pypi/v/dev-log-cli)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**DevLog** is a minimalist developer journaling CLI tool designed to help you keep track of your daily work, bugs, and ideas without leaving your terminal. Built with ❤️ by **Satyaa & Clawdy**.

**Status:** 🚀 Available on [PyPI](https://pypi.org/project/dev-log-cli/)

## New in v3.0 🚀

*   **Interactive Editing:** Use `devlog edit <id>` to update any field of a log entry.
*   **Deletion:** Safely remove entries with `devlog delete <id>` (includes confirmation).
*   **Detailed View:** Use `devlog view <id>` for a beautiful, full-width display of a single entry.
*   **Enhanced Status System:**
    *   Standardized statuses: `pending`, `completed`, `in-progress`, `none`.
    *   Custom status support during `add` and `edit`.
    *   **Status Summary:** The `list` command now shows a breakdown of statuses for the logs in view.
*   **Stats Filtering:** Filter your activity metrics by project using `devlog stats --project <name>`.
*   **Improved Search UI:** Search results are now more readable and detailed.

## Features 🌟

*   **Fast Logging:** Add logs quickly with a single command.
*   **Interactive Mode:** Don't like flags? Just run `devlog add` and type away.
*   **Tagging:** Organize entries with tags (e.g., `bug`, `feature`, `meeting`).
*   **Powerful Search:** Full-text search to find that one command you forgot.
*   **Stats & Analytics:** View your logging habits, top tags, and activity heatmap.
*   **Export:** Export your data to Markdown or JSON for backups or reports.
*   **Beautiful TUI:** Powered by `rich` for a pleasant visual experience.

## Installation 📦

### Global (Recommended for Linux/macOS)
The cleanest way to install DevLog as a global tool without managing virtual environments:
```bash
pipx install dev-log-cli
```

### From PyPI
```bash
pip install dev-log-cli
```

### From Source
```bash
git clone https://github.com/satyaa/dev-log-cli.git
cd dev-log-cli
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Usage 🛠️

### 1. Add a Log
Quick one-liner:
```bash
devlog add "Fixed the infinite loop" --tags bug,fix --project api-server --status completed
```

Or interactive mode:
```bash
devlog add
# Prompts you for content, tags, project, and status
```

### 2. List & View Logs
View recent entries:
```bash
devlog list
```

View a specific entry in detail:
```bash
devlog view 42
```

Filter by tag, project, or status:
```bash
devlog list --tag bug
devlog list --project my-app
devlog list --status pending
```

### 3. Edit & Delete
Modify an existing entry:
```bash
devlog edit 42
```

Delete an entry:
```bash
devlog delete 42
```

### 4. Search
Find something specific across content, tags, project, or status:
```bash
devlog search "login"
```

### 5. Stats
See your productivity stats and activity heatmap:
```bash
devlog stats
devlog stats --project api-server
```

### 6. Sync & Backup
Backup your logs to a local folder or a private git repository:
```bash
devlog sync --path ~/backups/devlog
devlog sync --repo https://github.com/username/my-private-devlogs.git
```

### 7. Export
Export your data:
```bash
devlog export --format markdown --output my_journal.md
```

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Maintained by Satyaa & Clawdy*
