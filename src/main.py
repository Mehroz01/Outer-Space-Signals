# write your code here
from collections import Counter
from typing import Dict, List, Tuple

def create_frequency_mapping(encrypted_text: str) -> Dict[str, str]:
    """Create initial substitution mapping based on frequency analysis."""
    encrypted_freq = calculate_frequencies(encrypted_text)
    english_order = "ETAOINSHRDLCUMWFGYPBVKJXQZ"  # English letters by frequency
    
    # Sort encrypted letters by frequency
    encrypted_sorted = sorted(encrypted_freq.items(), key=lambda x: x[1], reverse=True)
    
    mapping = {}
    for i, (encrypted_letter, _) in enumerate(encrypted_sorted):
        if i < len(english_order):
            mapping[encrypted_letter] = english_order[i]
    
    return mapping


def calculate_frequencies(text: str) -> Dict[str, float]:
    """Calculate letter frequencies in the given text."""
    # Only count letters, ignore spaces
    letters_only = ''.join(char for char in text if char.isalpha())
    if not letters_only:
        return {}
    
    counter = Counter(letters_only)
    total = len(letters_only)
    
    return {letter: (count / total) * 100 for letter, count in counter.items()}


def get_english_frequencies() -> Dict[str, float]:
    """Return expected English letter frequencies (as percentages)."""
    return {
        'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
        'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
        'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
        'P': 1.9, 'B': 1.3, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
        'Q': 0.10, 'Z': 0.07
    }

def score_english_likelihood(text: str) -> float:
    """Score how likely a text is to be English based on letter frequencies."""
    text_freq = calculate_frequencies(text)
    english_freq = get_english_frequencies()
    
    if not text_freq:
        return 0
    
    # Calculate chi-squared like score (lower is better match)
    score = 0
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        expected = english_freq.get(letter, 0)
        observed = text_freq.get(letter, 0)
        if expected > 0:
            score += ((observed - expected) ** 2) / expected
    
    return 1 / (1 + score)  # Convert to higher-is-better score




def find_best_message_window(signal: str, message_length: int = 721) -> Tuple[str, int]:
    """Find the most English-like window of the specified length."""
    best_score = 0
    best_window = ""
    best_position = 0
    
    print(f"🔍 Scanning {len(signal):,} characters for {message_length}-character message...")
    
    # Try every possible position for the message
    for i in range(len(signal) - message_length + 1):
        window = signal[i:i + message_length]
        
        # Skip if window doesn't have enough variety (likely noise)
        unique_chars = len(set(char for char in window if char.isalpha()))
        if unique_chars < 10:  # Need reasonable letter variety
            continue
        
        score = score_english_likelihood(window)
        
        if score > best_score:
            best_score = score
            best_window = window
            best_position = i
            
        # Progress indicator
        if i % 10000 == 0:
            print(f"   Progress: {i:,}/{len(signal) - message_length:,} ({i/(len(signal) - message_length)*100:.1f}%)")
    
    print(f"✅ Best candidate found at position {best_position} with score {best_score:.4f}")
    return best_window, best_position



def load_signal(filename: str = "signal.txt") -> str:
    """Load the 64KB signal file containing the encrypted message."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found!")
        return ""


def main():
    """Main function to run the program."""
    print("🛸 NASA Signal Decoder - Deciphering Messages from Planet Dyslexia 🛸")
    print("=" * 70)
    # Your code logic goes here -- feel free to add functions or classes as needed

    print("📡 Loading signal data...")
    signal_data = load_signal("signal.txt")
    #print(signal_data)

    if not signal_data:
            return

    print("Analyzing 64KB of alien signals...")
    print("Searching for 721-character encrypted message...")
    print(f"✅ Loaded {len(signal_data):,} characters of signal data")

    print("\n🔍 Phase 1: Locating the encrypted message...")
    encrypted_message, position = find_best_message_window(signal_data, 721)
    
    if not encrypted_message:
        print("❌ Could not find a suitable message candidate!")
        return


    print(f"📍 Message located at position {position}")
    print(f"🔤 First 50 characters: {encrypted_message[:50]}...")
    

    # Step 3: Create initial frequency-based mapping
    print("\n🧮 Phase 2: Creating frequency-based substitution mapping...")
    initial_mapping = create_frequency_mapping(encrypted_message)
    


if __name__ == "__main__":
    main() 
