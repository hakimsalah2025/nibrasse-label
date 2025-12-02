# 📘 Guide Technique NIBRASSE - Système RAG Avancé

## Vue d'ensemble du système

NIBRASSE est un système RAG (Retrieval-Augmented Generation) avancé optimisé pour les documents académiques en langue arabe, avec support multilingue (arabe, français, anglais).

**Version :** 1.1.0  
**Date :** 26 novembre 2025  
**Nouveauté :** Extraction automatique des numéros de page dans les citations

---

## 🏗️ Architecture du système

### Stack Technique

```
Frontend
├── HTML5 + CSS3 (Vanilla)
├── JavaScript (ES6+)
└── Interface responsive

Backend
├── FastAPI (Python 3.10+)
├── Uvicorn (Serveur ASGI)
└── Structure modulaire

Intelligence Artificielle
├── Google Gemini Pro (génération)
├── Gemini Embedding (vectorisation)
└── Gemini 1.5 Pro (reranking)

Bases de données
├── ChromaDB (base vectorielle)
├── Supabase (PostgreSQL)
└── BM25 (recherche lexicale)

Traitement de texte
├── LangChain (chunking)
├── RecursiveCharacterTextSplitter
└── Regex (extraction de métadonnées)
```

---

## 🔍 Pipeline RAG Détaillé

### 1. Ingestion des documents

```python
# Fichier: backend/app/services/ingestion.py

def process_document(file_path: str):
    """
    Processus complet d'ingestion:
    1. Lecture du fichier
    2. Extraction des numéros de page ✨ NOUVEAU
    3. Découpage intelligent (chunking)
    4. Génération des embeddings
    5. Stockage multi-base de données
    """
```

#### 1.1 Extraction des numéros de page (✨ Nouvelle fonctionnalité)

```python
def extract_page_number(text: str) -> str:
    """
    Extrait le numéro de page à partir de différents formats:
    - --- صفحة 123 (OCR) ---
    - --- صفحة 123 ---
    - صفحة 123
    - ص 123
    
    Retourne:
        str: Numéro de page ou None
    """
    patterns = [
        r'---\s*صفحة\s+(\d+)\s*\(OCR\)\s*---',
        r'---\s*صفحة\s+(\d+)\s*---',
        r'صفحة\s+(\d+)',
        r'ص\s*\.?\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None
```

**Logique d'attribution des pages:**
- Chaque chunk vérifie s'il contient une marque de page
- Si oui → enregistre ce numéro
- Si non → hérite du dernier numéro de page connu
- Résultat : continuité des numéros de page même en cas de chunks longs

#### 1.2 Chunking intelligent

```python
def chunk_text(text: str) -> list[dict]:
    """
    Découpage optimisé pour l'arabe:
    - Taille: 512 caractères (équilibre contexte/précision)
    - Chevauchement: 150 caractères (évite perte de contexte)
    - Séparateurs: priorité paragraphes > phrases > mots
    
    Retourne:
        Liste de dictionnaires avec:
        {
            "text": "contenu...",
            "index": 0,
            "page_number": "256",  # ✨ NOUVEAU
            "has_page_marker": True  # ✨ NOUVEAU
        }
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=150,
        separators=["\n\n", "\n", "。", ".", " ", ""]
    )
    
    text_chunks = text_splitter.split_text(text)
    
    current_page = None
    chunks_with_metadata = []
    
    for i, chunk in enumerate(text_chunks):
        page_num = extract_page_number(chunk)
        if page_num:
            current_page = page_num
        
        chunks_with_metadata.append({
            "text": chunk,
            "index": i,
            "page_number": current_page,
            "has_page_marker": bool(page_num)
        })
    
    return chunks_with_metadata
```

#### 1.3 Stockage multi-base

```python
# ChromaDB: Stockage vectoriel
metadatas = [{
    "document_id": doc_id,
    "chunk_index": i,
    "filename": filename,
    "page_number": chunk_dict.get("page_number"),  # ✨
    "has_page_marker": chunk_dict.get("has_page_marker")  # ✨
}]

add_documents_to_chroma(
    ids=chroma_ids,
    documents=chunks,
    metadatas=metadatas,
    embeddings=embeddings
)

# Supabase: Métadonnées structurées
supabase.table("chunk").insert({
    "document_id": doc_id,
    "chunk_index": i,
    "content": chunk_dict["text"],
    "embedding_id": chroma_ids[i],
    "metadata": {  # ✨ Stocké en JSON
        "page_number": chunk_dict.get("page_number"),
        "has_page_marker": chunk_dict.get("has_page_marker")
    }
})

# BM25: Index lexical
bm25_service.build_index(
    corpus=current_corpus,
    metadatas=current_metadatas
)
```

---

### 2. Recherche Hybride

