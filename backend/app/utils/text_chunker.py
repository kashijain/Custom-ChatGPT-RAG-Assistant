def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If not the last chunk, try to end at a sentence
        if end < len(text):
            # Look for sentence endings within the last 100 chars
            sentence_endings = ['. ', '! ', '? ', '\n']
            best_end = end
            for ending in sentence_endings:
                pos = text.rfind(ending, end - 100, end)
                if pos != -1 and pos > best_end - 100:
                    best_end = pos + len(ending)
            
            end = best_end
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else end
    
    return chunks