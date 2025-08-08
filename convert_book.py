"""Convert book content to typing game format"""

import re
from pathlib import Path

def convert_book_to_words(input_file: Path, output_file: Path, preserve_punctuation: bool = True):
    """Convert a book/text file to word-per-line format for typing game.
    
    Args:
        input_file: Path to book file (can be paragraphs/sentences)
        output_file: Path where to save word-per-line output
        preserve_punctuation: Keep punctuation attached to words
    """
    try:
        content = input_file.read_text(encoding='utf-8')
        
        if preserve_punctuation:
            # Split on whitespace but keep punctuation attached
            words = re.findall(r'\S+', content)
        else:
            # Remove punctuation and split
            words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
        
        # Write one word per line
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in words:
                f.write(word + '\n')
        
        print(f"✅ Converted {len(words)} words from {input_file.name} to {output_file.name}")
        return len(words)
        
    except Exception as e:
        print(f"❌ Error converting file: {e}")
        return 0

def create_difficulty_levels():
    """Create different difficulty word lists"""
    base_path = Path("data/wordlists")
    
    # Easy words (short, common)
    easy_words = [
        "the", "and", "for", "you", "all", "not", "can", "had", "but", "was",
        "one", "our", "out", "day", "get", "has", "him", "his", "how", "man",
        "new", "now", "old", "see", "two", "way", "who", "boy", "did", "its",
        "let", "put", "say", "she", "too", "use"
    ]
    
    # Medium words (longer, moderate difficulty)
    medium_words = [
        "about", "after", "again", "before", "being", "below", "between",
        "could", "every", "first", "found", "great", "group", "large",
        "light", "might", "never", "other", "place", "right", "small",
        "sound", "still", "such", "think", "three", "through", "under",
        "water", "where", "which", "while", "world", "would", "write", "years"
    ]
    
    # Save word lists
    (base_path / "easy.txt").write_text('\n'.join(easy_words))
    (base_path / "medium.txt").write_text('\n'.join(medium_words))
    
    print("✅ Created easy.txt and medium.txt word lists")

if __name__ == "__main__":
    print("📚 Book to Typing Game Converter")
    print("=" * 40)
    
    # Convert Alice sample
    alice_file = Path("data/wordlists/alice_sample.txt")
    if alice_file.exists():
        convert_book_to_words(
            alice_file, 
            Path("data/wordlists/alice_words.txt"), 
            preserve_punctuation=True
        )
    
    # Create difficulty levels
    create_difficulty_levels()
    
    print("\n📝 How to add your own book:")
    print("1. Paste your book content into a .txt file in data/wordlists/")
    print("2. Run: python convert_book.py")
    print("3. Use the generated _words.txt file with the game")
    print("\n🎯 Available word lists:")
    wordlist_dir = Path("data/wordlists")
    if wordlist_dir.exists():
        for file in wordlist_dir.glob("*.txt"):
            word_count = len(file.read_text().splitlines())
            print(f"   - {file.name}: {word_count} words")
