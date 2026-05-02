"""
algorithms/string_match.py — String pattern matching algorithms.

All functions return (matches, elapsed_microseconds).
  matches  = list of starting indices where pattern is found in text
  elapsed  = time taken in microseconds (float)

Zero GUI / tkinter imports — pure Python only.

Complexity reference:
    Naive      — O(n · m)     worst case
    Rabin-Karp — O(n + m)     average; O(n · m) worst (hash collisions)
    KMP        — O(n + m)     guaranteed
"""

import time


# ── Naive Search ─────────────────────────────────────────────────────────────

def naive_search(text: str, pattern: str) -> tuple[list[int], float]:
    """
    Brute-force sliding window comparison.
    Slides pattern across text one character at a time and checks
    for a full match at each position.

    Time:  O(n · m)
    Space: O(1)
    """
    start = time.perf_counter()

    matches = []
    n = len(text)
    m = len(pattern)

    if m == 0 or n == 0 or m > n:
        elapsed = (time.perf_counter() - start) * 1_000_000
        return matches, elapsed

    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            j += 1
        if j == m:
            matches.append(i)

    elapsed = (time.perf_counter() - start) * 1_000_000
    return matches, elapsed


# ── Rabin-Karp ───────────────────────────────────────────────────────────────

def rabin_karp(text: str, pattern: str,
               base: int = 256, prime: int = 101) -> tuple[list[int], float]:
    """
    Rolling hash string matching.
    Computes a hash for the pattern and a sliding window of the text.
    Only does a full character comparison when hashes match (to handle
    collisions).

    Args:
        base:  alphabet size (default 256 for ASCII)
        prime: large prime for modulo hashing (reduces collisions)

    Time:  O(n + m) average, O(n · m) worst
    Space: O(1)
    """
    start = time.perf_counter()

    matches = []
    n = len(text)
    m = len(pattern)

    if m == 0 or n == 0 or m > n:
        elapsed = (time.perf_counter() - start) * 1_000_000
        return matches, elapsed

    # h = base^(m-1) % prime  — the highest place value in the rolling hash
    h = 1
    for _ in range(m - 1):
        h = (h * base) % prime

    # Compute initial hash for pattern and first window of text
    pattern_hash = 0
    window_hash = 0
    for i in range(m):
        pattern_hash = (base * pattern_hash + ord(pattern[i])) % prime
        window_hash  = (base * window_hash  + ord(text[i]))    % prime

    for i in range(n - m + 1):
        # Hash match — verify character by character to avoid false positives
        if pattern_hash == window_hash:
            if text[i:i + m] == pattern:
                matches.append(i)

        # Roll the hash: remove leading character, add next character
        if i < n - m:
            window_hash = (base * (window_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
            # Keep hash positive
            if window_hash < 0:
                window_hash += prime

    elapsed = (time.perf_counter() - start) * 1_000_000
    return matches, elapsed


# ── KMP ──────────────────────────────────────────────────────────────────────

def _build_lps(pattern: str) -> list[int]:
    """
    Build the Longest Proper Prefix which is also Suffix (LPS) array.
    lps[i] = length of the longest proper prefix of pattern[0..i]
    that is also a suffix of pattern[0..i].

    This tells KMP how far to shift the pattern on a mismatch
    without re-examining already-matched characters.

    Time:  O(m)
    Space: O(m)
    """
    m = len(pattern)
    lps = [0] * m

    length = 0  # length of the previous longest prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                # Fall back — don't increment i here
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    return lps


def kmp_search(text: str, pattern: str) -> tuple[list[int], float]:
    """
    Knuth-Morris-Pratt pattern matching using the LPS failure function.
    Uses the LPS array to skip re-checking characters on mismatches,
    guaranteeing linear time.

    Time:  O(n + m)   guaranteed
    Space: O(m)       for the LPS array
    """
    start = time.perf_counter()

    matches = []
    n = len(text)
    m = len(pattern)

    if m == 0 or n == 0 or m > n:
        elapsed = (time.perf_counter() - start) * 1_000_000
        return matches, elapsed

    lps = _build_lps(pattern)

    i = 0  # index into text
    j = 0  # index into pattern

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1

        if j == m:
            # Full match found — record start index
            matches.append(i - j)
            # Use LPS to slide pattern (avoid redundant comparisons)
            j = lps[j - 1]
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                # Skip ahead using LPS — don't move i
                j = lps[j - 1]
            else:
                i += 1

    elapsed = (time.perf_counter() - start) * 1_000_000
    return matches, elapsed
