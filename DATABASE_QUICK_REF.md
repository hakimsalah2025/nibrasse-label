# 🚀 مرجع سريع - إدارة قاعدة البيانات NIBRASSE

## 📋 الأوامر السريعة

### إفراغ كامل (توصية)
```cmd
clear_database.bat
```
✅ آمن (يطلب تأكيد)  
🗑️ يمسح: ChromaDB + BM25 + Supabase

---

### إفراغ جزئي

```cmd
# ChromaDB فقط
cd backend && python clear_database.py chroma

# BM25 فقط  
cd backend && python clear_database.py bm25

# Supabase فقط
cd backend && python clear_database.py supabase
```

---

### إعادة بناء من الملفات

```cmd
cd backend
python rebuild_database.py
```
📚 يعالج جميع ملفات `.txt` في `backend/data/`

---

## 🎯 سيناريوهات شائعة

### 🆕 بدء مشروع جديد
```cmd
1. stop_app.bat
2. clear_database.bat → نعم
3. start_app.bat
4. رفع مستندات من الواجهة
```

### 🔄 تحديث المستندات
```cmd
1. clear_database.bat → نعم
2. cd backend
3. python rebuild_database.py
```

### 🐛 إصلاح مشكلة بحث
```cmd
cd backend
python clear_database.py bm25
python rebuild_database.py
```

---

## 🗂️ مكونات قاعدة البيانات

| المكون | الموقع | الوظيفة |
|--------|---------|----------|
| **ChromaDB** | `backend/data/chroma_db/` | المتجهات (Embeddings) |
| **BM25** | `backend/data/bm25_index.pkl` | البحث الكلمات المفتاحية |
| **Supabase** | Cloud (PostgreSQL) | البيانات الوصفية |

---

## ⚠️ قبل المسح

- ☑️ أوقف التطبيق (`stop_app.bat`)
- ☑️ انسخ البيانات المهمة
- ☑️ تأكد من وجود نسخة احتياطية

---

## 📚 التوثيق الكامل

راجع: `DATABASE_CLEAR_GUIDE_AR.md`
