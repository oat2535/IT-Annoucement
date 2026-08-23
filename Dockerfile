# เลือกใช้ Python 3.12 (แบบ Alpine) เป็น Image หลัก เพื่อลดขนาดไฟล์และเพิ่มความปลอดภัย
FROM python:3.12-alpine

# ตั้งค่าตัวแปรสิ่งแวดล้อม (Environment Variables)
# ป้องกันไม่ให้ Python เขียนไฟล์ .pyc (ไม่จำเป็นใน Docker)
ENV PYTHONDONTWRITEBYTECODE=1
# ให้ Python ส่ง Log ออกมาทันที ไม่ต้องรอ Buffer (ช่วยให้เห็น Log Real-time)
ENV PYTHONUNBUFFERED=1

# กำหนดโฟลเดอร์ทำงานภายใน Container เป็น /app
WORKDIR /app

# คัดลอกไฟล์ requirements.txt เข้าไปก่อน เพื่อติดตั้ง Library
# (ทำแยกเพื่อใช้ประโยชน์จาก Docker Cache Layer หากไม่มีการแก้ไฟล์นี้)
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
# ติดตั้ง LibreOffice และ Font ภาษาไทย สำหรับแปลงไฟล์ Word เป็น PDF
RUN apk add --no-cache libreoffice font-terminus font-inconsolata font-dejavu font-noto font-noto-cjk font-awesome font-noto-extra font-noto-thai


# คัดลอกไฟล์โปรเจคทั้งหมดใน Folder ปัจจุบัน เข้าสู่ Container
COPY . /app/

# เปิด Port 8000 สำหรับการเชื่อมต่อ (ปรับเปลี่ยนจาก 5886 เพื่อไม่ให้ชนกับ Project เดิม)
EXPOSE 5889

# คำสั่งเริ่มต้นเมื่อ Container ทำงาน (รัน Server ผ่าน Gunicorn สำหรับ Production)
# เพิ่ม --workers 3 และ --threads 2 เพื่อรองรับ Request พร้อมกันหลายๆ ตัว ป้องกันปัญหาหน้าเว็บโหลดช้า
CMD ["gunicorn", "it_announcement_project.wsgi:application", "--bind", "0.0.0.0:5889", "--workers", "3", "--threads", "2"]
