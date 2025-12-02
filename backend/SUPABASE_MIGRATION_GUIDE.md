# 🔄 دليل الهجرة إلى Supabase جديد

## 📋 الخطوات الكاملة

### 1️⃣ إنشاء الـ Schema في Supabase الجديد

#### الطريقة الأولى: SQL Editor (موصى بها)

1. افتح Dashboard الجديد في Supabase
2. انتقل إلى **SQL Editor** من القائمة الجانبية
3. اضغط على **New Query**
4. انسخ السكريبت التالي كاملاً
5. اضغط **Run** أو `Ctrl+Enter`

#### السكريبت الكامل:

```sql
-- =====================================================
-- NIBRASSE RAG System - Supabase Schema
-- =====================================================
-- تاريخ الإنشاء: 26 نوفمبر 2025
-- الإصدار: 1.0.0
-- =====================================================

-- 1. إنشاء جدول المستندات (Documents)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT NOW(),
    total_chunks INTEGER DEFAULT 0,
    file_size INTEGER,
    file_type TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. إنشاء جدول الأجزاء النصية (Chunks)
CREATE TABLE IF NOT EXISTS chunk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- 3. إنشاء الـ Indexes لتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunk(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index ON chunk(chunk_index);
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date);

-- 4. إنشاء Function لتحديث updated_at تلقائياً
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. إنشاء Trigger لجدول documents
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. إضافة تعليقات توضيحية للجداول
COMMENT ON TABLE documents IS 'جدول المستندات المرفوعة في نظام NIBRASSE RAG';
COMMENT ON TABLE chunk IS 'جدول الأجزاء النصية (chunks) المستخرجة من المستندات';

COMMENT ON COLUMN documents.id IS 'المعرف الفريد للمستند';
COMMENT ON COLUMN documents.filename IS 'اسم الملف الأصلي';
COMMENT ON COLUMN documents.upload_date IS 'تاريخ ووقت رفع الملف';
COMMENT ON COLUMN documents.total_chunks IS 'عدد الأجزاء المستخرجة من المستند';
COMMENT ON COLUMN documents.file_size IS 'حجم الملف بالبايت';
COMMENT ON COLUMN documents.file_type IS 'نوع الملف (txt, pdf, docx)';

COMMENT ON COLUMN chunk.id IS 'المعرف الفريد للجزء النصي';
COMMENT ON COLUMN chunk.document_id IS 'مرجع للمستند الأصلي';
COMMENT ON COLUMN chunk.chunk_index IS 'رقم الجزء ضمن المستند';
COMMENT ON COLUMN chunk.content IS 'محتوى الجزء النصي';
COMMENT ON COLUMN chunk.embedding_id IS 'معرف الـ embedding في ChromaDB';
COMMENT ON COLUMN chunk.metadata IS 'بيانات إضافية (JSON)';

-- 7. عرض معلومات النجاح
DO $$
BEGIN
    RAISE NOTICE 'تم إنشاء Schema بنجاح!';
    RAISE NOTICE 'الجداول المنشأة: documents, chunk';
    RAISE NOTICE 'الـ Indexes المنشأة: 4 indexes';
    RAISE NOTICE 'الـ Triggers المنشأة: update_documents_updated_at';
END $$;
```

---

### 2️⃣ التحقق من نجاح الإنشاء

بعد تشغيل السكريبت، تحقق من:

