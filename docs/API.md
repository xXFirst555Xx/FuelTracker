# การใช้งาน OilPriceService

`fetch_latest(session)` จะดาวน์โหลดราคาน้ำมันล่าสุดจาก Thai-Oil-API และบันทึกลงตาราง `FuelPrice` โดยจะข้ามวันที่มีข้อมูลอยู่แล้ว

สามารถกำหนดฐาน URL ของ API ผ่านตัวแปรสภาพแวดล้อม `OIL_API_BASE` หรือตัวแปร `api_base` ในฟังก์ชัน `fetch_latest`

จำนวนวันที่เก็บข้อมูลสามารถปรับได้ด้วยตัวแปร `OIL_PRICE_RETENTION_DAYS` (ค่าเริ่มต้น 30 วัน) โดย `fetch_latest` จะลบรายการเก่าหลังดาวน์โหลดสำเร็จ

ใช้ `get_price(session, fuel_type, station, date)` เพื่อดึงราคาน้ำมันในรูป `Decimal` หรือ `None` หากไม่มีข้อมูล

หากเกิดข้อผิดพลาดด้านเครือข่าย ตรวจสอบว่าระบบอนุญาตให้เชื่อมต่อ HTTPS ไปยัง `api.chnwt.dev`
