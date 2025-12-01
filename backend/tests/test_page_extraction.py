"""
اختبار وحدوي لدالة استخراج أرقام الصفحات
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.ingestion import extract_page_number, chunk_text


def test_extract_page_number_ocr():
    """اختبار استخراج رقم الصفحة من تنسيق OCR الكامل"""
    text = "--- صفحة 256 (OCR) ---\nمحتوى الصفحة هنا"
    result = extract_page_number(text)
    assert result == "256", f"Expected '256', got '{result}'"
    print("✅ test_extract_page_number_ocr passed")


def test_extract_page_number_simple():
    """اختبار استخراج رقم الصفحة من تنسيق بسيط"""
    text = "--- صفحة 89 ---\nمحتوى هنا"
    result = extract_page_number(text)
    assert result == "89", f"Expected '89', got '{result}'"
    print("✅ test_extract_page_number_simple passed")


def test_extract_page_number_in_text():
    """اختبار استخراج رقم الصفحة من داخل النص"""
    text = "يُذكر في صفحة 123 أن المؤلف..."
    result = extract_page_number(text)
    assert result == "123", f"Expected '123', got '{result}'"
    print("✅ test_extract_page_number_in_text passed")


def test_extract_page_number_arabic_abbreviation():
    """اختبار استخراج رقم الصفحة مع الاختصار العربي"""
    text = "انظر ص 45 للمزيد"
    result = extract_page_number(text)
    assert result == "45", f"Expected '45', got '{result}'"
    print("✅ test_extract_page_number_arabic_abbreviation passed")


def test_extract_page_number_none():
    """اختبار عندما لا يوجد رقم صفحة"""
    text = "هذا نص عادي بدون رقم صفحة"
    result = extract_page_number(text)
    assert result is None, f"Expected None, got '{result}'"
    print("✅ test_extract_page_number_none passed")


def test_chunk_text_with_pages():
    """اختبار تقسيم النص مع الحفاظ على أرقام الصفحات"""
    content = """--- صفحة 1 (OCR) ---
النص الأول هنا في الصفحة الأولى.
يحتوي على عدة جمل.

--- صفحة 2 (OCR) ---
النص الثاني في الصفحة الثانية.
محتوى مختلف.
"""
    
    chunks = chunk_text(content)
    
    # التحقق من أن النتيجة list من dicts
    assert isinstance(chunks, list), "chunks should be a list"
    assert len(chunks) > 0, "Should have at least one chunk"
    assert isinstance(chunks[0], dict), "Each chunk should be a dict"
    
    # التحقق من المفاتيح
    required_keys = {'text', 'index', 'page_number', 'has_page_marker'}
    assert required_keys.issubset(chunks[0].keys()), f"Missing keys. Got: {chunks[0].keys()}"
    
    # التحقق من أن أول chunk له page_number
    first_chunk_with_page = next((c for c in chunks if c['page_number']), None)
    assert first_chunk_with_page is not None, "Should find a chunk with page_number"
    assert first_chunk_with_page['page_number'] in ['1', '2'], f"Page number should be 1 or 2, got {first_chunk_with_page['page_number']}"
    
    print(f"✅ test_chunk_text_with_pages passed - Found {len(chunks)} chunks")
    print(f"   First chunk with page: page {first_chunk_with_page['page_number']}")


def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("\n" + "="*50)
    print("🧪 Starting Page Number Extraction Tests")
    print("="*50 + "\n")
    
    try:
        test_extract_page_number_ocr()
        test_extract_page_number_simple()
        test_extract_page_number_in_text()
        test_extract_page_number_arabic_abbreviation()
        test_extract_page_number_none()
        test_chunk_text_with_pages()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50 + "\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
