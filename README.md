# DevLog CLI 🦞 v2.0

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**DevLog** is a minimalist developer journaling CLI tool designed to help you keep track of your daily work, bugs, and ideas without leaving your terminal. Built with ❤️ by **Satyaa & Clawdy**.

## New in v2.0 🌟

*   **Project & Status Tracking:** Categorize logs by project and track their status (todo, doing, done).
*   **Activity Heatmap:** Visualize your consistency with a GitHub-style heatmap in `stats`.
*   **Sync & Backup:** Easily sync your database to a private git repo or local path.
*   **Improved Schema:** Faster search and better data structure.

## Features 🚀

*   **Fast Logging:** Add logs quickly with a single command.
*   **Interactive Mode:** Don't like flags? Just run `devlog add` and type away.
*   **Tagging:** Organize entries with tags (e.g., `bug`, `feature`, `meeting`).
*   **Powerful Search:** Full-text search to find that one command you forgot.
*   **Stats & Analytics:** View your logging habits, top tags, and activity heatmap.
*   **Export:** Export your data to Markdown or JSON for backups or reports.
*   **Beautiful TUI:** Powered by `rich` for a pleasant visual experience.

## Installation 📦

It is recommended to use a virtual environment:

```bash
git clone https://github.com/satyaa/dev-log-cli.git
cd dev-log-cli
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

Or for development:

```bash
pip install -e .
```

## Usage 🛠️

### 1. Add a Log
Quick one-liner:
```bash
devlog add "Fixed the infinite loop" --tags bug,fix --project api-server --status done
```

Or interactive mode:
```bash
devlog add
# Prompts you for content, tags, project, and status
```

### 2. List Logs
View recent entries:
```bash
devlog list
```

Filter by tag, project, or status:
```bash
devlog list --tag bug
devlog list --project my-app
devlog list --status todo
```

### 3. Search
Find something specific across content, tags, project, or status:
```bash
devlog search "login"
```

### 4. Stats
See your productivity stats and activity heatmap:
```bash
devlog stats
```

### 5. Sync & Backup
Backup your logs to a local folder or a private git repository:
```bash
devlog sync --path ~/backups/devlog
devlog sync --repo https://github.com/username/my-private-devlogs.git
```

### 6. Export
Export your data:
```bash
devlog export --format markdown --output my_journal.md
```

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Maintained by Satyaa & Clawdy*
