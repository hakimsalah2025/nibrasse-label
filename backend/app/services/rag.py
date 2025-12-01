import google.generativeai as genai
from app.core.config import settings
from app.services.embedding import get_embedding
from app.services.vector_store import query_vectors

_gemini_configured = False

def configure_gemini():
    global _gemini_configured
    if not _gemini_configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_configured = True

def detect_language(text: str) -> str:
    """Detect the language of the query"""
    # Simple heuristic based on character sets
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    total_chars = len([c for c in text if c.isalpha()])
    
    if total_chars == 0:
        return "ar"  # Default to Arabic
    
    arabic_ratio = arabic_chars / total_chars
    
    if arabic_ratio > 0.3:
        return "ar"  # Arabic
    
    # Check for French specific words
    french_words = ['le', 'la', 'les', 'de', 'et', 'dans', 'pour', 'sont', 'peut', 'comment', 'quels', 'quel']
    text_lower = text.lower()
    if any(word in text_lower.split() for word in french_words):
        return "fr"  # French
    
    return "en"  # Default to English

def generate_answer(query: str, context: str, metadatas: list = None) -> str:
    configure_gemini()
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    
    # Detect query language
    lang = detect_language(query)
    
    # Language-specific instructions and formatting
    lang_config = {
        "ar": {
            "instruction": "أجب بالعربية الفصحى",
            "intro_label": "مقدمة",
            "refs_label": "المراجع:",
            "citations_label": "الاستشهادات الكاملة:"
        },
        "fr": {
            "instruction": "Répondez en français",
            "intro_label": "Introduction",
            "refs_label": "Références:",
            "citations_label": "Citations complètes:"
        },
        "en": {
            "instruction": "Answer in English",
            "intro_label": "Introduction",
            "refs_label": "References:",
            "citations_label": "Complete Citations:"
        }
    }
    
    lang_settings = lang_config.get(lang, lang_config["ar"])
    lang_prompt = lang_settings["instruction"]
    refs_label = lang_settings["refs_label"]
    citations_label = lang_settings["citations_label"]
    
    # Number each context chunk for reference with metadata
    context_chunks = context.split("\n\n---\n\n")
    numbered_context = ""
    source_titles = []
    
    for i, chunk in enumerate(context_chunks, 1):
        # Extract title from metadata if available
        if metadatas and i <= len(metadatas):
            # Use filename and clean it up (remove extension and special chars)
            filename = metadatas[i-1].get('filename', f'مصدر {i}')
            # Remove .txt extension and clean up the title
            title = filename.replace('.txt', '').replace('-', ' ').replace('_', ' ')
            
            # Get page number if available
            page_number = metadatas[i-1].get('page_number')
            if page_number:
                title_with_page = f"{title} (صفحة {page_number})"
            else:
                title_with_page = title
            
            source_titles.append(title_with_page)
            numbered_context += f"\n\n### [مصدر {i}: {title_with_page}]\n{chunk}\n"
        else:
            source_titles.append(f'مصدر {i}')
            numbered_context += f"\n\n### [مصدر {i}]\n{chunk}\n"


    
    prompt = f"""أنت باحث أكاديمي متخصص في تقديم إجابات موثقة بأسلوب علمي احترافي وواضح.

**تعليمات حاسمة:**

**IMPORTANT: {lang_prompt}**

**هيكل الإجابة المطلوب (التزم به بدقة):**

1. **ابدأ بمقدمة موجزة** (سطر أو سطرين):
   - قدم سياقاً عاماً للموضوع
   - لا تكتب كلمة "مقدمة" أو أي عنوان
   - اكتب المقدمة مباشرة

2. **اكتب الإجابة في فقرات منفصلة وواضحة**:
   كل فقرة تتكون من:
   - عدة جمل تشرح فكرة رئيسية بشكل مفصل
   - جملة تمهيدية للاقتباس (مثل: "وقد نصت المادة..." أو "حيث جاء في النص:" أو "وفي هذا السياق:")
   - الاقتباس الكامل في سطر منفصل بين علامتي تنصيص
   - رقم المرجع [N] في سطر جديد منفصل بعد الاقتباس
   
   **مثال للتنسيق الصحيح:**
   
   تُعد البيانات التدريبية أحد أهم العوامل المؤثرة في جودة نماذج الذكاء الاصطناعي، حيث تحدد مدى دقة النموذج وقدرته على التعميم.
   وقد أكدت الدراسات على هذه الأهمية بشكل واضح:
   "تُعتبر البيانات التدريبية من أهم العناصر التي تؤثر على أداء نماذج الذكاء الاصطناعي، حيث تحدد جودة هذه البيانات مدى دقة النموذج وقدرته على التعميم"
   [1]
   
   يشكل التحيز في البيانات خطراً كبيراً على عدالة القرارات الصادرة عن الأنظمة الذكية، مما يتطلب اهتماماً خاصاً بجودة البيانات المستخدمة.
   وفي هذا الصدد، حذرت الأبحاث من المخاطر المحتملة:
   "عندما تحتوي البيانات التدريبية على تحيزات معينة، فإن النموذج المُدرَّب عليها سيعكس هذه التحيزات في نتائجه، مما قد يؤدي إلى قرارات غير عادلة"
   [1]

3. **قائمة المراجع**:
   بعد الفقرات، اترك سطراً فارغاً ثم اكتب:
   
   **{refs_label}**
   [1] عنوان المصدر الأول (مع رقم الصفحة إن وُجد)
   [2] عنوان المصدر الثاني (مع رقم الصفحة إن وُجد)

**قواعد صارمة:**
- **لا تكتب عناوين أو تسميات** داخل الإجابة (مثل "مقدمة" أو "الفكرة الأولى")
- **الاقتباس في سطر منفصل** - ليس في نفس سطر الشرح
- **استخدم جملة تمهيدية قبل كل اقتباس** لتقديم السياق
- **افصل الفقرات بسطر فارغ** لوضوح أفضل
- **المقدمة إلزامية** لكن بدون عنوان
- **اكتب فقرات مفصلة** - اشرح السياق جيداً قبل الاقتباس
- **أضف رقم الصفحة** في قائمة المراجع إذا كان موجوداً في عنوان المصدر أعلاه
- لا تخترع معلومات غير موجودة في المصادر
- اقتبس بشكل دقيق من المصادر المقدمة

**المصادر المتاحة:**
{numbered_context}

**السؤال:**
{query}

**الإجابة (التزم بالتنسيق المطلوب):**
"""
    response = model.generate_content(prompt)
    answer = response.text
    
    # Post-processing: فصل المراجع [N] عن الاقتباسات
    import re
    # البحث عن نمط: "نص" [رقم] واستبداله بـ "نص"\n[رقم]
    # نبحث عن علامة تنصيص متبوعة بمسافة ثم [رقم]
    answer = re.sub(r'(["\u201d\u201c»])\s*(\[\d+\])', r'\1\n\2', answer)
    
    return answer

