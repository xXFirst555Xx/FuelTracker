# การส่งออกรายงาน

การส่งออกรายงานประจำเดือนมีให้ใช้งานผ่าน `ExportService`
ซึ่งจะสร้างไฟล์ PDF หรือ Excel ชั่วคราวแล้วคืนค่า `Path`
ของไฟล์ที่สร้างขึ้น ตัวอย่างเช่น

```python
from pathlib import Path
from src.services import ExportService, StorageService

storage = StorageService(Path("db.sqlite"))
service = ExportService(storage)

pdf_file = service.export_monthly_pdf("2024-05", None)
xlsx_file = service.export_monthly_xlsx("2024-05")
```

เมทอด `export_monthly_xlsx` ต้องติดตั้งไลบรารี `openpyxl`
เพื่อเขียนไฟล์ Excel

หากต้องการส่งออกเป็น CSV ยังคงใช้เมทอด `Exporter.monthly_csv`
โดยระบุเดือน ปี และ `Path` ปลายทางเหมือนเดิม

รายงานทั้งสองรูปแบบจะมีคอลัมน์ต่อไปนี้

- `date`
- `fuel_type`
- `odo_before`
- `odo_after`
- `distance`
- `liters`
- `amount_spent`

## รูปแบบไฟล์ PDF

ไฟล์ PDF ที่สร้างประกอบด้วยสามหน้าได้แก่

1. รายการข้อมูลการเติมเชื้อเพลิงเรียงลำดับตามวันที่
2. หน้าสรุปรวมระยะทาง ปริมาณเชื้อเพลิง ค่าใช้จ่าย จำนวนครั้งที่เติม
   และราคาเชื้อเพลิงเฉลี่ยต่อ ลิตร ประจำเดือน
3. กราฟแบบแกนคู่แสดงระยะทางและค่าใช้จ่ายรายวัน

แบบอักษรที่ใช้คือ `NotoSansThai` ซึ่งค้นหาผ่าน `matplotlib.font_manager.findfont`.
หากไม่พบแบบอักษรนี้ โปรแกรมจะใช้ `Tahoma` หรือแบบอักษร sans-serif
ทั่วไปแทน

## รูปแบบไฟล์ Excel

ไฟล์ Excel แบ่งเป็นสองชีต

1. **Weekly** - แสดงข้อมูลรายวันแบบสัปดาห์ต่อสัปดาห์
2. **Summary** - สรุปค่าสถิติระยะทาง ลิตรที่ใช้ อัตราสิ้นเปลือง จำนวนครั้งที่เติม
   และราคาเชื้อเพลิงเฉลี่ยต่อ ลิตร
