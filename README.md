
# NASA Signal Decoder Challenge – My Solution

## First 9 Words

**\[WE HAVE ENCOUNTERED SIJNIFICANT DIFFICUXTP LROCESSINJ THE AUDITORP EMISSIONS]**

---

## Approach

The challenge was to locate and decode a 721-character alien message buried somewhere in 64KB of noisy signal data. The decoded text had to follow a very specific letter frequency order:
**E A T O I R S N H U** (most to least common).

### Early Attempts (a.k.a. “How I Got Nowhere Fast”)

1. **Simple frequency mapping** – Just mapped the most common cipher letter to `E`, next to `A`, and so on.
   → The result looked like my cat walked across the keyboard.
2. **Word shape matching** – Tried matching letter patterns (e.g., “THAT” → ABCA).
   → Found a few words but still unreadable overall.
3. **Genetic algorithm** – Let random “solutions” breed and mutate.
   → Way too slow, and got stuck on nonsense.

### What Finally Worked

After some trial and error, I built a combined strategy:

1. **Smart Sampling**
   Instead of testing every single starting position, I sampled every 50th position to cut runtime.
2. **Initial Frequency Mapping**
   Used letter frequencies in each sampled window to make a decent first guess.
3. **Hill Climbing**
   Swapped letter pairs and kept changes that improved the score.
4. **Scoring Function**

   * Rewarded common English words (+7–15 points)
   * Bonus for common digrams like `TH`, `HE` (+0.25 each)
   * Penalized vowel-less words (–3 points)
   * Gave a **+100 bonus** if the decoded text matched the exact required frequency pattern.
5. **Multiple Restarts**
   Ran the hill climb 40 times with different initial maps to escape bad starting points.

