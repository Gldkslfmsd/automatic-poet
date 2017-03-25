usage = """usage:
python3 ngram_model.py {2,3,4,5} < corpus.txt
"""
import sys

from ngram import BasicNgram

import pejsekakocicka

from collections import Counter
import random

if len(sys.argv)!=1:
	error = False
	try:
		N = int(sys.argv[1])-1
	except ValueError:
		error = True
	if error or not 1<= N <= 4:
		sys.stderr.write(usage)
		sys.exit(2)
else:
	N = 2

text = sys.stdin.read()

tok = pejsekakocicka.get_tokens(text)
print(tok[:10])

s = random.randint(0,len(tok)-N)
start = tuple(tok[s:s+N])

ngram = BasicNgram(N+1, tok)

randomtext = list(start)
for _ in range(100-N):
	d = ngram[tuple(randomtext[-N:])]
	nextword = d.generate()
	randomtext.append(nextword)

print(" ".join(randomtext))


