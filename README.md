# FuelTracker

Simple application demonstrating MVC architecture for tracking fuel usage.
## Screenshot

![Screenshot](assets/ui.png)


## Requirements

- Python 3.12
- Packages listed in `requirements.txt`

## Setup

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and adjust the values as needed. At runtime
the application will load variables from this file using
[`python-dotenv`](https://pypi.org/project/python-dotenv/).
The `DB_PATH` variable controls where the SQLite database is stored.

## Running

```bash
python -m src.app
```

Launching via `-m` ensures the package is recognized, preventing the relative-import error.

## Building

Run the included batch script on Windows to create a standalone executable:

```bat
build.bat
```

The resulting binary will be placed in the `dist` directory. Set the `SIGNTOOL` and `CERT_PATH` environment variables to automatically sign the executable.

The PyInstaller spec embeds the application icon as a base64 string so no separate
binary asset needs to be stored in the repository.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
