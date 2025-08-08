"""Enhanced demo with different difficulty levels"""

from typing_game.engine import interactive_loop
from typing_game.config import ModeConfig
from pathlib import Path

def choose_difficulty():
    """Let user choose difficulty level"""
    print("\n🎯 Choose Difficulty Level:")
    print("1. Easy (short common words)")
    print("2. Medium (moderate length words)")  
    print("3. Hard (complex words)")
    print("4. Programming (technical terms)")
    print("5. Alice in Wonderland (book content)")
    print("6. Default (mixed)")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    wordlist_map = {
        "1": "data/wordlists/easy.txt",
        "2": "data/wordlists/medium.txt", 
        "3": "data/wordlists/hard_words.txt",
        "4": "data/wordlists/programming.txt",
        "5": "data/wordlists/alice_words.txt",
        "6": None  # default
    }
    
    wordlist_path = wordlist_map.get(choice)
    if wordlist_path and Path(wordlist_path).exists():
        return Path(wordlist_path)
    return None

def main():
    print("🎯 Enhanced Typing Game with Difficulty Levels")
    print("=" * 50)
    
    # Choose difficulty
    wordlist = choose_difficulty()
    
    # Setup config
    cfg = ModeConfig(
        word_count=25,  # Start with 25 words
        punctuation_prob=0.0,  # Start without punctuation
        numbers=False,
        wordlist_path=wordlist
    )
    
    if wordlist:
        word_count = len(wordlist.read_text().splitlines())
        print(f"\n✅ Using {wordlist.name} ({word_count} words available)")
    else:
        print("\n✅ Using default word list")
    
    print(f"\n⚙️  Mode: {cfg.word_count} words")
    print("📝 Instructions:")
    print("   • Type each word exactly as shown")
    print("   • Press SPACE or ENTER after each word")
    print("   • Use BACKSPACE to correct mistakes") 
    print("   • Type '/quit' to exit early")
    print("\n" + "=" * 50)
    
    try:
        interactive_loop(cfg)
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing!")

if __name__ == "__main__":
    main()
