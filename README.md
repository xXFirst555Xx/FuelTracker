# FuelTracker
[![Dependabot alerts](https://img.shields.io/badge/dependabot-enabled-brightgreen?logo=dependabot)](../../security/dependabot)

โปรแกรมตัวอย่างแสดงโครงสร้าง MVC สำหรับบันทึกการใช้น้ำมัน

แถบด้านข้างใช้ชุดไอคอน Feather พร้อมข้อความภาษาไทย

## Features

- **Statistics panel** shows kilometres per litre and cost per kilometre. See
  [USAGE.md](docs/USAGE.md) for details.
- **Automatic backups** keep up to 30 daily copies under
  `~/.fueltracker/backups/` (see [USAGE.md](docs/USAGE.md)).
- **Graceful exit** removes the main window's event filter when the
  application is about to quit.
- **Monthly budget alerts** display a toast notification when the limit is
  exceeded. Usage in [BUDGET.md](docs/BUDGET.md).
- **Maintenance scheduler** highlights overdue tasks. Learn more in
  [MAINTENANCE.md](docs/MAINTENANCE.md).
- **CSV/PDF/Excel exporting** via `ExportService` creates monthly reports,
  described in [EXPORTING.md](docs/EXPORTING.md).
- Excel export requires the `openpyxl` library.
- **System tray icon** provides quick actions and keeps the app running in the background.
- **Global hotkey** (default `Ctrl+Shift+N`) instantly opens the Add Entry dialog.
- **Oil price API** fetches daily fuel prices using `OilPriceService`.
  See [API.md](docs/API.md) for usage details.
- **Reports page** summarises fuel usage with graphs and tables.
  See [REPORTS.md](docs/REPORTS.md) for screenshots.
- **Signed updates** use the `tufup` CLI and The Update Framework.
  Setup instructions in [UPDATER_SETUP.md](docs/UPDATER_SETUP.md).

## ความต้องการ

- Python 3.11 or later
 - ติดตั้งแพ็กเกจที่ระบุใน `requirements.lock`
- ติดตั้งแพ็กเกจระบบ `libegl1` (หรือเทียบเท่า) เพื่อให้การทดสอบที่ใช้ PySide6 ทำงานได้

```bash
sudo apt-get install libegl1
```

## การติดตั้ง

```bash
pip install -e .[dev]
```
คำสั่งนี้จะติดตั้งไทป์สตับที่จำเป็นสำหรับการพัฒนา เช่น `types-setuptools` เพื่อให้การตรวจสอบชนิดด้วย `mypy` ทำงานได้ครบถ้วน

## Using Poe the Poet

ติดตั้ง `Poe the Poet` เพื่อจัดการงานต่าง ๆ ภายในโปรเจ็กต์ได้ด้วย

```bash
pip install poethepoet
```

งานที่มีให้ใช้งานประกอบด้วย

- `poe lint` - รัน `ruff`, `mypy` และ `vulture` เพื่อตรวจสอบคุณภาพโค้ด
- `poe test` - รันชุดทดสอบด้วย `pytest` หลังจากอัปเกรดฐานข้อมูล
- `poe migrate` - รันสคริปต์ `alembic` เพื่ออัปเกรดฐานข้อมูล
- `poe runtime-check` - เปิดโปรแกรมแบบไม่สร้างหน้าต่างเพื่อตรวจสอบการทำงาน
- `poe build` - สร้างไฟล์ปฏิบัติการแบบ standalone ด้วย `PyInstaller`
- `poe validate` - รันคำสั่ง `lint` แล้วต่อด้วย `test`
- `poe report` - รัน `lint`, `test` และ `runtime-check` เพื่อรายงานผลโดยรวม

คำสั่งเหล่านี้กำหนดไว้ในไฟล์ `pyproject.toml` สามารถเรียกใช้ได้ตามต้องการ

หากปรับแก้รายการแพ็กเกจใน `pyproject.toml` ให้รัน `make lock` เพื่ออัปเดต
ไฟล์ `requirements.lock`

## Development setup

โปรเจ็กต์นี้ใช้ [pre-commit](https://pre-commit.com/) เพื่อตรวจสอบสไตล์และรันทดสอบโดยอัตโนมัติ
ติดตั้งและเปิดใช้งานฮุคได้ด้วยคำสั่งต่อไปนี้:

```bash
pip install pre-commit
pre-commit install
```

ฮุคจะรัน `ruff`, `black`, `mypy` และ `pytest` ทุกครั้งที่คอมมิต
หากต้องการรันทั้งหมดด้วยตนเองให้ใช้:

```bash
pre-commit run --all-files
```

## การแก้ปัญหา

หากทดสอบบน Windows แล้วพบข้อความ `WPARAM is simple, so must be an int` ให้ตรวจสอบว่า
ได้อัปเดตโค้ดเวอร์ชันล่าสุดซึ่งบังคับให้ callback ของ hotkey ส่งคืนค่า `1` เสมอ
(ดูโมดูล `src/hotkey.py`) รวมถึงติดตั้งแพ็กเกจด้วย `pip install -e .` ก่อนรัน `pytest`.

## การตั้งค่า

คัดลอก `.env.example` ไปเป็น `.env` แล้วปรับค่าตามต้องการ
เมื่อรันโปรแกรม [`python-dotenv`](https://pypi.org/project/python-dotenv/) จะโหลดตัวแปรจากไฟล์นี้ให้โดยอัตโนมัติ

- `DB_PATH` กำหนดตำแหน่งฐานข้อมูล SQLite (ค่าเริ่มต้นคือ
  `appdirs.user_data_dir("FuelTracker")/fuel.db`)
- `FT_THEME` เลือกธีม `light`, `dark` หรือ `modern`
- `FT_DB_PASSWORD` ตั้งรหัสผ่านเพื่อเปิดใช้ SQLCipher (ปล่อยว่างได้ถ้าไม่ต้องการ)
- `OIL_API_BASE` กำหนด URL พื้นฐานสำหรับ API ราคาน้ำมัน (เขียนทับค่าที่ตั้งไว้)

## ธีม

มีไฟล์สไตล์ชีต Qt ให้เลือกสี่แบบได้แก่ `theme.qss` (โทนสว่าง) `theme_dark.qss` (โทนมืด) `modern.qss` และ `vivid.qss` (สีสันสดใส)
ตั้งค่าตัวแปร `FT_THEME` หรือระบุ `--theme` ขณะเรียกโปรแกรมเพื่อเลือกธีม
ค่าที่รองรับคือ `light`, `dark`, `modern` และ `vivid` หากไม่ระบุจะใช้ธีมสว่างเป็นค่าเริ่มต้น
เพียงเริ่มโปรแกรมใหม่หลังเปลี่ยนค่าเพื่อให้ธีมใหม่ทำงาน

## แบบอักษร

โปรแกรมใช้แบบอักษรที่มีใช้งานทั่วไป จึงไม่จำเป็นต้องติดตั้งแบบอักษร **Prompt**
ไฟล์ QSS ตั้งค่าเริ่มต้นเป็น `Tahoma`, `Arial` และแบบ sans-serif ของระบบ
หากต้องการใช้แบบอักษรอื่น ให้วางไฟล์ `.ttf` ไว้ใน `assets/fonts` แล้วปรับ `font-family` ในไฟล์ QSS

## การใช้งาน

```bash
python -m fueltracker
```

หรือจะใช้คำสั่ง

```bash
fueltracker-launcher
```
เพื่อเปิดโปรแกรมผ่านตัว launcher ที่ตรวจสอบอัปเดตก่อนเริ่มทำงาน

ใช้ `--start-minimized` เพื่อเปิดโปรแกรมแบบย่อโดยอัตโนมัติ

โปรแกรมจะอัปเกรดฐานข้อมูลเป็นเวอร์ชันล่าสุดให้อัตโนมัติ หากไม่ได้ใช้ `--check`

รันคำสั่งด้านล่างเพื่ออัปเกรดฐานข้อมูล:

```bash
python -m fueltracker migrate
```
หากอัปเดตจากเวอร์ชันก่อนหน้า ให้รันคำสั่งนี้อีกครั้งเพื่อสร้างดัชนีใหม่ใน
ตาราง `fuelentry` และ `maintenance`

การรันด้วย `-m` ช่วยให้โมดูลถูกค้นพบถูกต้อง ป้องกันปัญหาการนำเข้าแบบ relative

## Shortcuts

- `Ctrl+N` สร้างรายการใหม่
- `F1` เปิดหน้าต่าง About

## การสร้างแพ็กเกจ

ใช้คำสั่ง `poe build` เพื่อสร้างไฟล์ปฏิบัติการ

```bash
poe build
```

ไฟล์ที่ได้จะอยู่ในไดเรกทอรี `dist` กำหนดตัวแปร `SIGNTOOL` และ `CERT_PATH` เพื่อเซ็นไฟล์อัตโนมัติ

สเปกของ PyInstaller ฝังไอคอนโปรแกรมเป็น base64 จึงไม่ต้องเก็บไฟล์แยกในคลัง

## การทดสอบบน Windows

หลังจากติดตั้งโปรเจ็กต์ตามขั้นตอนด้านบน สามารถรันทดสอบทั้งหมดได้ด้วย `pytest`
โดยทำงานภายใน virtual environment:

```bat
python -m venv .venv
\.venv\Scripts\activate
pip install -r requirements.lock
rem requirements.lock รวม `pytest-qt` ซึ่งให้ฟิกซ์เจอร์ `qtbot` สำหรับทดสอบ Qt
pip install -e .
pytest
```

ต้องการตรวจสอบแบบครบถ้วนยิ่งขึ้นสามารถใช้คำสั่ง `poe validate`
ซึ่งจะติดตั้งแพ็กเกจแบบ editable รัน `pytest` และทดสอบการเปิดโปรแกรมแบบ
offscreen ผลลัพธ์จะถูกบันทึกไว้ในโฟลเดอร์ `reports/` ทั้งหมด ก่อนใช้งานให้ติดตั้งเครื่องมือสำหรับนักพัฒนาดังนี้

```bash
pip install pydeps ruff vulture mypy
```

```bash
poe validate
```

## การตั้งค่าคลังอัปเดต

โปรเจ็กต์รองรับการอัปเดตแบบลงนามด้วย [TUF](https://theupdateframework.io)
ผ่านเครื่องมือ `tufup`. ดูเอกสาร [UPDATER_SETUP.md](docs/UPDATER_SETUP.md)
และสคริปต์ `scripts/init_repo.sh` เพื่อสร้างคลังอัปเดตเริ่มต้น
และกุญแจสำหรับลงนาม.

โปรเจ็กต์นี้ใช้สัญญาอนุญาต MIT ดูรายละเอียดได้ที่ไฟล์ [LICENSE](LICENSE)
