import re
from sekacek import sekejtext, sekejslovo

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


