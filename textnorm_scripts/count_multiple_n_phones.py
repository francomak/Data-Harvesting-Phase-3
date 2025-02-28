#!/usr/bin/python2

from __future__ import print_function
import os
import sys
import count_n_phones

if len(sys.argv)<1:
    sys.stderr.write("Provide at least one file name.\n")
    sys.stderr.flush()
    sys.exit(1)


results = []
for path in sys.argv[1:]:
    if path != "blank":
        phonedir = path+"_out"
        os.system("mkdir -p \"%s\""%(phonedir))
        results.append(count_n_phones.getNPhones(path, phonedir))
    else:
        results.append(())

print("\nTable of counts:")
for i in range(0,5):
    for result in results:
        if result!=():
            print(result[i], end='\t')
        else:
            print("", end="\t")
    print()
