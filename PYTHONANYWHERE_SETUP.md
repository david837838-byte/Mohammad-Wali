# تعليمات نشر بيت المسيح على PythonAnywhere

## خطوات النشر:

### 1. إنشاء حساب على PythonAnywhere
- ادخل إلى https://www.pythonanywhere.com
- أنشئ حساباً مجاني أو مدفوع

### 2. تحميل الملفات
```bash
# استخدم git أو الرفع المباشر
git clone https://github.com/your-repo/hospital-management.git
cd hospital-management
```

### 3. إنشاء وتفعيل Python Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.9 hospital
workon hospital
pip install -r requirements.txt
```

### 4. إنشاء قاعدة بيانات PostgreSQL
- ادخل إلى Databases في PythonAnywhere
- أنشئ قاعدة بيانات جديدة
- احصل على DATABASE_URL

### 5. تحديث ملف .env
```bash
# على PythonAnywhere
nano .env
```

غيّر:
```
DATABASE_URL=postgresql://username:password@your-host.postgres.pythonanywhere-services.com/database_name
FLASK_ENV=production
```

### 6. إنشاء Web App
1. انقر على "Web" في لوحة التحكم
2. اختر "Add a new web app"
3. اختر "Manual configuration"
4. اختر Python 3.9
5. في خطوة WSGI configuration، استخدم:

```python
import sys
import os

# إضافة المسار
path = '/home/your_username/hospital-management'
if path not in sys.path:
    sys.path.append(path)

# تحميل متغيرات البيئة
from dotenv import load_dotenv
load_dotenv()

# استيراد التطبيق
from app import app
application = app
```

### 7. إعادة تحميل الموقع
- انقر على الزر "Reload" في صفحة Web

### 8. تهيئة قاعدة البيانات
```bash
# في bash console على PythonAnywhere
cd hospital-management
python3
>>> from database.db_handler import init_db
>>> init_db()
>>> exit()
```

### 9. البيانات الافتراضية
```bash
python3
>>> from database.db_handler import seed_sample_data
>>> seed_sample_data()
>>> exit()
```

## معلومات تسجيل الدخول الافتراضية:
- **اسم المستخدم:** admin
- **كلمة المرور:** admin123

## ملاحظات مهمة:

1. **قاعدة البيانات:**
   - استخدم PostgreSQL لقابلية الأداء الأفضل
   - تأكد من اتصالك الآمن

2. **الملفات الثابتة:**
   - يجب إضافة static files إلى PythonAnywhere
   - في صفحة Web، أضف: `/static/` -> `/home/your_username/hospital-management/static/`

3. **Session:**
   - تأكد من وجود مجلد `flask_session`
   - امنح صلاحيات القراءة/الكتابة

4. **البريد الإلكتروني (اختياري):**
   - إذا أردت إرسال بريد إلكتروني، استخدم SendGrid أو Mailgun

5. **HTTPS:**
   - أضف شهادة SSL من Let's Encrypt المدمجة

## استكشاف الأخطاء:
- افتح "Error log" في صفحة Web للاطلاع على الأخطاء
- تحقق من "Server log" للمزيد من التفاصيل

## دعم قاعدة البيانات:

### SQLite (افتراضي - محلي فقط)
```
DATABASE_URL=sqlite:///hospital.db
```

### PostgreSQL (موصى به للإنتاج)
```
DATABASE_URL=postgresql://user:password@host:5432/database
pip install psycopg2-binary
```

## نصائح الأمان:

1. غيّر `SECRET_KEY` إلى قيمة عشوائية قوية
2. استخدم كلمات مرور قوية للمسؤول
3. فعّل HTTPS دائماً
4. حدّث المكتبات بانتظام
5. استخدم متغيرات البيئة للمعلومات الحساسة
