# DevLog CLI 🦞📝

A minimalist developer journaling tool for the terminal. Built for speed and simplicity.

## Features
- ⚡ **Fast**: Instant startup.
- 🔦 **Searchable**: Full-text search over your logs.
- 🎨 **Rich UI**: Beautiful terminal output.
- 💾 **Local**: Data stored in `~/.devlog.db` (SQLite).

## Installation

```bash
pip install .
```

## Usage

```bash
# Add a log
devlog add "Refactored the auth middleware" --tags "refactor,auth"

# List recent logs
devlog ls

# Search logs
devlog search "auth"

# Show stats
devlog stats
```

## License
MIT
