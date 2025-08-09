#!/usr/bin/env python3
# completed_signal_decoder.py
# Reads ./signal.txt, finds the 721-char substitution-cipher message,
# runs a stronger hillclimb / simulated annealing + restarts and writes the best 721-char decryption.
# Also prints the "first 9 words" from the discovered message.

import re, random, math, argparse
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

def initial_map_from_freq(window, seed_offset=0):
    cnt = Counter(c for c in window if c!=" ")
    freq_sorted = [c for c,_ in cnt.most_common()]
    mapping = {}
    for i,src in enumerate(freq_sorted):
        if i < len(TOP10_ORDER):
            mapping[src] = TOP10_ORDER[i]
    remaining_plain = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in mapping.values()]
    remaining_src = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in mapping.keys()]
    rnd = random.Random(sum(ord(c) for c in window[:50]) + seed_offset)
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
    # reward common words strongly
    for w in words:
        if w in COMMON_WORDS:
            score += 8 + len(w) * 0.6
        if w in ONE_TWO_WORDS:
            score += 1.5
        # penalize long consonant-only words (likely garbage)
        if len(w) >= 6 and all(ch not in vowels for ch in w):
            score -= 4.0
    # reward presence of " THE " and " AND "
    if " THE " in f" {dec} ":
        score += 18
    if " AND " in f" {dec} ":
        score += 6
    # digram bonuses
    dg_count = sum(1 for i in range(len(dec)-1) if dec[i:i+2] in COMMON_DIGRAMS)
    score += dg_count * 0.35
    # penalize unknown mappings
    score -= dec.count("?") * 0.8
    # small penalty for too many single-letter garbage tokens
    single_bad = sum(1 for w in words if len(w)==1 and w not in ONE_TWO_WORDS)
    score -= single_bad * 0.4
    return score

def neighbor_swap(mapping):
    k1, k2 = random.sample(list(mapping.keys()), 2)
    m = mapping.copy()
    m[k1], m[k2] = m[k2], m[k1]
    return m

def simulated_anneal_map(window, init_map, max_iters=1200, start_temp=1.2, end_temp=0.001):
    # returns best_map, best_score
    curr_map = init_map.copy()
    curr_score = score_decryption_fast(apply_map(window, curr_map))
    best_map, best_score = curr_map.copy(), curr_score

    for it in range(max_iters):
        # linear cooling
        t = start_temp * ((end_temp/start_temp) ** (it / max_iters))
        prop = neighbor_swap(curr_map)
        s2 = score_decryption_fast(apply_map(window, prop))
        delta = s2 - curr_score
        if delta > 0 or math.exp(delta / max(t, 1e-12)) > random.random():
            curr_map, curr_score = prop, s2
            if curr_score > best_score:
                best_map, best_score = curr_map.copy(), curr_score
    return best_map, best_score

def improve_mapping_for_window(window, restarts=35):
    best_map = None
    best_score = float("-inf")
    # a few carefully seeded restarts
    for r in range(restarts):
        if r == 0:
            init_map = initial_map_from_freq(window, seed_offset=0)
        else:
            init_map = initial_map_from_freq(window, seed_offset=r*13)
        m, s = simulated_anneal_map(window, init_map, max_iters=1000)
        if s > best_score:
            best_score = s
            best_map = m
    return best_map, best_score

def find_best_721_segment_from_map(full_text, mapping):
    # apply mapping to full text and slide to find best scoring 721 window
    dec_full = apply_map(full_text, mapping)
    best_s = float("-inf")
    best_seg = None
    best_start = 0
    # step 1 scan with step 1 (size roughly len-721) -> still OK for 64KB
    for i in range(0, len(dec_full)-WINDOW_LEN+1):
        seg = dec_full[i:i+WINDOW_LEN]
        s = score_decryption_fast(seg)
        if s > best_s:
            best_s = s
            best_seg = seg
            best_start = i
    return best_seg, best_start, best_s

def main(filepath):
    random.seed(12345)  # deterministic-ish runs; change or remove for variety
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    text = normalize_text(raw)

    # sample windows (coarse step for candidate selection)
    step = 40
    candidates = []
    for start in range(0, len(text)-WINDOW_LEN+1, step):
        wnd = text[start:start+WINDOW_LEN]
        init_map = initial_map_from_freq(wnd)
        dec = apply_map(wnd, init_map)
        candidates.append((score_decryption_fast(dec), start, init_map))

    # pick top candidates and hillclimb them more thoroughly
    candidates.sort(reverse=True, key=lambda x: x[0])
    candidates = candidates[:18]

    best_overall = (float("-inf"), None, None, None)  # (score, start, map, decoded_window)
    for _, start, init_map in candidates:
        wnd = text[start:start+WINDOW_LEN]
        best_map_for_wnd, best_score_for_wnd = improve_mapping_for_window(wnd, restarts=40)
        dec = apply_map(wnd, best_map_for_wnd)
        if best_score_for_wnd > best_overall[0]:
            best_overall = (best_score_for_wnd, start, best_map_for_wnd, dec)

    best_score, best_start, best_map, best_decoded = best_overall
    print("BEST candidate window start", best_start, "score", best_score)

    # Now apply best_map to entire text and find the best 721-length segment
    final_segment, seg_start, seg_score = find_best_721_segment_from_map(text, best_map)
    print("Best 721-segment found at", seg_start, "score", seg_score)
    if final_segment is None:
        print("No segment decoded. Exiting.")
        return

    # Write the final 721-char decrypted message
    outpath = "decoded_message.txt"
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(final_segment)
    print(f"Wrote decoded 721-character message to {outpath}")

    # Print the first 9 words (for the challenge)
    words = [w for w in final_segment.split() if w]
    first9 = " ".join(words[:9])
    print("\nFirst 9 words (words separated by spaces) ->")
    print(first9)
    print("\nDecoded message preview (first 400 chars):\n")
    print(final_segment[:400])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode 721-char substitution-cipher message in signal.txt")
    parser.add_argument("--file", "-f", default=FILEPATH, help="path to signal file")
    args = parser.parse_args()
    main(args.file)
