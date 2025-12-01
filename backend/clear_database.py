"""
Script لإفراغ قاعدة البيانات بالكامل (Supabase + ChromaDB + BM25)
بدون إعادة بناء - فقط مسح كل شيء
"""
import os
import shutil
from pathlib import Path
from app.services.database import get_supabase

def clear_database():
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║    🗑️  مسح قاعدة البيانات - Clear Database                   ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    
    # تحذير
    print("⚠️  تحذير: هذه العملية ستمسح جميع البيانات!")
    print("   Warning: This will delete ALL data!")
    print()
    response = input("هل أنت متأكد؟ اكتب 'نعم' أو 'yes' للمتابعة: ")
    
    if response.lower() not in ['نعم', 'yes', 'y']:
        print("❌ تم الإلغاء - Cancelled")
        return
    
    print()
    print("🔄 بدء عملية المسح...")
    print()
    
    # 1. مسح ChromaDB
    chroma_path = Path("data/chroma_db")
    if chroma_path.exists():
        print("🗑️  [1/3] مسح ChromaDB...")
        try:
            shutil.rmtree(chroma_path)
            print("   ✅ تم مسح ChromaDB بنجاح")
        except PermissionError:
            print("   ❌ خطأ: لا يمكن مسح الملفات لأنها قيد الاستخدام!")
            print("   ⚠️  يرجى إغلاق التطبيق (النافذة السوداء) أولاً ثم المحاولة مرة أخرى.")
            print("   Error: Files are in use. Please STOP the application first.")
        except Exception as e:
            print(f"   ⚠️  خطأ في مسح ChromaDB: {e}")
    else:
        print("ℹ️  [1/3] ChromaDB فارغة بالفعل")
    
    # 2. مسح BM25 Index
    bm25_path = Path("data/bm25_index.pkl")
    if bm25_path.exists():
        print("🗑️  [2/3] مسح BM25 Index...")
        try:
            bm25_path.unlink()
            print("   ✅ تم مسح BM25 Index بنجاح")
        except Exception as e:
            print(f"   ⚠️  خطأ في مسح BM25: {e}")
    else:
        print("ℹ️  [2/3] BM25 Index فارغ بالفعل")
    
    # 3. مسح Supabase
    print("🗑️  [3/3] مسح جداول Supabase...")
    supabase = get_supabase()
    try:
        # مسح جدول chunks أولاً (لأنه يعتمد على documents)
        try:
            result = supabase.table("chunk").delete().neq("id", 0).execute()
            print(f"   ✅ تم مسح جدول chunks (تم حذف {len(result.data) if result.data else 0} سجل)")
        except Exception as e:
            print(f"   ⚠️  خطأ في مسح chunks: {e}")
        
        # مسح جدول documents
        try:
            result = supabase.table("documents").delete().neq("id", 0).execute()
            print(f"   ✅ تم مسح جدول documents (تم حذف {len(result.data) if result.data else 0} سجل)")
        except Exception as e:
            print(f"   ⚠️  خطأ في مسح documents: {e}")
            
    except Exception as e:
        print(f"   ⚠️  خطأ في الاتصال بـ Supabase: {e}")
    
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║  ✅ اكتملت عملية المسح!                                       ║")
    print("║     Database cleared successfully!                           ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    else:
        # مسح كل شيء
        clear_database()
