# PythonAnywhere Deployment Guide

## خطوات نشر التطبيق على PythonAnywhere

### الخطوة 1: إنشاء حساب على PythonAnywhere
1. اذهب إلى https://www.pythonanywhere.com
2. انقر على "Sign up"
3. اختر الخطة المناسبة (Beginner هي مجانية)

### الخطوة 2: استنساخ المستودع
1. افتح console في PythonAnywhere
2. نسخ الأوامر التالية:

```bash
git clone https://github.com/david837838-byte/Mohammad-Wali.git
cd Mohammad-Wali
```

### الخطوة 3: إنشاء بيئة افتراضية (Virtual Environment)
```bash
mkvirtualenv --python=/usr/bin/python3.10 hospital_env
pip install -r requirements.txt
```

### الخطوة 4: تكوين Web App
1. اذهب إلى قائمة "Web" في لوحة التحكم
2. انقر على "Add a new web app"
3. اختر "Manual configuration" 
4. اختر Python 3.10
5. في خطوة WSGI configuration، ضع المسار التالي:
   `/home/{your-username}/Mohammad-Wali/wsgi.py`

### الخطوة 5: تحديث ملف WSGI
في لوحة التحكم، تحت Web Apps، اضغط على ملف WSGI وأضف:

```python
import sys
path = '/home/{your-username}/Mohammad-Wali'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### الخطوة 6: تعيين Virtual Environment
في الصفحة الخاصة بـ Web App:
1. انقر على "Virtualenv"
2. أدخل مسار البيئة الافتراضية: `/home/{your-username}/.virtualenvs/hospital_env`

### الخطوة 7: إعادة تحميل التطبيق
انقر على زر "Reload" الأخضر في الأعلى

### الخطوة 8: قاعدة البيانات
يمكنك استخدام SQLite المضمنة أو ربط قاعدة بيانات MySQL:
- سجل دخولك إلى لوحة التحكم
- اذهب إلى قسم Databases
- أنشئ قاعدة بيانات جديدة

### الخطوة 9: المتغيرات البيئية (Environment Variables)
إذا كان لديك متغيرات بيئية في `.env`:
```bash
# في console PythonAnywhere
cd ~/Mohammad-Wali
nano .env
# أضف متغيراتك البيئية
```

## عنوان التطبيق
بعد الانتهاء من جميع الخطوات، سيكون التطبيق متاحاً على:
`https://{your-username}.pythonanywhere.com`

## استكشاف الأخطاء
- افحص ملف Log في: Web → Log files
- استخدم "Bash console" لتنفيذ أوامر التشخيص
- تأكد من أن Virtual Environment محدد بشكل صحيح

## تحديث التطبيق
```bash
cd ~/Mohammad-Wali
git pull origin master
# أعد تحميل التطبيق من لوحة التحكم
```

---
**ملاحظة:** استبدل `{your-username}` باسم المستخدم الفعلي الخاص بك على PythonAnywhere
