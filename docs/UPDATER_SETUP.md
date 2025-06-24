# การตั้งค่าที่เก็บอัปเดตของ TUF

```bash
# การตั้งค่าเริ่มต้นสำหรับที่เก็บอัปเดต FuelTracker
# สร้างโครงสร้างที่เก็บ
mkdir fueltracker-updates && cd fueltracker-updates

# สร้างคีย์สำหรับเซ็นกำกับ
tufup repo keys create root.ed25519
tufup repo keys create targets.ed25519

# เริ่มต้นข้อมูลเมตาของที่เก็บ
tufup repo init FuelTracker

# ลงทะเบียนคีย์
tufup repo keys add root root.ed25519.pub
tufup repo keys add targets targets.ed25519.pub

# เซ็นข้อมูลเมตาครั้งแรก
tufup repo sign root
tufup repo sign targets
```
