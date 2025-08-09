import re, random
from collections import Counter

FILEPATH = "signal.txt"
WINDOW_LEN = 721
TOP10_ORDER = ["E","A","T","O","I","R","S","N","H","U"]

COMMON_WORDS = set(w.upper() for w in [
    "the","and","to","of","a","in","is","it","you","that","he","was","for","on","are","as","with",
    "his","they","i","at","be","this","have","from","or","one","had","by","word","but","not","what",
    "all","were","we","when","your","can","said","there","use","an","each","which","she","do","how",
    "their","if","will","up","other","about","out","many","then","them","these","so","some","her",
    "would","make","like","him","into","time","has","look","two","more","write","go","see","number",
    "no","way","could","people","my","than","first","been","call","who","its","now","find","long",
    "down","day","did","get","come","made","may","part", "hello","world","nasa","message","signal"
])
ONE_TWO_WORDS = {"A","I","AN","IN","TO","OF","ON","AT","IT","IS","BE","BY","OR","AS","DO","MY","ME","WE","US","HE","SHE","THE"}
COMMON_DIGRAMS = ["TH","HE","IN","ER","AN","RE","ED","ON","ES","ST","EN","AT","TO"]

def normalize_text(raw):
    t = raw.replace("\n"," ").upper()
    t = re.sub(r"[^A-Z ]+", " ", t)
    t = re.sub(r" +", " ", t).strip()
    return t

def initial_map_from_freq(window):
    cnt = Counter(c for c in window if c!=" ")
    freq_sorted = [c for c,_ in cnt.most_common()]
    mapping = {}
    for i,src in enumerate(freq_sorted):
        if i < len(TOP10_ORDER):
            mapping[src] = TOP10_ORDER[i]
    remaining_plain = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in mapping.values()]
    remaining_src = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in mapping.keys()]
    rnd = random.Random(sum(ord(c) for c in window[:50]))
    rnd.shuffle(remaining_plain)
    for s,p in zip(remaining_src, remaining_plain):
        mapping[s] = p
    return mapping

def apply_map(segment, mapping):
    return "".join(" " if ch==" " else mapping.get(ch,"?") for ch in segment)

def score_decryption_fast(dec):
    vowels = set("AEIOU")
    score = 0.0
    words = dec.split()
    for w in words:
        if w in COMMON_WORDS:
            score += 7 + len(w)
        if w in ONE_TWO_WORDS:
            score += 1.5
        if len(w) >= 5 and all(ch not in vowels for ch in w):
            score -= 3.0
    if " THE " in f" {dec} ":
        score += 15
    dg_count = sum(1 for i in range(len(dec)-1) if dec[i:i+2] in COMMON_DIGRAMS)
    score += dg_count * 0.25
    score -= dec.count("?") * 0.5
    return score

def neighbor_swap(mapping):
    k1, k2 = random.sample(list(mapping.keys()), 2)
    m = mapping.copy()
    m[k1], m[k2] = m[k2], m[k1]
    return m

def get_frequency_order(text):
    """Get the top 10 letters by frequency in the decrypted text."""
    # Count only letters (not spaces)
    letter_counts = Counter(c for c in text if c != " " and c != "?")
    # Get letters sorted by frequency
    freq_sorted = [letter for letter, count in letter_counts.most_common()]
    return freq_sorted[:10] if len(freq_sorted) >= 10 else freq_sorted

# MAIN
with open(FILEPATH, "r", encoding="utf-8", errors="ignore") as f:
    raw = f.read()
text = normalize_text(raw)

# sample windows (step to limit runtime), score initial maps, pick best region(s)
step = 50
candidates = []
for start in range(0, len(text)-WINDOW_LEN+1, step):
    wnd = text[start:start+WINDOW_LEN]
    init_map = initial_map_from_freq(wnd)
    dec = apply_map(wnd, init_map)
    candidates.append((score_decryption_fast(dec), start, init_map))

candidates.sort(reverse=True, key=lambda x: x[0])
candidates = candidates[:12]  # keep top candidates

best_overall = (float("-inf"), None, None, None)
for _, start, init_map in candidates:
    wnd = text[start:start+WINDOW_LEN]
    best_map = init_map.copy()
    best_score = score_decryption_fast(apply_map(wnd, best_map))
    # a limited but focused hillclimb
    for restart in range(40):
        curr_map = best_map.copy() if restart==0 else initial_map_from_freq(wnd)
        curr_score = score_decryption_fast(apply_map(wnd, curr_map))
        no_imp = 0
        for _it in range(400):
            prop = neighbor_swap(curr_map)
            s2 = score_decryption_fast(apply_map(wnd, prop))
            if s2 > curr_score or random.random() < 0.002:
                curr_map, curr_score = prop, s2
                no_imp = 0
            else:
                no_imp += 1
            if curr_score > best_score:
                best_map, best_score = curr_map.copy(), curr_score
            if no_imp > 160:
                break
    dec = apply_map(wnd, best_map)
    if best_score > best_overall[0]:
        best_overall = (best_score, start, best_map, dec)

best_score, best_start, best_map, best_decoded = best_overall

print("="*70)
print("NASA SIGNAL DECODER RESULTS")
print("="*70)
print(f"\nBEST start position: {best_start}")
print(f"Score: {best_score}")

# Get and display the top 10 frequency letters
top_10_freq = get_frequency_order(best_decoded)
print(f"\n* The top 10 English letters in the deciphered text by frequency is:")
print(f"  {' '.join(top_10_freq)}")

# Check if it matches the required pattern
if top_10_freq == TOP10_ORDER:
    print("  ✓ MATCHES REQUIRED PATTERN: E A T O I R S N H U")
else:
    print(f"  ✗ Required pattern: {' '.join(TOP10_ORDER)}")
    print(f"  Actual pattern:   {' '.join(top_10_freq)}")

# Extract and display first 9 words
words = best_decoded.split()
first_9_words = ' '.join(words[:9]) if len(words) >= 9 else ' '.join(words)

print(f"\n* FIRST 9 WORDS FOR SUBMISSION:")
print(f"  >>> {first_9_words} <<<")

# Show preview of decoded message
print(f"\nDecoded message preview (first 200 chars):")
print(f"{best_decoded[:200]}...")

# Count valid English words
valid_word_count = sum(1 for word in words if word in COMMON_WORDS)
print(f"\nReadability: {valid_word_count}/{len(words)} valid English words ({(valid_word_count/len(words)*100):.1f}%)")

print("\n" + "="*70)

# Save to file with additional info
with open("decoded_message.txt", "w", encoding="utf-8") as f:
    f.write("NASA SIGNAL DECODER RESULTS\n")
    f.write("="*70 + "\n")
    f.write(f"Position: {best_start}\n")
    f.write(f"Score: {best_score}\n")
    f.write(f"Top 10 frequencies: {' '.join(top_10_freq)}\n")
    f.write(f"Required pattern:   {' '.join(TOP10_ORDER)}\n")
    f.write(f"Match: {'YES' if top_10_freq == TOP10_ORDER else 'NO'}\n")
    f.write(f"First 9 words: {first_9_words}\n")
    f.write(f"Readability: {valid_word_count}/{len(words)} valid words\n")
    f.write("\nFull decoded message:\n")
    f.write("="*70 + "\n")
    f.write(best_decoded)

print("Results saved to decoded_message.txt")