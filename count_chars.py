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

counter = Counter()
files_scanned = 0
files_skipped = 0

print("Scanning...", file=sys.stderr)

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    if files:
        status(f"Entering {root}/ ({len(files)} file(s))")
    for fname in files:
        path = os.path.join(root, fname)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            found = sum(1 for ch in content if is_chinese(ch))
            status(f"  {path}: {found} Chinese character(s)")
            for ch in content:
                if is_chinese(ch):
                    counter[ch] += 1
            files_scanned += 1
        except (OSError, IsADirectoryError) as e:
            status(f"  {path}: skipped ({e})")
            files_skipped += 1

print(f"\nDone. Scanned {files_scanned} file(s), skipped {files_skipped}.", file=sys.stderr)
print(f"Found {len(counter)} unique Chinese characters, {sum(counter.values())} total.\n", file=sys.stderr)

print(f"{'Char':<6} {'Frequency':>10}")
print('-' * 18)
for ch, freq in counter.most_common():
    print(f"{ch:<6} {freq:>10}")
