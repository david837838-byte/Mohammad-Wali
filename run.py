#!/usr/bin/env python3
"""
نقطة بداية تشغيل بيت المسيح
"""

import os
import sys
from app import app


def check_dependencies():
    """التحقق من المتطلبات الأساسية"""
    try:
        import flask
        import sqlite3
        import pandas
        print("✓ جميع المتطلبات مثبتة")
        return True
    except ImportError as e:
        print(f"✗ خطأ في المتطلبات: {e}")
        print("يرجى تثبيت المتطلبات باستخدام:")
        print("pip install -r requirements.txt")
        return False


def setup_environment():
    """إعداد بيئة النظام"""
    print("جاري إعداد بيئة النظام...")

    # إنشاء المجلدات المطلوبة
    folders = [
        "static/uploads",
        "templates/includes",
        "database",
        "models",
        "controllers",
        "utils"
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ تم إنشاء مجلد: {folder}")

    # ملفات التكوين الافتراضية
    config_files = {
        "requirements.txt": (
            "Flask==2.3.3\n"
            "Flask-Session==0.5.0\n"
            "python-dotenv==1.0.0\n"
            "requests==2.31.0\n"
            "pandas==2.0.3\n"
            "openpyxl==3.1.2\n"
            "gspread==5.11.3\n"
            "google-auth==2.22.0\n"
            "google-auth-oauthlib==1.0.0\n"
            "google-auth-httplib2==0.1.0\n"
            "google-api-python-client==2.95.0\n"
        ),

        ".env": (
            "SECRET_KEY=hospital-management-system-secret-key-2024\n"
            "FLASK_ENV=development\n"
            "DATABASE_URL=sqlite:///hospital.db\n"
            "GOOGLE_SHEETS_ENABLED=false\n"
        ),

        "README.md": (
            "# بيت المسيح\n\n"
            "نظام متكامل لإدارة المستشفيات والمؤسسات الطبية "
            "بلغة Python باستخدام Flask.\n\n"
            "## المميزات\n"
            "- تسجيل دخول متعدد المستويات (مدير، طبيب، ممرض، مشاهد)\n"
            "- إدارة المرضى والسجلات الطبية\n"
            "- جدولة الزيارات والمتابعة\n"
            "- تقارير وإحصائيات\n\n"
            "## متطلبات التشغيل\n"
            "- Python 3.8 أو أحدث\n"
            "- pip\n\n"
            "## التثبيت\n"
            "1. قم بنسخ المشروع:\n"
            "git clone https://github.com/yourusername/hospital-management-system.git\n"
            "cd hospital-management-system\n\n"
            "2. تثبيت المتطلبات:\n"
            "pip install -r requirements.txt\n\n"
            "3. تشغيل النظام:\n"
            "python run.py\n"
        )
    }

    # إنشاء الملفات إن لم تكن موجودة
    for filename, content in config_files.items():
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ تم إنشاء ملف: {filename}")
        else:
            print(f"✓ الملف موجود مسبقًا: {filename}")


def main():
    """تشغيل التطبيق"""
    print("=== نظام إدارة المستشفى ===")

    if not check_dependencies():
        sys.exit(1)

    setup_environment()
    
    from database.db_handler import init_db
    print("جاري تهيئة قاعدة البيانات...")
    init_db()

    print("✓ تم الإعداد بنجاح")
    print("✓ تشغيل التطبيق...")
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
