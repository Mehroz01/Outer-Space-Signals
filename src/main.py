# write your code here
import re
from collections import Counter
from typing import Dict, List, Tuple

def validate_solution(decrypted_text: str, expected_top_10: str = "EATOIRSNHU") -> bool:
    """Validate that the solution matches the expected frequency pattern."""
    frequencies = calculate_frequencies(decrypted_text)
    sorted_letters = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    
    if len(sorted_letters) < 10:
        return False
    
    actual_top_10 = ''.join([letter for letter, _ in sorted_letters[:10]])
    
    print(f"📊 Expected top 10: {expected_top_10}")
    print(f"📊 Actual top 10:   {actual_top_10}")
    
    # Check if at least 7 out of 10 match (allowing for some variation)
    matches = sum(1 for a, b in zip(actual_top_10, expected_top_10) if a == b)
    return matches >= 7

def refine_mapping_with_patterns(encrypted_text: str, initial_mapping: Dict[str, str]) -> Dict[str, str]:
    """Refine the mapping using common English word patterns."""
    mapping = initial_mapping.copy()
    
    # Apply initial mapping
    decrypted = apply_substitution(encrypted_text, mapping)
    
    # Look for common patterns and adjust
    common_words = {
        'THE': ['THE', 'TGE', 'TCE', 'TAE'],  # Common misspellings/variants to look for
        'AND': ['AND', 'AID', 'ANO'],
        'FOR': ['FOR', 'FAR', 'FER'],
        'ARE': ['ARE', 'ATE', 'APE'],
        'YOU': ['YOU', 'YAU', 'YEU'],
        'ALL': ['ALL', 'AII', 'ALI'],
        'BUT': ['BUT', 'BET', 'BOT'],
        'NOT': ['NOT', 'NAT', 'NET'],
        'CAN': ['CAN', 'CAI', 'CEI'],
        'HAD': ['HAD', 'GAD', 'HED']
    }
    
    # Count potential matches for each pattern
    words_in_text = decrypted.split()
    
    for target_word, variants in common_words.items():
        for word in words_in_text:
            if len(word) == len(target_word):
                # Check if this could be the target word with minor adjustments
                differences = sum(1 for a, b in zip(word, target_word) if a != b)
                if differences == 1:  # Only one letter different
                    # Find the different positions and update mapping
                    for i, (encrypted_char, target_char) in enumerate(zip(word, target_word)):
                        if encrypted_char != target_char:
                            # Find original encrypted character
                            for enc_char, dec_char in mapping.items():
                                if dec_char == encrypted_char:
                                    mapping[enc_char] = target_char
                                    break
    
    return mapping

def apply_substitution(text: str, mapping: Dict[str, str]) -> str:
    """Apply the substitution mapping to decrypt text."""
    result = ""
    for char in text:
        if char in mapping:
            result += mapping[char]
        else:
            result += char  # Keep spaces and unknown characters
    return result

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
    
    print("📋 Initial mapping (top 10):")
    sorted_mapping = sorted(initial_mapping.items(), key=lambda x: calculate_frequencies(encrypted_message).get(x[0], 0), reverse=True)
    for i, (enc, dec) in enumerate(sorted_mapping[:10]):
        freq = calculate_frequencies(encrypted_message).get(enc, 0)
        print(f"   {enc} → {dec} (frequency: {freq:.1f}%)")
    
        # Step 4: Apply initial decryption
    print("\n🔓 Phase 3: Applying initial decryption...")
    decrypted_v1 = apply_substitution(encrypted_message, initial_mapping)
    print(f"🔤 Initial result: {decrypted_v1[:100]}...")
    


    # Step 5: Refine mapping using patterns
    print("\n🎯 Phase 4: Refining with common English patterns...")
    refined_mapping = refine_mapping_with_patterns(encrypted_message, initial_mapping)
    final_decrypted = apply_substitution(encrypted_message, refined_mapping)
    
    # Step 6: Validate solution
    print("\n✅ Phase 5: Validating solution...")
    is_valid = validate_solution(final_decrypted)
    
    if is_valid:
        print("🎉 SUCCESS! Message successfully decrypted!")
    else:
        print("⚠️  Warning: Frequency validation didn't fully match expected pattern")
        print("   (This might still be correct - continuing with result)")
    
    # Step 7: Extract and display results
    print("\n📜 DECRYPTED MESSAGE:")
    print("=" * 70)
    print(final_decrypted)
    print("=" * 70)
    
    # Extract first 9 words for submission
    words = final_decrypted.split()
    first_nine_words = ' '.join(words[:9]) if len(words) >= 9 else ' '.join(words)
    
    print(f"\n🎯 FIRST 9 WORDS FOR SUBMISSION:")
    print(f"➤ {first_nine_words}")


    print(f"\n📊 FINAL STATISTICS:")
    print(f"   • Message length: {len(final_decrypted)} characters")
    print(f"   • Word count: {len(words)} words")
    print(f"   • Located at position: {position}")
    
    # Show final frequency analysis
    final_freq = calculate_frequencies(final_decrypted)
    top_letters = sorted(final_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"   • Top 10 letters: {''.join([letter for letter, _ in top_letters])}")
    print("\n🚀 Mission Complete! The message from Planet Dyslexia has been decoded!")

if __name__ == "__main__":
    main() 
