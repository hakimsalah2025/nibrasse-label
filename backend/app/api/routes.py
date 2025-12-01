from fastapi import APIRouter, UploadFile, File, Body
from app.services.ingestion import process_file_content
from app.services.rag import rag_pipeline
from app.services.database import get_supabase

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read file content into memory
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")
        
        # Process directly
        result = process_file_content(content, file.filename)
        return {"message": "File processed successfully", "data": result}
    except Exception as e:
        print(f"❌ Upload Error: {str(e)}")
        import traceback
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/documents")
async def get_documents():
    """Get list of all uploaded documents"""
    supabase = get_supabase()
    response = supabase.table("documents").select("*").order("upload_date", desc=True).execute()
    return {"documents": response.data}

@router.post("/query")
async def query_rag(query: str = Body(..., embed=True)):
    try:
        print(f"Received query: {query}")
        result = rag_pipeline(query)
        return result
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_route(text: str = Body(..., embed=True)):
    from app.services.rag import summarize_text
    try:
        summary = summarize_text(text)
        return {"summary": summary}
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
