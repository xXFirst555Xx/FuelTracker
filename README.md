# FuelTracker

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
- **CSV/PDF exporting** creates monthly reports, described in
  [EXPORTING.md](docs/EXPORTING.md).

## ความต้องการ

- Python 3.12
- ติดตั้งแพ็กเกจที่ระบุใน `requirements.txt`

## การติดตั้ง

```bash
python -m venv .venv
pip install -r requirements.txt
pip install -e .
```

## การตั้งค่า

คัดลอก `.env.example` ไปเป็น `.env` แล้วปรับค่าตามต้องการ
เมื่อรันโปรแกรม [`python-dotenv`](https://pypi.org/project/python-dotenv/) จะโหลดตัวแปรจากไฟล์นี้ให้โดยอัตโนมัติ

- `DB_PATH` กำหนดตำแหน่งฐานข้อมูล SQLite
- `FT_THEME` เลือกธีม `light`, `dark` หรือ `modern`
- `FT_DB_PASSWORD` ตั้งรหัสผ่านเพื่อเปิดใช้ SQLCipher (ปล่อยว่างได้ถ้าไม่ต้องการ)

## ธีม

มีไฟล์สไตล์ชีต Qt ให้เลือกสามแบบได้แก่ `theme.qss` (โทนสว่าง) `theme_dark.qss` (โทนมืด) และ `modern.qss`
ตั้งค่าตัวแปร `FT_THEME` หรือระบุ `--theme` ขณะเรียกโปรแกรมเพื่อเลือกธีม
ค่าที่รองรับคือ `light`, `dark` และ `modern` หากไม่ระบุจะใช้ธีมสว่างเป็นค่าเริ่มต้น
เพียงเริ่มโปรแกรมใหม่หลังเปลี่ยนค่าเพื่อให้ธีมใหม่ทำงาน

## แบบอักษร

โปรแกรมใช้แบบอักษรที่มีใช้งานทั่วไป จึงไม่จำเป็นต้องติดตั้งแบบอักษร **Prompt**
ไฟล์ QSS ตั้งค่าเริ่มต้นเป็น `Tahoma`, `Arial` และแบบ sans-serif ของระบบ
หากต้องการใช้แบบอักษรอื่น ให้วางไฟล์ `.ttf` ไว้ใน `assets/fonts` แล้วปรับ `font-family` ในไฟล์ QSS

## การใช้งาน

```bash
python -m fueltracker
```

รันคำสั่งด้านล่างเพื่ออัปเกรดฐานข้อมูล:

```bash
python -m fueltracker migrate
```

การรันด้วย `-m` ช่วยให้โมดูลถูกค้นพบถูกต้อง ป้องกันปัญหาการนำเข้าแบบ relative

## การสร้างแพ็กเกจ

รันสคริปต์ batch ที่ให้มาบน Windows เพื่อสร้างไฟล์ปฏิบัติการ

```bat
build.bat
```

ไฟล์ที่ได้จะอยู่ในไดเรกทอรี `dist` กำหนดตัวแปร `SIGNTOOL` และ `CERT_PATH` เพื่อเซ็นไฟล์อัตโนมัติ

สเปกของ PyInstaller ฝังไอคอนโปรแกรมเป็น base64 จึงไม่ต้องเก็บไฟล์แยกในคลัง

โปรเจ็กต์นี้ใช้สัญญาอนุญาต MIT ดูรายละเอียดได้ที่ไฟล์ [LICENSE](LICENSE)
