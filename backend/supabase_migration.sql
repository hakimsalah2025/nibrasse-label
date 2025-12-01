-- 1. Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- 2. Add embedding column to chunk table
-- Gemini Pro embedding dimension is 768
alter table chunk add column if not exists embedding vector(768);

-- 3. Create a function to search for documents
create or replace function match_documents (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    chunk.id,
    chunk.content,
    chunk.metadata,
    1 - (chunk.embedding <=> query_embedding) as similarity
  from chunk
  where 1 - (chunk.embedding <=> query_embedding) > match_threshold
  order by chunk.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- 4. Create an index for faster queries (HNSW)
create index on chunk using hnsw (embedding vector_cosine_ops);
