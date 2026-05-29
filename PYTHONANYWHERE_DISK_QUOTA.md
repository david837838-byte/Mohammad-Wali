# PythonAnywhere Disk Quota Management

## مشكلة: Disk quota exceeded

عند النشر على PythonAnywhere، قد تواجه خطأ `OSError: [Errno 122] Disk quota exceeded` لأن مساحة التخزين محدودة.

## ✅ الحل:

### 1. حذف الملفات غير الضرورية

```bash
cd ~/Mohammad-Wali

# حذف مجلدات Python الوسيطة
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# حذف ملفات جلسات Flask القديمة
rm -rf flask_session/*

# حذف قاعدة البيانات القديمة (إذا أردت إعادة تعيين)
# rm -f hospital.db
```

### 2. تنظيف Cache في PythonAnywhere

```bash
# مسح pip cache
pip cache purge

# أو استخدم النسخة الأقدم
pip install --no-cache-dir -r requirements-production.txt
```

### 3. معلومات استخدام القرص

```bash
# عرض استخدام المساحة
du -sh ~/*
df -h

# معرفة الملفات الكبيرة
find ~ -type f -size +10M -exec ls -lh {} \;
```

### 4. حذف الملفات المؤقتة

```bash
# حذف ملفات النسخ الاحتياطية
find . -name "*.bak" -delete
find . -name "*.tmp" -delete
find . -name "*.log" -delete

# حذف الملفات المرفوعة المؤقتة (إن لم تكن بحاجة إليها)
rm -rf static/uploads/*
```

### 5. تحسين حجم الملفات

```bash
# حذف الملفات المكررة في git
git gc --aggressive
```

---

## 📊 حدود التخزين على PythonAnywhere:

| الخطة | المساحة المتاحة |
|------|----------------|
| Beginner | 512 MB |
| Hacker | 2 GB |
| Professional | 20 GB |
| Premium | غير محدود |

---

## 💡 نصائح لتقليل استهلاك المساحة:

1. **قاعدة البيانات:** استخدم MySQL بدلاً من SQLite (يتم تخزينها منفصلة)
2. **الملفات المرفوعة:** انقل الملفات المرفوعة إلى خدمة تخزين سحابية (AWS S3, Google Cloud Storage)
3. **الصور:** ضغط الصور قبل الحفظ
4. **السجلات:** احذف ملفات السجلات القديمة بانتظام

---

## 🔄 تحديث بدون مشاكل:

```bash
cd ~/Mohammad-Wali

# سحب آخر نسخة
git pull origin master

# تنظيف المساحة
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# إعادة تثبيت المكتبات بدون cache
pip install --no-cache-dir --upgrade -r requirements-production.txt

# أعد تحميل التطبيق من لوحة التحكم
```

---

**ملاحظة:** إذا استمرت المشكلة، يمكنك الترقية إلى خطة أعلى على PythonAnywhere.