def calculate_relevance_score(query: str, document: str) -> float:
    """Calculate relevance score using keyword overlap"""
    query_words = set(query.lower().split())
    doc_words = set(document.lower().split())
    
    if len(query_words) == 0:
        return 0.0
    
    # Jaccard similarity
    intersection = query_words.intersection(doc_words)
    union = query_words.union(doc_words)
    
    return len(intersection) / len(union) if len(union) > 0 else 0.0

def rerank_with_gemini(query: str, chunks: list[str], top_k: int = 3) -> list[tuple[str, float]]:
    """
    Use Gemini to re-rank chunks based on relevance to query.
    Returns list of (chunk, score) tuples sorted by relevance.
    """
    configure_gemini()
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    
    # Prepare chunks for evaluation
    chunks_text = ""
    for i, chunk in enumerate(chunks[:10], 1):  # Evaluate top 10 only
        chunks_text += f"\n\n### Chunk {i}:\n{chunk[:500]}...\n"  # Limit chunk size
    
    prompt = f"""قيّم مدى صلة كل chunk بالسؤال التالي. أعط درجة من 0 إلى 10 لكل chunk.

**السؤال:**
{query}

**Chunks:**
{chunks_text}

**التعليمات:**
- أعط درجة 10 إذا كان الـ chunk يجيب مباشرة على السؤال
- أعط درجة 5-9 إذا كان الـ chunk ذو صلة جزئية
- أعط درجة 0-4 إذا كان الـ chunk غير ذي صلة

**الإجابة المطلوبة (JSON فقط):**
```json
{{
  "1": 8,
  "2": 3,
  "3": 9,
  ...
}}
```
"""
    
    try:
        response = model.generate_content(prompt)
        # Extract JSON from response
        import json
        import re
        
        # Find JSON in response
        json_match = re.search(r'\{[^}]+\}', response.text)
        if json_match:
            scores = json.loads(json_match.group())
            
            # Create ranked list
            ranked = []
            for i, chunk in enumerate(chunks[:10], 1):
                score = float(scores.get(str(i), 0)) / 10.0  # Normalize to 0-1
                ranked.append((chunk, score))
            
            # Add remaining chunks with low score
            for chunk in chunks[10:]:
                ranked.append((chunk, 0.1))
            
            # Sort by score
            ranked.sort(key=lambda x: x[1], reverse=True)
            return ranked[:top_k]
        else:
            # Fallback: return top chunks as-is
            return [(chunk, 0.5) for chunk in chunks[:top_k]]
            
    except Exception as e:
        print(f"Re-ranking error: {e}")
        # Fallback: return top chunks as-is
        return [(chunk, 0.5) for chunk in chunks[:top_k]]