```python
# Fichier: backend/app/services/rag.py

def hybrid_search(query: str, top_k: int = 10):
    """
    Recherche hybride combinant:
    1. Recherche sémantique (ChromaDB)
    2. Recherche lexicale (BM25)
    3. Fusion RRF (Reciprocal Rank Fusion)
    """
```

#### 2.1 Recherche sémantique

```python
# Vectorisation de la requête
query_embedding = get_embedding(query, is_query=True)

# Recherche dans ChromaDB
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    include=['documents', 'metadatas', 'distances']
)
```

#### 2.2 Recherche lexicale BM25

```python
# Tokenisation
tokenized_query = query.split(" ")

# Scoring BM25
bm25_scores = bm25_service.bm25.get_scores(tokenized_query)

# Top-k résultats
top_indices = np.argsort(bm25_scores)[::-1][:top_k]
```

#### 2.3 Fusion RRF

```python
def reciprocal_rank_fusion(results_list, k=60):
    """
    Formule RRF: score = Σ(1 / (k + rank))
    
    Avantages:
    - Sans paramètres à ajuster
    - Robuste aux différences d'échelle
    - Combine efficacement sources hétérogènes
    """
    fused_scores = {}
    for results in results_list:
        for rank, doc_id in enumerate(results):
            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0
            fused_scores[doc_id] += 1 / (k + rank + 1)
    
    return sorted(fused_scores.items(), 
                  key=lambda x: x[1], 
                  reverse=True)
```

---

### 3. Reranking avec Gemini

```python
def rerank_with_gemini(query: str, chunks: list, top_k: int = 3):
    """
    Utilise Gemini 1.5 Pro pour évaluer la pertinence:
    - Analyse sémantique profonde
    - Compréhension contextuelle
    - Scoring sur échelle 0-10
    """
    prompt = f"""Évalue la pertinence de chaque passage...
    
    Question: {query}
    
    Passages:
    {numbered_chunks}
    
    Retourne JSON: [{{"passage": 1, "score": 8.5}}, ...]
    """
    
    response = model.generate_content(prompt)
    scores = parse_scores(response.text)
    
    return sorted(scores, key=lambda x: x['score'], reverse=True)[:top_k]
```

---

### 4. Génération de réponse (✨ Amélioré)

```python
def generate_answer(query: str, context: str, metadatas: list) -> str:
    """
    Génère une réponse structurée avec citations et numéros de page
    """
```

#### 4.1 Préparation du contexte enrichi

```python
# ✨ Inclusion des numéros de page dans les titres
for i, chunk in enumerate(context_chunks, 1):
    filename = metadatas[i-1].get('filename', f'source {i}')
    title = filename.replace('.txt', '')
    
    # ✨ NOUVEAU: Ajout automatique du numéro de page
    page_number = metadatas[i-1].get('page_number')
    if page_number:
        title_with_page = f"{title} (page {page_number})"
    else:
        title_with_page = title
    
    numbered_context += f"\n### [Source {i}: {title_with_page}]\n{chunk}\n"
```

#### 4.2 Prompt engineering optimisé

```python
prompt = f"""Tu es un chercheur académique spécialisé...

**Instructions CRITIQUES pour les références:**
1. Utilise le format: [N] Titre (page X) quand disponible
2. Le numéro de page est indiqué dans le titre de chaque source ci-dessus
3. Si pas de numéro de page: [N] Titre seulement
4. Cite précisément, ne pas inventer

**Structure obligatoire:**
1. Introduction (2-3 lignes, sans titre)
2. Paragraphes avec citations:
   - Explication complète
   - Phrase d'introduction à la citation
   - Citation textuelle entre guillemets
   - Référence [N] sur ligne séparée
3. Liste des références:
   **Références:**
   [1] Titre (page X) si disponible
   [2] Titre (page Y) si disponible

**Sources disponibles:**
{numbered_context}

**Question:** {query}
"""
```

#### 4.3 Post-traitement

```python
# Séparation citations/références
answer = re.sub(
    r'(["\u201d\u201c»])\s*(\[\d+\])', 
    r'\1\n\2', 
    answer
)

# Formatage des listes
answer = answer.replace('- ', '\n- ')

return answer
```

---

## 📊 Performance et Optimisations

### Métriques clés

```
Temps de traitement (document moyen 50 pages):
├── Upload + OCR: ~2-3 secondes
├── Chunking + extraction pages: ~1-2 secondes
├── Embeddings (batch): ~3-5 secondes
├── Stockage DB: ~1-2 secondes
└── Total ingestion: ~7-12 secondes

Temps de requête:
├── Recherche hybride: ~0.5-1 seconde
├── Reranking Gemini: ~2-3 secondes
├── Génération réponse: ~5-10 secondes
└── Total query: ~8-15 secondes
```

### Optimisations implémentées

