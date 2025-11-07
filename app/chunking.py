def chunk_by_sentences(text, max_length=200):
    """
    Chunk text by sentences with a maximum length per chunk.
    
    Args:
        text: Input text to chunk
        max_length: Maximum length of each chunk
        
    Returns:
        List of text chunks
        
    Raises:
        ValueError: If text is invalid or max_length is invalid
    """
    try:
        # Validate input text
        if text is None:
            raise ValueError("Text cannot be None")
        
        if not isinstance(text, str):
            raise ValueError(f"Text must be a string, got {type(text).__name__}")
        
        if not text.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        
        # Validate max_length
        if not isinstance(max_length, int):
            raise ValueError(f"max_length must be an integer, got {type(max_length).__name__}")
        
        if max_length <= 0:
            raise ValueError(f"max_length must be positive, got {max_length}")
        
        if max_length < 50:
            raise ValueError(f"max_length too small ({max_length}), minimum recommended is 50")
        
        # Split sentences
        sentences = text.split(". ")
        
        if not sentences:
            return [text.strip()]
        
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # Skip empty sentences
            if not sentence.strip():
                continue
            
            # Check if adding this sentence exceeds max_length
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                # Save current chunk if it's not empty
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If no chunks were created, return the original text as one chunk
        if not chunks:
            chunks.append(text.strip())
        
        return chunks
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Error in chunk_by_sentences: {str(e)}")


def chunk_by_fixed_length(text, chunk_size=500):
    """
    Chunk text by fixed character length.
    
    Args:
        text: Input text to chunk
        chunk_size: Size of each chunk in characters
        
    Returns:
        List of text chunks
        
    Raises:
        ValueError: If text is invalid or chunk_size is invalid
    """
    try:
        # Validate input text
        if text is None:
            raise ValueError("Text cannot be None")
        
        if not isinstance(text, str):
            raise ValueError(f"Text must be a string, got {type(text).__name__}")
        
        if not text.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        
        # Validate chunk_size
        if not isinstance(chunk_size, int):
            raise ValueError(f"chunk_size must be an integer, got {type(chunk_size).__name__}")
        
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        
        if chunk_size < 50:
            raise ValueError(f"chunk_size too small ({chunk_size}), minimum recommended is 50")
        
        # Create chunks
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Filter out empty chunks
        chunks = [chunk for chunk in chunks if chunk.strip()]
        
        # If no chunks were created, return the original text
        if not chunks:
            chunks.append(text.strip())
        
        return chunks
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Error in chunk_by_fixed_length: {str(e)}")