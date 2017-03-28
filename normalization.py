#!/home/d/Plocha/sb/coli/p3/bin/python3

import nltk.data
from nltk.tokenize import WordPunctTokenizer

from unicodedata import category as cat

def is_punctuation(word):
	return any(True for char in word if cat(char).startswith('P'))


sent_detector = nltk.data.load('tokenizers/punkt/czech.pickle')
wptokenizer = WordPunctTokenizer()


def normalize(text, lowercase=True, filter_interpunction=True):
	sent_tokenized = sent_detector.tokenize(text)

	normed = []
	for s in sent_tokenized:
		tok = wptokenizer.tokenize(s)

		if filter_interpunction:
			tok = filter(lambda t: not (is_punctuation(t) or t.isdigit()), tok)

		if lowercase:
			o = " ".join(map(lambda s: s.lower(), tok))
		else:
			o = " ".join(tok)
		normed.append(o)

	return normed


if __name__ == "__main__":

	from sys import argv, stderr, stdin, stdout

	#t = "jedou prý ve středu. Ty “úřední” kandidátky už se zase rozpl"
	#p = normalize(t)

	p = normalize(stdin.read(), filter_interpunction=True, lowercase=False)
	for l in p:
		print(l)
