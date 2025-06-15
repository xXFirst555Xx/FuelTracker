# FuelTracker

Simple application demonstrating MVC architecture for tracking fuel usage.

The sidebar uses Feather icons alongside Thai text labels.

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

## Themes

Three Qt stylesheets are included: `theme.qss` (light), `theme_dark.qss` (dark)
and `modern.qss`.
Set the `FT_THEME` environment variable or pass `--theme` on the command line
to select a theme. Valid values are `light`, `dark` and `modern`. Omitting the
argument uses the default light theme. Simply restart the application after
changing the variable or option to switch themes.

## Fonts

The application now relies on widely available fonts rather than the
previously required **Prompt** typeface. The QSS themes default to
`Tahoma`, `Arial` and finally the system sans-serif. No additional font
installation is needed.

To use custom fonts, place the `.ttf` files under `assets/fonts` and
update the `font-family` rules in the QSS files.

## Running

```bash
python -m src.app
```

Launching via `-m` ensures the package is recognized, preventing the relative-import error.

## Building

Run the Windows build script to create a standalone executable. You can use the batch file or the PowerShell version:

```bat
build.bat
```

```powershell
./build.ps1
```

The resulting binary will be placed in the `dist` directory. Set the `SIGNTOOL` and `CERT_PATH` environment variables to automatically sign the executable.

The PyInstaller spec embeds the application icon as a base64 string so no separate
binary asset needs to be stored in the repository.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
