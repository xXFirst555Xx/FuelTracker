# FuelTracker

Simple application demonstrating MVC architecture for tracking fuel usage.

## Requirements

- Python 3.12
- Packages listed in `requirements.txt`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running

```bash
python -m src.app
```

## Building

Run the included batch script on Windows to create a standalone executable:

```bat
build.bat
```

The resulting binary will be placed in the `dist` directory. Set the `SIGNTOOL` and `CERT_PATH` environment variables to automatically sign the executable.

The PyInstaller spec embeds the application icon as a base64 string so no separate
binary asset needs to be stored in the repository.
