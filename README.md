# NASA Signal Decoder Challenge – My Solution

## First 9 Words

**\[WE HAVE ENCOUNTERED SIJNIFICANT DIFFICUXTP LROCESSINJ THE AUDITORP EMISSIONS]**

---

## Early Attempts (a.k.a. “How I Got Nowhere Fast”)

1. **Simple frequency mapping** – mapped top letters to `E A T...` → looked like my cat typed it. 😅
2. **Word shape matching** – matched letter patterns → still unreadable.
3. **Genetic algorithm** – too slow and stuck on nonsense.

---

## What Finally Worked

After studying from the internet and basic cipher techniques:

* Sampled the signal in chunks to spot the message.
* Built an initial letter map from frequency order.
* Improved the map by swapping letters until it looked more English.
* Used multiple restarts to avoid bad guesses.
* Applied the best map to reveal the 721-char message.

