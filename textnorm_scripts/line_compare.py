#!/usr/bin/python3

import sys

def compare_text(text1, text2):
    return text1==text2

def compare_texts(text1, text2):
    lines1=text1.strip().split("\n")
    lines2=text2.strip().split("\n")
    compare_lines(lines1, lines2)

def compare_lines(lines1, lines2):
    match_count=0
    progress=0
    percentage=0
    lines2count=len(lines2)
    new_lines=[]
    lines1_dict = {}
    for line in lines1:
        try:
            lines1_dict[line] = 1
        except:
            print(line[0:3])
            sys.exit(2)
    for line in lines2:
        progress+=1
        new_percentage=int(progress/lines2count*100)
        if new_percentage>percentage:
            percentage=new_percentage
            print("Progress: %d%%, match_count: %d"%(percentage, match_count))
        if line in lines1_dict:
            match_count+=1
        else:
            new_lines.append(line)
    return match_count, new_lines

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: %s: <file1> <file2>"%(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    f = open(sys.argv[1])
    text1=f.read()
    f.close()
    f = open(sys.argv[2])
    text2 = f.read()
    f.close()
    print("%d lines of file2 in file1"%(compare_lines(text1, text2)[0]))

