# envoy-cli

> A CLI tool for managing and syncing `.env` files across projects and environments securely.

---

## Installation

```bash
pip install envoy-cli
```

Or with pipx (recommended):

```bash
pipx install envoy-cli
```

---

## Usage

```bash
# Initialize envoy in your project
envoy init

# Push your local .env to a remote environment
envoy push --env production

# Pull the latest .env from a remote environment
envoy pull --env staging

# List all tracked environments
envoy list
```

Secrets are encrypted before being synced and never stored in plain text.

---

## Features

- 🔐 End-to-end encryption for all `.env` values
- 🔄 Sync across multiple environments (dev, staging, production)
- 📁 Support for multiple projects from a single CLI
- 🚀 Simple, intuitive commands

---

## Requirements

- Python 3.8+
- An active internet connection for remote sync operations

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the [MIT License](LICENSE).