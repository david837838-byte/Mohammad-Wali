#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database.db_handler import get_db_connection

print("🔍 فحص قاعدة البيانات...")
print("=" * 50)

conn = get_db_connection()
cursor = conn.cursor()

# جلب عدد الجداول
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"✅ عدد الجداول: {len(tables)}")
for table in tables:
    print(f"   - {table[0]}")

# عدد المستخدمين
cursor.execute("SELECT COUNT(*) FROM users")
users_count = cursor.fetchone()[0]
print(f"\n✅ عدد المستخدمين: {users_count}")

# عدد المرضى
cursor.execute("SELECT COUNT(*) FROM patients")
patients_count = cursor.fetchone()[0]
print(f"✅ عدد المرضى: {patients_count}")

# عدد السجلات الطبية
cursor.execute("SELECT COUNT(*) FROM medical_records")
medical_count = cursor.fetchone()[0]
print(f"✅ عدد السجلات الطبية: {medical_count}")

# عدد الزيارات
cursor.execute("SELECT COUNT(*) FROM visits")
visits_count = cursor.fetchone()[0]
print(f"✅ عدد الزيارات: {visits_count}")

conn.close()

print("\n" + "=" * 50)
print("✅ قاعدة البيانات تعمل بشكل صحيح!")
print("🚀 النظام جاهز للاستخدام!")
