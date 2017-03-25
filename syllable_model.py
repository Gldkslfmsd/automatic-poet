
from sekacek import sekejtext, sekejslovo
import re
import random

from ngram import *

def text2syl(text):	
	t = sekejtext(" "+text+" ")
	syl = []
	last = None
	for sl in re.split(r"( )",t):
		for s in sl.split("/"):
			if s == " ":
				syl[-1] += s
			else:
				if last == " ":
					s = " "+s
				if "-" in s:
					syl.extend([ s[:s.index("-")], s[s.index("-"):]])
				else:
					syl.append(s)
			last = s
	return syl[1:-1]


def ngram_model_text(tok,N=1):
	s = random.randint(0,len(tok)-N)
	start = tuple(tok[s:s+N])

	ngram = BasicNgram(N+1, tok)

	randomtext = list(start)
	for _ in range(100-N):
		d = ngram[tuple(randomtext[-N:])]
		nextword = d.generate()
		randomtext.append(nextword)

	print("".join(randomtext))


from czech_word_accentizer import accentize 


import sys

demosent="vykoupal-li on sebe i jeho ve vodě z řeky"
demosent="sporů mezi havlem a zákonodárným sborem postupně příbývalo"
demosent="""místo padlého klausova kabinetu zformoval prezident svoji
úřednickou vládu což posílilo jeho roli v politice ale jen na omezenou
dobu"""
#print(text2syl(demosent))
syl = text2syl(demosent)
a = accentize(syl)
print([s+b for s,b in zip(syl,a)])


#tok = []
#for line,_ in zip(sys.stdin, range(15000)):
#	line = line.strip()
#	tok.extend(text2syl(line))

#ngram_model_text(tok)

# "Ostra_va_ci ma_ju_ krat_ke_ zo_ba_ky"