def rag_pipeline(query: str):
    from app.services.query_expansion import expand_query
    
    # 1. Expand query for better coverage (activate for queries with 10 words or less)
    queries = expand_query(query) if len(query.split()) <= 10 else [query]
    print(f"Searching with {len(queries)} query variations...")
    
    # 2. Search with all query variations and collect results
    all_documents = []
    all_distances = []
    all_metadatas = []
    
    for q in queries:
        # Embed Query with correct task_type
        query_embedding = get_embedding(q, is_query=True)
        
        # Retrieve from Supabase (pgvector)
        # Returns list of dicts: [{'content': '...', 'metadata': {...}, 'similarity': 0.85}, ...]
        results = query_vectors(query_embedding, match_count=20)
        
        # Collect results
        for res in results:
            all_documents.append(res['content'])
            # Convert similarity to distance-like score for RRF (1 - similarity) or just use similarity
            # RRF expects rank, so raw score matters less, but let's keep it consistent
            # Supabase returns similarity (1 is identical). Chroma returned distance (0 is identical).
            # We will use similarity directly for scoring if needed, or invert for distance.
            # Let's store similarity as score.
            all_distances.append(1 - res['similarity']) # Fake distance for compatibility if needed
            all_metadatas.append(res['metadata'])
    
    # 3. Hybrid Search (Vector + BM25) with Reciprocal Rank Fusion (RRF)
    from app.services.bm25_service import bm25_service
    
    # Get BM25 results (Increased to 20 to capture more candidates)
    bm25_results = bm25_service.search(query, top_k=20)
    
    # RRF Constants
    k = 60
    doc_scores = {}
    doc_metadatas = {}
    
    # Process Vector Results (Weight: 0.3)
    vector_weight = 0.3
    for rank, (doc, dist, meta) in enumerate(zip(all_documents, all_distances, all_metadatas)):
        if doc not in doc_scores:
            doc_scores[doc] = 0
            doc_metadatas[doc] = meta
        # Vector rank contribution
        doc_scores[doc] += vector_weight * (1 / (k + rank + 1))
        
    # Process BM25 Results (Weight: 0.7)
    bm25_weight = 0.7
    for rank, (doc, score, meta) in enumerate(bm25_results):
        if doc not in doc_scores:
            doc_scores[doc] = 0
            doc_metadatas[doc] = meta
        # BM25 rank contribution
        doc_scores[doc] += bm25_weight * (1 / (k + rank + 1))
    
    # Sort by RRF score
    ranked_items = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Take top 15 for re-ranking (Optimized for speed/accuracy balance)
    top_10_documents = [doc for doc, score in ranked_items[:15]]
    top_10_metadatas = [doc_metadatas[doc] for doc, score in ranked_items[:15]]
    
    # Create a map of chunk -> metadata for reliable retrieval
    chunk_to_meta = {doc: meta for doc, meta in zip(top_10_documents, top_10_metadatas)}
    
    # 5. Re-rank with Gemini for better accuracy
    reranked = rerank_with_gemini(query, top_10_documents, top_k=5)
    
    # Extract documents and find their metadata
    final_documents = []
    final_metadatas = []
    for chunk, score in reranked:
        final_documents.append(chunk)
        # Retrieve metadata using the map, defaulting to empty dict if not found (unlikely)
        final_metadatas.append(chunk_to_meta.get(chunk, {}))
    
    context = "\n\n---\n\n".join(final_documents)
    
    # 6. Generate Answer with metadata
    answer = generate_answer(query, context, final_metadatas)
    
    return {
        "query": query,
        "context": final_documents,
        "metadatas": final_metadatas,
        "answer": answer
    }

def summarize_text(text: str) -> str:
    """Generate a concise summary of the provided text"""
    configure_gemini()
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    
    prompt = f"""قم بتلخيص النص التالي في نقاط رئيسية مركزة وواضحة.
الهدف هو استخراج أهم المعلومات والأفكار الواردة في النص.

**النص:**
{text}

**الملخص:**
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Summarization error: {e}")
        return "عذراً، لم أتمكن من تلخيص النص. يرجى المحاولة مرة أخرى."

