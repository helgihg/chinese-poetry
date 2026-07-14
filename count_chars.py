#!/usr/bin/env python3
import multiprocessing
import os
import sys
from collections import Counter

OUTPUT_PATH = os.path.abspath('chinese_char_frequencies.txt')

def status(msg):
    print(f"  {msg}", file=sys.stderr)

def is_chinese(ch):
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF or   # CJK Unified Ideographs
        0x3400 <= cp <= 0x4DBF or   # CJK Extension A
        0x20000 <= cp <= 0x2A6DF or # CJK Extension B
        0x2A700 <= cp <= 0x2B73F or # CJK Extension C
        0x2B740 <= cp <= 0x2B81F or # CJK Extension D
        0x2B820 <= cp <= 0x2CEAF or # CJK Extension E
        0x2CEB0 <= cp <= 0x2EBEF or # CJK Extension F
        0xF900 <= cp <= 0xFAFF or   # CJK Compatibility Ideographs
        0x2F800 <= cp <= 0x2FA1F    # CJK Compatibility Supplement
    )

def read_files(root_dir):
    print("Reading files...", file=sys.stderr)
    chunks = []
    scanned = 0
    skipped = 0
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if files:
            status(f"Entering {root}/ ({len(files)} file(s))")
        for fname in files:
            path = os.path.join(root, fname)
            if os.path.abspath(path) == OUTPUT_PATH:
                status(f"  {path}: skipped (output file)")
                continue
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                status(f"  {path}: {len(content)} character(s) read")
                chunks.append(content)
                scanned += 1
            except (OSError, IsADirectoryError) as e:
                status(f"  {path}: skipped ({e})")
                skipped += 1
    heap = ''.join(chunks)
    print(f"\nDone reading. Scanned {scanned} file(s), skipped {skipped}. Heap: {len(heap):,} characters.", file=sys.stderr)
    return heap

def count_chunk(args):
    i, num_chunks, chunk = args
    print(f"  Chunk {i}/{num_chunks} starting...", file=sys.stderr)
    return i, Counter(ch for ch in chunk if is_chinese(ch))

def analyze(heap):
    total = len(heap)
    num_workers = multiprocessing.cpu_count()
    chunk_size = max(1, total // num_workers)
    chunks = [heap[i:i + chunk_size] for i in range(0, total, chunk_size)]
    num_chunks = len(chunks)
    print(f"Analyzing across {num_workers} worker(s) ({num_chunks} chunk(s))...", file=sys.stderr)
    counter = Counter()
    with multiprocessing.Pool(num_workers) as pool:
        args = [(i, num_chunks, chunk) for i, chunk in enumerate(chunks, 1)]
        for done, (i, partial) in enumerate(pool.imap_unordered(count_chunk, args), 1):
            counter += partial
            status(f"  Chunk {i}/{num_chunks} done — {done}/{num_chunks} total complete, {len(counter)} unique Chinese chars so far")
    print(f"Found {len(counter)} unique Chinese characters, {sum(counter.values())} total.", file=sys.stderr)
    return counter

def write_results(counter):
    print(f"Writing results to {OUTPUT_PATH}...", end='', flush=True, file=sys.stderr)
    total = sum(counter.values())
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
        out.write(f"{'Char':<6} {'Codepoint':<12} {'Frequency':>10} {'Percentage':>12}\n")
        out.write('-' * 44 + '\n')
        for ch, freq in sorted(counter.items(), key=lambda x: (-x[1], ord(x[0]))):
            pct = freq / total * 100
            out.write(f"{ch:<6} U+{ord(ch):05X}     {freq:>10} {pct:>11.2f}%\n")
    print(" done.", file=sys.stderr)

def main():
    heap = read_files('.')
    counter = analyze(heap)
    write_results(counter)

if __name__ == '__main__':
    main()