1. **Batch embeddings:** Vectorisation groupée pour réduire les appels API
2. **Caching:** Mise en cache des embeddings fréquents
3. **Index BM25:** Pré-calcul pour recherche instantanée
4. **Chunk size optimisé:** 512 caractères = équilibre contexte/précision
5. **Lazy loading:** Initialisation des modèles à la demande

---

## 🔧 Configuration et Déploiement

### Variables d'environnement

```env
# backend/.env

# API Keys
GEMINI_API_KEY=votre_cle_gemini
VITE_SUPABASE_URL=https://votre-projet.supabase.co
VITE_SUPABASE_ANON_KEY=votre_cle_anon

# Modèles Gemini
GEMINI_CHAT_MODEL=gemini-1.5-pro-002
GEMINI_EMBEDDING_MODEL=models/text-embedding-004

# Paramètres RAG
CHUNK_SIZE=512
CHUNK_OVERLAP=150
TOP_K_RESULTS=10
RERANK_TOP_K=3
```

### Structure des bases de données

#### Supabase Schema

```sql
-- Table documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT NOW(),
    total_chunks INTEGER DEFAULT 0,
    file_size INTEGER,
    file_type TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table chunks
CREATE TABLE chunk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB  -- ✨ Contient page_number et has_page_marker
);

-- Indexes pour performance
CREATE INDEX idx_chunks_document_id ON chunk(document_id);
CREATE INDEX idx_chunks_chunk_index ON chunk(chunk_index);
CREATE INDEX idx_documents_filename ON documents(filename);
```

#### ChromaDB Collections

```python
collection = client.get_or_create_collection(
    name="rag_collection",
    embedding_function=None,  # Embeddings pré-calculés
    metadata={"hnsw:space": "cosine"}
)

# Métadonnées stockées:
{
    "document_id": "uuid",
    "chunk_index": 0,
    "filename": "document.txt",
    "page_number": "256",  # ✨ NOUVEAU
    "has_page_marker": True  # ✨ NOUVEAU
}
```

---

## 🧪 Tests et Validation

### Tests unitaires

```python
# backend/tests/test_page_extraction.py

def test_extract_page_number_ocr():
    """Teste extraction format OCR complet"""
    text = "--- صفحة 256 (OCR) ---\nContenu..."
    assert extract_page_number(text) == "256"

def test_chunk_text_with_pages():
    """Teste chunking avec préservation numéros de page"""
    chunks = chunk_text(sample_content)
    assert all('page_number' in c for c in chunks)
    assert chunks[0]['page_number'] is not None
```

Lancer les tests:
```bash
cd backend
python tests/test_page_extraction.py
```

### Tests d'intégration

```bash
# Test du pipeline complet
python tests/test_full_rag_pipeline.py

# Test avec document réel
python tests/test_with_real_document.py
```

---

## 🔍 Débogage et Monitoring

### Logs détaillés

```python
# Dans ingestion.py
print(f"✅ Document processé: {filename}")
print(f"   - Chunks totaux: {len(chunks)}")
print(f"   - Chunks avec pages: {chunks_with_pages}")
print(f"   - Taux de couverture: {chunks_with_pages/len(chunks)*100:.1f}%")

# Dans rag.py
print(f"🔍 Recherche pour: {query}")
print(f"   - Résultats hybrides: {len(hybrid_results)}")
print(f"   - Après reranking: {len(reranked)}")
print(f"   - Numéros de page trouvés: {sum(1 for m in metadatas if m.get('page_number'))}")
```

### Endpoints de diagnostic

```python
# GET /api/stats - Statistiques système
{
    "total_documents": 42,
    "total_chunks": 1234,
    "chunks_with_pages": 987,
    "coverage_rate": "80.0%"
}

# GET /api/health - État du système
{
    "status": "healthy",
    "chromadb": "connected",
    "supabase": "connected",
    "bm25": "indexed"
}
```

---

## 📚 Références techniques

### Documentation externe

- **LangChain:** https://python.langchain.com/
- **ChromaDB:** https://docs.trychroma.com/
- **Supabase:** https://supabase.com/docs
- **Google Gemini:** https://ai.google.dev/docs

### Papiers de recherche

1. **RAG:** "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
2. **BM25:** "The Probabilistic Relevance Framework: BM25 and Beyond" (Robertson & Zaragoza, 2009)
3. **RRF:** "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods" (Cormack et al., 2009)

---

## 🔄 Roadmap Technique

### Version 1.2.0 (Planifiée)
- [ ] Support PDF natif (sans conversion)
- [ ] Extraction automatique de tables
- [ ] Amélioration chunking sémantique
- [ ] Cache Redis pour embeddings

### Version 1.3.0 (Future)
- [ ] Multi-modal (images + texte)
- [ ] Graphes de connaissances
- [ ] Fine-tuning modèle embedding
- [ ] API REST complète

---

**Maintenu par:** Équipe NIBRASSE  
**Dernière mise à jour:** 26 novembre 2025  
**Version:** 1.1.0
