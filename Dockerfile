# เลือกใช้ Python 3.12 (แบบ Alpine) เป็น Image หลัก เพื่อลดขนาดไฟล์และเพิ่มความปลอดภัย
FROM python:3.12-alpine

# ตั้งค่าตัวแปรสิ่งแวดล้อม (Environment Variables)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# กำหนดโฟลเดอร์ทำงานภายใน Container เป็น /app
WORKDIR /app

# ขั้นตอนที่ 1: ติดตั้ง System Packages (วางไว้บนสุดเพื่อให้ Docker Cache ชั้นนี้ถาวร ไม่ต้องดาวน์โหลดใหม่ทุกครั้งที่แก้โค้ด)
# ปรับตัดฟอนต์ CJK (ภาษาจีน/ญี่ปุ่น/เกาหลี) และฟอนต์ที่ไม่จำเป็นออก ช่วยประหยัดเน็ตและลดขนาดดาวน์โหลดกว่า 600MB
RUN apk add --no-cache curl libreoffice font-noto-thai

# ขั้นตอนที่ 2: ติดตั้ง Python Dependencies (แยก Layer เพื่อให้ Cache ถาวรหาก requirements.txt ไม่เปลี่ยนแปลง)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ขั้นตอนที่ 3: คัดลอก Font ภาษาไทยเฉพาะของระบบ (Tahoma, TH Sarabun, Angsana, Cordia)
COPY fonts/ /usr/share/fonts/custom/
RUN fc-cache -f

# ขั้นตอนที่ 4: คัดลอกไฟล์โปรเจคทั้งหมด เข้าสู่ Container (วางไว้ท้ายสุดเพราะโค้ดมีการแก้ไขบ่อยที่สุด)
COPY . /app/

# เตรียมไดเรกทอรีสำหรับ persistent data & media และแปลง line-endings ป้องกันปัญหา CRLF
RUN mkdir -p /app/data /app/media /app/staticfiles && \
    sed -i 's/\r$//' /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# เปิด Port 5889 สำหรับการเชื่อมต่อ
EXPOSE 5889

# กำหนด Entrypoint Script สำหรับการ Migrate & Collectstatic อัตโนมัติทุกครั้งที่ Deploy
ENTRYPOINT ["/app/entrypoint.sh"]

# คำสั่งเริ่มต้นเมื่อ Container ทำงาน (รัน Server ผ่าน Gunicorn สำหรับ Production)
# เพิ่ม --workers 3 และ --threads 2 เพื่อรองรับ Request พร้อมกันหลายๆ ตัว ป้องกันปัญหาหน้าเว็บโหลดช้า
# เพิ่ม --forwarded-allow-ips "*" เพื่อให้รองรับ Header X-Forwarded-Proto จาก Reverse Proxy สำหรับ HTTPS
CMD ["gunicorn", "it_announcement_project.wsgi:application", "--bind", "0.0.0.0:5889", "--workers", "3", "--threads", "2", "--forwarded-allow-ips", "*"]