#### ✅ الجداول:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('documents', 'chunk');
```

يجب أن ترى:
- `documents`
- `chunk`

#### ✅ الـ Indexes:
```sql
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('documents', 'chunk');
```

#### ✅ الـ Triggers:
```sql
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';
```

---

### 3️⃣ تحديث ملف `.env` في التطبيق

عندما تريد الهجرة للحساب الجديد، غيّر في `backend/.env`:

```env
# Supabase الجديد
VITE_SUPABASE_URL=https://your-new-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-new-anon-key-here
```

**مهم:** احصل على:
- **Project URL** من: Settings → API → Project URL
- **Anon Key** من: Settings → API → Project API keys → anon/public

---

### 4️⃣ اختبار الاتصال

بعد تحديث `.env`، اختبر الاتصال:

```python
# في backend directory
python -c "
from app.services.database import get_supabase
supabase = get_supabase()
result = supabase.table('documents').select('*').execute()
print('✅ الاتصال ناجح!' if result else '❌ فشل الاتصال')
"
```

---

## 🔄 خطوات الهجرة الكاملة

### إذا أردت نقل البيانات الموجودة:

#### 1. **تصدير البيانات من Supabase القديم:**

```sql
-- في SQL Editor للحساب القديم
COPY (SELECT * FROM documents) TO STDOUT WITH CSV HEADER;
COPY (SELECT * FROM chunk) TO STDOUT WITH CSV HEADER;
```

أو استخدم Supabase Dashboard:
- Table Editor → documents → Export as CSV
- Table Editor → chunk → Export as CSV

#### 2. **استيراد البيانات للحساب الجديد:**

في SQL Editor للحساب الجديد:

```sql
-- مثال لاستيراد documents
-- (يجب أن يكون الملف CSV محفوظاً محلياً)
-- استخدم Table Editor → Import data from CSV
```

#### 3. **نقل ChromaDB:**

```cmd
# انسخ مجلد ChromaDB
xcopy /E /I d:\arabic_rag\nibrasse-finale-v01-1.0.0\backend\data\chroma_db d:\backup\chroma_db
```

#### 4. **نقل BM25 Index:**

```cmd
# انسخ ملف BM25
copy d:\arabic_rag\nibrasse-finale-v01-1.0.0\backend\data\bm25_index.pkl d:\backup\
```

---

## 🧪 اختبار الهجرة

### قبل التشغيل الكامل:

1. **تحديث `.env` للحساب الجديد**
2. **تشغيل التطبيق:**
   ```cmd
   start_app.bat
   ```
3. **رفع ملف تجريبي:**
   - افتح http://localhost:8000
   - ارفع ملف txt صغير
   - تأكد من نجاح الرفع

4. **اختبار الاستعلام:**
   - اطرح سؤالاً
   - تأكد من الحصول على إجابة

---

## ⚠️ ملاحظات مهمة

### 🔐 الأمان:
- ✅ لا تشارك `SUPABASE_ANON_KEY` مع أحد
- ✅ احتفظ بنسخة من `.env` القديم كـ `.env.backup`
- ✅ استخدم Row Level Security في Supabase:

```sql
-- تفعيل RLS على الجداول
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunk ENABLE ROW LEVEL SECURITY;

-- سياسة للقراءة (مثال)
CREATE POLICY "Enable read access for all users" ON documents
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON chunk
    FOR SELECT USING (true);
```

### 📊 الأداء:
- ✅ الـ Indexes موجودة بالفعل (تم إنشاءها في السكريبت)
- ✅ إذا كانت البيانات كثيرة (>10,000 chunk)، فكر في:
  - Partitioning
  - Additional indexes على metadata

### 🔄 Rollback (العودة للقديم):
إذا حدثت مشكلة، ببساطة:

```env
# في .env، أعد القيم القديمة:
VITE_SUPABASE_URL=https://old-project.supabase.co
VITE_SUPABASE_ANON_KEY=old-anon-key
```

---

## 📝 Checklist الهجرة

قبل الهجرة النهائية:

- [ ] تشغيل السكريبت في Supabase الجديد
- [ ] التحقق من إنشاء الجداول
- [ ] التحقق من الـ Indexes
- [ ] تحديث `.env` بالمفاتيح الجديدة
- [ ] اختبار رفع ملف
- [ ] اختبار الاستعلام
- [ ] نسخ احتياطي من ChromaDB و BM25
- [ ] (اختياري) نقل البيانات القديمة

---

## 🆘 حل المشاكل

### مشكلة: "relation already exists"
**الحل:** الجداول موجودة مسبقاً. استخدم:
```sql
DROP TABLE IF EXISTS chunk;
DROP TABLE IF EXISTS documents;
-- ثم أعد تشغيل السكريبت
```

### مشكلة: "permission denied"
**الحل:** تأكد من أنك مسجل دخول كـ Owner للمشروع

### مشكلة: "cannot connect to database"
**الحل:** 
1. تحقق من اتصال الإنترنت
2. تحقق من صحة SUPABASE_URL و SUPABASE_ANON_KEY
3. تحقق من أن المشروع active في Supabase

---

**تم إنشاء الدليل بواسطة:** Antigravity AI  
**التاريخ:** 26 نوفمبر 2025  
**الإصدار:** 1.0.0
