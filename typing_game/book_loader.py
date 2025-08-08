"""Enhanced word loading for books and longer passages."""

from pathlib import Path
from typing import List, Optional
import re

def load_book_content(file_path: Path) -> List[str]:
    """Load a book/passage and split into words, preserving punctuation and capitalization.
    
    Args:
        file_path: Path to text file containing book content
        
    Returns:
        List of words with proper spacing and punctuation
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Split into words while preserving punctuation
        # This regex keeps punctuation attached to words
        words = re.findall(r'\S+', content)
        
        return words
    except Exception as e:
        print(f"Error loading book content: {e}")
        return ["error", "loading", "book", "content"]

def create_sentence_chunks(words: List[str], chunk_size: int = 10) -> List[str]:
    """Group words into sentence-like chunks for progressive typing.
    
    Args:
        words: List of individual words
        chunk_size: Number of words per chunk
        
    Returns:
        List of word chunks (phrases/sentences)
    """
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def format_book_for_typing(file_path: Path, mode: str = "words") -> List[str]:
    """Format book content for different typing modes.
    
    Args:
        file_path: Path to book file
        mode: "words" (individual words), "sentences" (sentence chunks), 
              "paragraphs" (paragraph chunks)
              
    Returns:
        List of typing units based on mode
    """
    words = load_book_content(file_path)
    
    if mode == "words":
        return words
    elif mode == "sentences":
        return create_sentence_chunks(words, chunk_size=8)
    elif mode == "paragraphs":
        return create_sentence_chunks(words, chunk_size=25)
    else:
        return words
