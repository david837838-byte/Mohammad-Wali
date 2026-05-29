// ملف JavaScript الرئيسي

document.addEventListener('DOMContentLoaded', function() {
    // تهيئة التواريخ
    initializeDates();
    
    // إعداد معالجات الأحداث
    setupEventListeners();
    
    // إعداد اختيار الدور في صفحة تسجيل الدخول
    setupRoleSelection();
    
    // إعداد النافذة المنبثقة للحذف
    setupDeleteModal();
    
    // تحديث الإحصائيات تلقائياً كل دقيقة
    setInterval(updateStats, 60000);
});

// تهيئة التواريخ
function initializeDates() {
    const dateElements = document.querySelectorAll('.current-date, #currentDate');
    if (dateElements.length > 0) {
        const now = new Date();
        const days = ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
        const months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 
                       'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];
        
        const dayName = days[now.getDay()];
        const day = now.getDate();
        const month = months[now.getMonth()];
        const year = now.getFullYear();
        
        const formattedDate = `${dayName} ${day} ${month} ${year}`;
        
        dateElements.forEach(el => {
            el.textContent = formattedDate;
        });
    }
}

// إعداد اختيار الدور
function setupRoleSelection() {
    const roleOptions = document.querySelectorAll('.role-option');
    
    roleOptions.forEach(option => {
        option.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                
                roleOptions.forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
            }
        });
    });
}

// إعداد النافذة المنبثقة للحذف
function setupDeleteModal() {
    const deleteModal = document.getElementById('deleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const modalCloseBtn = document.querySelector('.modal-close');
    
    if (deleteModal && cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', function() {
            deleteModal.style.display = 'none';
        });
        
        if (modalCloseBtn) {
            modalCloseBtn.addEventListener('click', function() {
                deleteModal.style.display = 'none';
            });
        }
        
        // إغلاق النافذة المنبثقة عند النقر خارجها
        window.addEventListener('click', function(e) {
            if (e.target === deleteModal) {
                deleteModal.style.display = 'none';
            }
        });
    }
}

// تأكيد الحذف
function confirmDelete(type, id, name) {
    const deleteModal = document.getElementById('deleteModal');
    const deleteMessage = document.getElementById('deleteMessage');
    const deleteForm = document.getElementById('deleteForm');
    const deleteItemType = document.getElementById('deleteItemType');
    const deleteItemId = document.getElementById('deleteItemId');
    
    if (deleteModal && deleteMessage && deleteForm && deleteItemType && deleteItemId) {
        const typeNames = {
            'patient': 'المريض',
            'user': 'المستخدم',
            'medical_record': 'السجل الطبي',
            'visit': 'الزيارة'
        };
        
        deleteMessage.textContent = `هل أنت متأكد من رغبتك في حذف ${typeNames[type] || 'العنصر'} "${name}"؟`;
        deleteItemType.value = type;
        deleteItemId.value = id;
        
        // بناء الـ action URL بناءً على النوع
        let actionUrl = '';
        if (type === 'medical_record') {
            actionUrl = `/medical/${id}/delete`;
        } else if (type === 'visit') {
            actionUrl = `/visits/${id}/delete`;
        } else if (type === 'patient') {
            actionUrl = `/patients/${id}/delete`;
        } else if (type === 'user') {
            actionUrl = `/users/${id}/delete`;
        }
        
        deleteForm.action = actionUrl;
        deleteModal.style.display = 'flex';
    }
}

// تحديث الإحصائيات
function updateStats() {
    const dashboardPage = document.getElementById('dashboardPage');
    
    if (dashboardPage && dashboardPage.style.display !== 'none') {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                if (data.total_patients !== undefined) {
                    document.getElementById('totalPatients').textContent = data.total_patients;
                }
                if (data.total_doctors !== undefined) {
                    document.getElementById('totalDoctors').textContent = data.total_doctors;
                }
                if (data.total_users !== undefined) {
                    document.getElementById('totalUsers').textContent = data.total_users;
                }
                if (data.today_visits !== undefined) {
                    document.getElementById('todayVisits').textContent = data.today_visits;
                }
            })
            .catch(error => console.error('خطأ في تحديث الإحصائيات:', error));
    }
}

// إعداد معالجات الأحداث
function setupEventListeners() {
    // إخفاء التنبيهات تلقائياً بعد 5 ثوانٍ
    const notifications = document.querySelectorAll('.notification.show');
    notifications.forEach(notification => {
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.style.display = 'none';
            }, 300);
        }, 5000);
    });
    
    // البحث في جداول المرضى
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.table-container')?.querySelector('tbody');
            
            if (table) {
                const rows = table.querySelectorAll('tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });
    
    // تحميل زيارات اليوم
    const visitsPage = document.getElementById('visitsPage');
    if (visitsPage && visitsPage.style.display !== 'none') {
        fetch('/visits/api/today')
            .then(response => response.json())
            .then(data => {
                console.log('زيارات اليوم:', data);
            })
            .catch(error => console.error('خطأ في جلب زيارات اليوم:', error));
    }
    
    // التحقق من صحة كلمات المرور
    const passwordForms = document.querySelectorAll('form input[type="password"]');
    passwordForms.forEach(input => {
        const confirmInput = document.getElementById('userConfirmPassword');
        if (confirmInput && input.id === 'userPassword') {
            input.addEventListener('input', function() {
                if (this.value !== confirmInput.value) {
                    confirmInput.style.borderColor = 'var(--danger)';
                } else {
                    confirmInput.style.borderColor = 'var(--light-gray)';
                }
            });
        }
    });
}

// عرض رسالة تنبيه
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} show`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

// تصدير البيانات إلى Excel
function exportToExcel(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let html = table.outerHTML;
    
    // إنشاء ملف Excel
    const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'data.xls';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// البحث عن المرضى (لأتمتة الاستكمال)
function searchPatients(query) {
    if (!query || query.length < 2) return;
    
    fetch(`/patients/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            console.log('نتائج البحث:', data);
        })
        .catch(error => console.error('خطأ في البحث:', error));
}