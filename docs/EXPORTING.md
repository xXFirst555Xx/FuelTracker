# การส่งออกรายงาน

บริการ `Exporter` สามารถสร้างรายงานประจำเดือนจากข้อมูลที่บันทึกไว้
รองรับสองรูปแบบคือ

* **CSV** ด้วย `Exporter.monthly_csv(month, year, path)`
* **PDF** ด้วย `Exporter.monthly_pdf(month, year, path)`
* **Excel** ด้วย `Exporter.monthly_excel(month, year, path)`

การส่งออกเป็น Excel ต้องติดตั้งไลบรารี `openpyxl`.

ทั้งสองเมทอดรับค่าเดือน ปี และเส้นทางปลายทางแบบ `Path`
