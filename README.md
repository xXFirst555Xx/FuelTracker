# FuelTracker
[![Dependabot alerts](https://img.shields.io/badge/dependabot-enabled-brightgreen?logo=dependabot)](../../security/dependabot)

โปรแกรมตัวอย่างแสดงโครงสร้าง MVC สำหรับบันทึกการใช้น้ำมัน

แถบด้านข้างใช้ชุดไอคอน Feather พร้อมข้อความภาษาไทย

## คุณสมบัติ

- **แผงสถิติ** แสดงกิโลเมตรต่อลิตรและต้นทุนต่อกิโลเมตร ดูรายละเอียดได้ที่
  [USAGE.md](docs/USAGE.md).
- **การสำรองข้อมูลอัตโนมัติ** เก็บสำเนารายวันได้สูงสุด 30 ชุดไว้ที่
  `~/.fueltracker/backups/` (ดู [USAGE.md](docs/USAGE.md)).
- **ออกจากโปรแกรมอย่างนุ่มนวล** จะลบตัวกรองอีเวนต์ของหน้าต่างหลักเมื่อ
  แอปพลิเคชันกำลังจะปิด.
- **การแจ้งเตือนงบประมาณรายเดือน** แสดงการแจ้งเตือนแบบ toast เมื่อเกินขีดจำกัด
  วิธีใช้อยู่ใน [BUDGET.md](docs/BUDGET.md).
- **ตัวจัดตารางบำรุงรักษา** จะเน้นงานที่ค้างกำหนด อ่านเพิ่มเติมที่
  [MAINTENANCE.md](docs/MAINTENANCE.md).
- **การส่งออก CSV/PDF/Excel** ผ่าน `ExportService` สร้างรายงานประจำเดือน
  อธิบายไว้ใน [EXPORTING.md](docs/EXPORTING.md).
- การส่งออก Excel ต้องใช้ไลบรารี `openpyxl`.
- **ไอคอนใน System Tray** ให้คำสั่งด่วนและทำให้แอปทำงานต่อเนื่องเบื้องหลัง.
- **ปุ่มลัดทั่วระบบ** (ค่าปริยาย `Ctrl+Shift+N`)
  เปิดหน้าต่างเพิ่มรายการได้ทันที.
- **API ราคาน้ำมัน** ดึงราคาน้ำมันประจำวันด้วย `OilPriceService`.
  ดูวิธีใช้ที่ [API.md](docs/API.md).
- **หน้ารายงาน** สรุปการใช้น้ำมันด้วยกราฟและตาราง.
  ดูภาพตัวอย่างได้ที่ [REPORTS.md](docs/REPORTS.md).
- **การอัปเดตแบบลงนาม** ใช้เครื่องมือ `tufup` และ The Update Framework.
  วิธีตั้งค่าอยู่ใน [UPDATER_SETUP.md](docs/UPDATER_SETUP.md).

## ความต้องการ

- Python 3.11 or later
- ติดตั้งแพ็กเกจที่ระบุใน `requirements.lock` (เช่น `SQLModel`)
- ติดตั้งแพ็กเกจระบบ `libegl1` (หรือเทียบเท่า) เพื่อให้การทดสอบที่ใช้ PySide6 ทำงานได้

```bash
sudo apt-get install libegl1
```

## การติดตั้ง

```bash
pip install -e .[dev]
```
คำสั่งนี้จะติดตั้งไทป์สตับที่จำเป็นสำหรับการพัฒนา เช่น `types-setuptools` เพื่อให้การตรวจสอบชนิดด้วย `mypy` ทำงานได้ครบถ้วน

## ใช้งาน Poe the Poet

ติดตั้ง `Poe the Poet` เพื่อจัดการงานต่าง ๆ ภายในโปรเจ็กต์ได้ด้วย

```bash
pip install poethepoet
```

งานที่มีให้ใช้งานประกอบด้วย

- `poe lint` - รัน `ruff`, `mypy` และ `vulture` เพื่อตรวจสอบคุณภาพโค้ด
- `poe test` - รันชุดทดสอบด้วย `pytest -n auto` หลังจากอัปเกรดฐานข้อมูล
- `poe cover` - รันชุดทดสอบพร้อมรายงาน coverage ด้วย `pytest -n auto`
- `poe migrate` - รันสคริปต์ `alembic` เพื่ออัปเกรดฐานข้อมูล
- `poe runtime-check` - เปิดโปรแกรมแบบไม่สร้างหน้าต่างเพื่อตรวจสอบการทำงาน
- `poe build` - สร้างไฟล์ปฏิบัติการแบบ standalone ด้วย `PyInstaller`
- `poe validate` - รันคำสั่ง `lint` แล้วต่อด้วย `test`
- `poe report` - รัน `lint`, `test` และ `runtime-check` เพื่อรายงานผลโดยรวม

คำสั่งเหล่านี้กำหนดไว้ในไฟล์ `pyproject.toml` สามารถเรียกใช้ได้ตามต้องการ

หากปรับแก้รายการแพ็กเกจใน `pyproject.toml` ให้รัน `make lock` เพื่ออัปเดต
ไฟล์ `requirements.lock`

## การตั้งค่าสภาพแวดล้อม

โปรเจ็กต์นี้ใช้ [pre-commit](https://pre-commit.com/) เพื่อตรวจสอบสไตล์และรันทดสอบโดยอัตโนมัติ
ติดตั้งและเปิดใช้งานฮุคได้ด้วยคำสั่งต่อไปนี้:

```bash
pip install pre-commit
pre-commit install
```

ติดตั้งแพ็กเกจพัฒนาเพิ่มเติมด้วยคำสั่ง

```bash
pip install -e .[dev]
```
คำสั่งนี้จะลงไทป์สตับ รวมถึง `types-requests` เพื่อให้ `mypy` ตรวจสอบ
การนำเข้าไลบรารี `requests` ได้อย่างครบถ้วน

ฮุคจะรัน `ruff`, `black`, `mypy` และ `pytest -n auto` ทุกครั้งที่คอมมิต
หากต้องการรันทั้งหมดด้วยตนเองให้ใช้:

```bash
pre-commit run --all-files
```

## การรันทดสอบ

ก่อนรัน `pytest` จำเป็นต้องติดตั้งแพ็กเกจจาก `requirements.lock`
ซึ่งรวม `SQLModel` และไลบรารีหลักอื่น ๆ ไว้ครบถ้วน:

```bash
pip install -r requirements.lock
pip install -e .[dev]
pytest -n auto
```

สามารถเรียกสคริปต์ `scripts/dev_setup.sh` เพื่อทำขั้นตอนติดตั้งให้อัตโนมัติได้เช่นกัน:

```bash
./scripts/dev_setup.sh
pytest -n auto
```

หากต้องการดูรายงาน coverage ใช้คำสั่ง:

```bash
poe cover
```

## การแก้ปัญหา

หากทดสอบบน Windows แล้วพบข้อความ `WPARAM is simple, so must be an int` ให้ตรวจสอบว่า
ได้อัปเดตโค้ดเวอร์ชันล่าสุดซึ่งบังคับให้ callback ของ hotkey ส่งคืนค่า `1` เสมอ
(ดูโมดูล `src/hotkey.py`) รวมถึงติดตั้งแพ็กเกจด้วย `pip install -e .` ก่อนรัน `pytest`.

## การตั้งค่า

คัดลอก `.env.example` ไปเป็น `.env` แล้วปรับค่าตามต้องการ
เมื่อรันโปรแกรม [`python-dotenv`](https://pypi.org/project/python-dotenv/) จะโหลดตัวแปรจากไฟล์นี้ให้โดยอัตโนมัติ

- `DB_PATH` กำหนดตำแหน่งฐานข้อมูล SQLite (ค่าเริ่มต้นคือ
  `appdirs.user_data_dir("FuelTracker", "YourOrg")/fuel.db`)
- `FT_THEME` เลือกธีม `light`, `dark` หรือ `modern`
- `FT_DB_PASSWORD` ตั้งรหัสผ่านเพื่อเปิดใช้ SQLCipher (ปล่อยว่างได้ถ้าไม่ต้องการ)
- `OIL_API_BASE` กำหนด URL พื้นฐานสำหรับ API ราคาน้ำมัน (เขียนทับค่าที่ตั้งไว้)
- `UPDATE_HOURS` กำหนดช่วงเวลาตรวจสอบอัปเดตอัตโนมัติ (หน่วยชั่วโมง)
  ตั้งเป็น `0` เพื่อปิดการตรวจสอบ

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

## ปุ่มลัด

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

หลังจากติดตั้งโปรเจ็กต์ตามขั้นตอนด้านบน สามารถรันทดสอบทั้งหมดได้ด้วย `pytest -n auto`
โดยทำงานภายใน virtual environment:

```bat
python -m venv .venv
\.venv\Scripts\activate
pip install -r requirements.lock
rem requirements.lock รวม `pytest-qt` ซึ่งให้ฟิกซ์เจอร์ `qtbot` สำหรับทดสอบ Qt
pip install -e .
pytest -n auto
```

ต้องการตรวจสอบแบบครบถ้วนยิ่งขึ้นสามารถใช้คำสั่ง `poe validate`
ซึ่งจะติดตั้งแพ็กเกจแบบ editable รัน `pytest -n auto` และทดสอบการเปิดโปรแกรมแบบ
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
