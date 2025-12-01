from app.services.database import get_supabase

def query_vectors(query_embedding: list[float], match_threshold: float = 0.5, match_count: int = 10):
    """
    Search for similar documents using Supabase pgvector.
    Calls the 'match_documents' RPC function defined in the migration SQL.
    """
    supabase = get_supabase()
    
    params = {
        "query_embedding": query_embedding,
        "match_threshold": match_threshold,
        "match_count": match_count
    }
    
    response = supabase.rpc("match_documents", params).execute()
    return response.data

