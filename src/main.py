# NASA Signal Decoder - Deciphering Messages from Planet Dyslexia
# Challenge: Find and decrypt a 721-character substitution cipher hidden in 64KB of noise

import re
from collections import Counter
from typing import Dict, List, Tuple

def load_signal(filename: str = "signal.txt") -> str:
    """Load the 64KB signal file containing the encrypted message."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found!")
        return ""

def get_english_frequencies() -> Dict[str, float]:
    """Return expected English letter frequencies (as percentages).
    Based on analysis of large English text corpora from practicalcryptography.com
    """
    return {
        'E': 12.10, 'T': 8.94, 'A': 8.55, 'O': 7.47, 'I': 7.33, 'N': 7.17,
        'S': 6.73, 'H': 4.96, 'R': 6.33, 'D': 3.87, 'L': 4.21, 'C': 3.16,
        'U': 2.68, 'M': 2.53, 'W': 1.83, 'F': 2.18, 'G': 2.09, 'Y': 1.72,
        'P': 2.07, 'B': 1.60, 'V': 1.06, 'K': 0.81, 'J': 0.22, 'X': 0.19,
        'Q': 0.10, 'Z': 0.11
    }

def calculate_frequencies(text: str) -> Dict[str, float]:
    """Calculate letter frequencies in the given text."""
    # Only count letters, ignore spaces
    letters_only = ''.join(char for char in text if char.isalpha())
    if not letters_only:
        return {}
    
    counter = Counter(letters_only)
    total = len(letters_only)
    
    return {letter: (count / total) * 100 for letter, count in counter.items()}

def score_english_likelihood(text: str) -> float:
    """Score how likely a text is to be English based on multiple factors."""
    text_freq = calculate_frequencies(text)
    english_freq = get_english_frequencies()
    
    if not text_freq:
        return 0
    
    # 1. Chi-squared test for letter frequencies
    chi_squared = 0
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        expected = english_freq.get(letter, 0)
        observed = text_freq.get(letter, 0)
        if expected > 0:
            chi_squared += ((observed - expected) ** 2) / expected
    
    freq_score = 1 / (1 + chi_squared / 100)  # Normalize
    
    # 2. Check for common English patterns
    pattern_score = 0
    text_upper = text.upper()
    common_patterns = [
        'THE ', ' THE', 'AND ', ' AND', 'ING ', 'TION', 'ATION',
        'ER ', 'AL ', 'EN ', 'OF ', 'TO ', 'IN ', 'IS ', 'IT ',
        'FOR ', 'AS ', 'ARE ', 'WAS ', 'BUT ', 'NOT ', 'OR ',
        'HAVE ', 'FROM ', 'THIS ', 'THAT ', 'WITH ', 'HIS ',
        'ON ', 'AT ', 'BE ', 'OR ', 'AN ', 'WILL ', 'MY ',
        'ONE ', 'ALL ', 'WOULD ', 'THERE ', 'THEIR '
    ]
    
    for pattern in common_patterns:
        pattern_score += text_upper.count(pattern) / len(text_upper) * 1000
    
    # 3. Check for reasonable word length distribution
    words = text.split()
    if words:
        avg_word_length = sum(len(word) for word in words) / len(words)
        # English average word length is around 4.7
        length_score = 1 - abs(avg_word_length - 4.7) / 10
        length_score = max(0, length_score)
    else:
        length_score = 0
    
    # 4. Check for balanced vowel/consonant ratio
    vowels = sum(text_freq.get(v, 0) for v in 'AEIOU')
    consonants = sum(text_freq.get(c, 0) for c in 'BCDFGHJKLMNPQRSTVWXYZ')
    if consonants > 0:
        vowel_ratio = vowels / consonants
        # English typically has vowel/consonant ratio around 0.6-0.8
        ratio_score = 1 - abs(vowel_ratio - 0.7) / 2
        ratio_score = max(0, ratio_score)
    else:
        ratio_score = 0
    
    # Combine all scores with weights
    total_score = (
        freq_score * 0.4 +      # 40% frequency analysis
        pattern_score * 0.3 +    # 30% common patterns  
        length_score * 0.2 +     # 20% word length
        ratio_score * 0.1        # 10% vowel/consonant ratio
    )
    
    return total_score

def find_best_message_window(signal: str, message_length: int = 721) -> Tuple[str, int]:
    """Find the most English-like window of the specified length."""
    best_score = 0
    best_window = ""
    best_position = 0
    candidates = []
    
    print(f"🔍 Scanning {len(signal):,} characters for {message_length}-character message...")
    
    # Try every possible position for the message
    for i in range(len(signal) - message_length + 1):
        window = signal[i:i + message_length]
        
        # Skip if window doesn't have enough variety (likely noise)
        unique_chars = len(set(char for char in window if char.isalpha()))
        if unique_chars < 15:  # Increased threshold for better filtering
            continue
        
        # Skip windows with too many repeated patterns (likely noise)
        letters_only = ''.join(c for c in window if c.isalpha())
        if len(letters_only) < message_length * 0.8:  # Should be mostly letters
            continue
        
        score = score_english_likelihood(window)
        
        # Keep track of top candidates
        candidates.append((score, i, window))
        candidates.sort(reverse=True)
        candidates = candidates[:5]  # Keep top 5
        
        if score > best_score:
            best_score = score
            best_window = window
            best_position = i
            
        # Progress indicator
        if i % 10000 == 0:
            print(f"   Progress: {i:,}/{len(signal) - message_length:,} ({i/(len(signal) - message_length)*100:.1f}%)")
    
    print(f"✅ Best candidate found at position {best_position} with score {best_score:.6f}")
    
    # Show top 3 candidates for comparison
    print("🏆 Top 3 candidates:")
    for j, (score, pos, win) in enumerate(candidates[:3]):
        freq = calculate_frequencies(win)
        top_letters = ''.join([letter for letter, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]])
        print(f"   #{j+1}: Position {pos}, Score {score:.6f}, Letters: {top_letters}")
    
    return best_window, best_position

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

def apply_substitution(text: str, mapping: Dict[str, str]) -> str:
    """Apply the substitution mapping to decrypt text."""
    result = ""
    for char in text:
        if char in mapping:
            result += mapping[char]
        else:
            result += char  # Keep spaces and unknown characters
    return result

def find_common_patterns(text: str) -> List[str]:
    """Find common English word patterns in the text."""
    words = text.split()
    word_patterns = []
    
    for word in words:
        if 2 <= len(word) <= 4:  # Focus on short common words
            word_patterns.append(word)
    
    return Counter(word_patterns).most_common(10)

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

def main():
    """Main function to run the program."""
    print("🛸 NASA Signal Decoder - Deciphering Messages from Planet Dyslexia 🛸")
    print("=" * 70)
    
    # Step 1: Load the signal
    print("📡 Loading signal data...")
    signal_data = load_signal("signal.txt")
    
    if not signal_data:
        return
    
    print(f"✅ Loaded {len(signal_data):,} characters of signal data")
    
    # Step 2: Find the most likely 721-character message
    print("\n🔍 Phase 1: Locating the encrypted message...")
    encrypted_message, position = find_best_message_window(signal_data, 721)
    
    if not encrypted_message:
        print("❌ Could not find a suitable message candidate!")
        return
    
    print(f"📍 Message located at position {position}")
    print(f"🔤 First 50 characters: {encrypted_message[:50]}...")
    
    # Quick validation - check if this looks like encrypted English
    initial_freq = calculate_frequencies(encrypted_message)
    initial_top = ''.join([letter for letter, _ in sorted(initial_freq.items(), key=lambda x: x[1], reverse=True)[:10]])
    #initial_top = ''.join(sorted(initial_freq.items(), key=lambda x: x[1], reverse=True)[:10])
    print(f"🔍 Initial frequency analysis: {initial_top}")
    
    # If the top letters look completely wrong, warn user
    common_first_letters = set('ETAOINSHRDL')
    found_common = sum(1 for letter in initial_top[:5] if letter in common_first_letters)
    if found_common < 3:
        print("⚠️  Warning: This segment might not be English text")
        print("   Consider checking other candidate positions manually")
    
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