#!/usr/bin/env python3
import os
import sys
from collections import Counter

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

def status(msg):
    print(f"  {msg}", file=sys.stderr)

chunks = []
files_scanned = 0
files_skipped = 0

print("Reading files...", file=sys.stderr)

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    if files:
        status(f"Entering {root}/ ({len(files)} file(s))")
    for fname in files:
        path = os.path.join(root, fname)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            status(f"  {path}: {len(content)} character(s) read")
            chunks.append(content)
            files_scanned += 1
        except (OSError, IsADirectoryError) as e:
            status(f"  {path}: skipped ({e})")
            files_skipped += 1

print(f"\nDone reading. Scanned {files_scanned} file(s), skipped {files_skipped}.", file=sys.stderr)

heap = ''.join(chunks)
total = len(heap)
status(f"Heap size: {total} characters total")
print("Analyzing...", file=sys.stderr)

counter = Counter()
report_every = max(1, total // 20)  # report every 5%
last_report = 0

for i, ch in enumerate(heap):
    if is_chinese(ch):
        counter[ch] += 1
    if i - last_report >= report_every:
        pct = (i + 1) / total * 100
        status(f"  {i+1:,} / {total:,} characters ({pct:.0f}%) — {len(counter)} unique Chinese chars so far")
        last_report = i

status(f"  {total:,} / {total:,} characters (100%) — done")
print(f"Found {len(counter)} unique Chinese characters, {sum(counter.values())} total.", file=sys.stderr)

output_path = 'chinese_char_frequencies.txt'
print(f"Writing results to {output_path}...", file=sys.stderr)
with open(output_path, 'w', encoding='utf-8') as out:
    out.write(f"{'Char':<6} {'Frequency':>10}\n")
    out.write('-' * 18 + '\n')
    for ch, freq in counter.most_common():
        out.write(f"{ch:<6} {freq:>10}\n")
print("Done.", file=sys.stderr)
