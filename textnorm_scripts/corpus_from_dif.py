#!/usr/bin/python3

import sys
from line_compare import compare_lines

def calculate_corpus(base_path, other_paths):
    base_lines = []
    with open(base_path) as f:
        base_lines = f.read().strip().split("\n")
    diff_lines = []
    for path in other_paths:
        with open(path) as f:
            comp_lines = f.read().strip().split("\n")
            new_lines = compare_lines(base_lines+diff_lines, comp_lines)[1]
            diff_lines+=new_lines
    return diff_lines

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: %s <base_file> <other_files...>"%(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    lines = calculate_corpus(sys.argv[1], sys.argv[2:])
    with open("lines.out", 'w') as f:
        f.write("\n".join(lines))
    print("%d lines written to lines.out"%(len(lines)))

