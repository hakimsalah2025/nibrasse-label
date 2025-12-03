import shutil
import os
import uuid
import re
from fastapi import UploadFile, HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.embedding import get_batch_embeddings
# from app.services.vector_store import add_documents_to_chroma (Removed)
from app.services.database import insert_document_record, insert_chunks_records

def extract_page_number(text: str) -> str:
    """
    Extract page number from text using regex patterns.
    """
    patterns = [
        r'---\s*صفحة\s+(\d+)\s*\(OCR\)\s*---',
        r'---\s*(?:Page|page|PAGE)\s+(\d+)\s*\(OCR\)\s*---',
        r'---\s*صفحة\s+(\d+)\s*---',
        r'---\s*(?:Page|page|PAGE)\s+(\d+)\s*---',
        r'صفحة\s+(\d+)',
        r'ص\s*\.?\s*(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

def chunk_text(text: str) -> list[dict]:
    """
    Split text into chunks and extract page numbers.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=150,
        separators=["\n\n", "\n", "。", ".", " ", ""],
        length_function=len,
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

def process_file_content(content: str, filename: str):
    """
    Process file content directly from memory (no local file saving).
    """
    # 1. Chunk text
    chunks_with_metadata = chunk_text(content)
    total_chunks = len(chunks_with_metadata)
    
    # 2. Create Document record in Supabase
    doc_record = insert_document_record(filename, total_chunks)
    document_id = doc_record['id']
    
    # 3. Prepare chunks for insertion (including embeddings)
    chunks_data = []
    texts_to_embed = [chunk['text'] for chunk in chunks_with_metadata]
    
    # Generate embeddings for all chunks in batch
    print(f"Generating embeddings for {len(texts_to_embed)} chunks...")
    embeddings = get_batch_embeddings(texts_to_embed)
    
    for i, chunk in enumerate(chunks_with_metadata):
        chunks_data.append({
            "document_id": document_id,
            "chunk_index": chunk['index'],
            "content": chunk['text'],
            "metadata": {
                "page_number": chunk['page_number'] if chunk['page_number'] else "",
                "has_page_marker": chunk['has_page_marker'],
                "filename": filename
            },
            "embedding": embeddings[i], # Insert embedding directly
            "embedding_id": str(uuid.uuid4()) # Dummy ID to satisfy NOT NULL constraint (legacy column)
        })
        
    # 4. Insert chunks into Supabase (now includes embeddings)
    # Use batching to avoid timeout with large files
    batch_size = 100
    total_inserted = 0
    print(f"Inserting {len(chunks_data)} chunks into Supabase in batches of {batch_size}...")
    
    for i in range(0, len(chunks_data), batch_size):
        batch = chunks_data[i:i + batch_size]
        try:
            insert_chunks_records(batch)
            total_inserted += len(batch)
            print(f"   - Inserted batch {i//batch_size + 1} ({len(batch)} chunks)")
        except Exception as e:
            print(f"❌ Error inserting batch {i//batch_size + 1}: {e}")
            raise e
    
    # 5. Update BM25 Index (In-Memory update only for current session)
    from app.services.bm25_service import bm25_service
    
    # Construct metadata list for BM25
    new_metadatas = [{
        "document_id": document_id,
        "chunk_index": c['chunk_index'],
        "filename": filename,
        "page_number": c['metadata']['page_number']
    } for c in chunks_data]
    
    bm25_service.add_documents(texts_to_embed, new_metadatas)
    
    # Count documents with page numbers
    chunks_with_pages = sum(1 for c in chunks_data if c['metadata'].get("page_number"))
    
    return {
        "filename": filename,
        "total_chars": len(content),
        "total_chunks": total_chunks,
        "chunks_with_page_numbers": chunks_with_pages,
        "document_id": document_id,
        "status": "processed_and_stored"
    }
    

