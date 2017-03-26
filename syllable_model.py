
import re
import random

from ngram import *

from text2syl import text2syl
from czech_word_accentizer import accentize
from normalization import normalize

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


from czech_word_accentizer import PRIMARY, SECONDARY, UNSTRESSED
from czech_word_accentizer import stress_types

from nltk.probability import FreqDist, MLEProbDist
from collections import Counter, defaultdict
from itertools import combinations, product

import pprint



class NGramAccentualSyllabicModel:

	START = ("^", None)
	END = ("$",None)

	# (N-1)-gram
	class NmoGram:
		Nmo = None	
		def __init__(self,syl_acc):
			self.is_frozen = False
			self.syl_acc = syl_acc
			self.primary = defaultdict(lambda: 0)
			self.secondary = defaultdict(lambda: 0)
			self.unstressed = defaultdict(lambda: 0)

		def add_next(self, syll_acc):
			syll, acc = syll_acc
			if acc == PRIMARY:
				self.primary[syll] += 1
			elif acc == SECONDARY:
				self.secondary[syll] += 1
			else:
				self.unstressed[syll] += 1
			
		def freeze(self):
			if self.is_frozen:
				raise ValueError("already frozen")
			self.primary_secondary = MLEProbDist(
				FreqDist(self.primary) + FreqDist(self.secondary)
				)
			self.unstressed_secondary = MLEProbDist(
				FreqDist(self.unstressed) + FreqDist(self.secondary)
				)

			self.primary = MLEProbDist(FreqDist(self.primary))
			self.secondary =MLEProbDist(FreqDist(self.secondary))
			self.unstressed =MLEProbDist(FreqDist(self.unstressed))

		def generate_next(self, stress):
			print(stress)
			if not self.is_frozen:
				raise ValueError("you must freeze it before")
			if stress == PRIMARY:
				d = self.primary
			elif stress == SECONDARY:
				d = secondary
			elif stress == UNSTRESSED:
				d = unstressed
			elif stress in (PRIMARY+SECONDARY, SECONDARY+PRIMARY):
				d = primary_secondary
			else:
				d = unstressed_secondary
			return d.generate()

	def n_grams(self, seq):
		s = [self.START]*(self.N-1) + list(seq) + [self.END]*(self.N-1)
		return zip(*(s[i:] for i in range(self.N)))

	def __init__(self, syllables, accents, N=1):
		
		self.N = N
		self.NmoGram.Nmo = N-1
		init = defaultdict(lambda: defaultdict(lambda: 0))
		nmo_grams = {}

		for ngram in self.n_grams(zip(syllables,accents)):
			*nmo_g, n = ngram
			nmo_g = tuple(nmo_g)
			if not nmo_g in nmo_grams:
				nmo_grams[nmo_g] = self.NmoGram(nmo_g)

			nmo_grams[nmo_g].add_next(n)

			acc = tuple(s[1] for s in ngram)
			syl = tuple(s[0] for s in ngram)
			init[acc][syl] += 1

		for n in nmo_grams.values():
			n.freeze()

		self.nmo_grams = nmo_grams


		self.init = defaultdict(lambda: MLEProbDist(FreqDist()))
		for k in init.keys():
			self.init[k] = MLEProbDist(FreqDist(init[k]))

		# allowing secondary stress...
		for sec in product([SECONDARY, ""], repeat=self.N):
			if sec==("",)*self.N: continue
			for key in product([PRIMARY, UNSTRESSED], repeat=self.N):
				add = tuple(SECONDARY if s==SECONDARY else k for s,k in zip(sec,key))
				print("přidávám", tuple(k+s for k,s in zip(key,sec)))
				self.init[tuple(k+s for k,s in zip(key,sec))] = MLEProbDist(
					FreqDist(init[key]) + FreqDist(init[add])
					)


		p = pprint.pformat(self.init)
		print(p)


	def generate_init(self, stress_Ntuple):
		print(stress_Ntuple)
		return self.init[stress_Ntuple].generate()

	def generate_next(self, last_nmo_gram, stress):
		return self.nmo_grams[last_nmo_gram].generate_next(stress)


	def generate_verse(self, metrum, allow_secondary=True):
		if allow_secondary:
			metrum = [ m+SECONDARY for m in metrum ]
		
		i = self.generate_init(tuple(metrum[:self.N]))
		verse = list(i)
		for i,m in enumerate(metrum[self.N:]):
			j=i+1
			try:
				n = self.generate_next(tuple(verse[-self.N:]), m)
			except KeyError:
				n, *_ = self.generate_init(tuple(metrum[j-self.N+1:j+1]))
			verse.append(n)
		print(verse)
		return verse




class PoemGenerator:

	trochee = ("-. -. -. -.|"*4)[:-1]
	iamb = (".- .- .- .-|"*4)[:-1]
	dactyl = ("-.. -.. -.. | -.. -.. -.|" *2)[:-1]


	def __init__(self, model):
		self.model = model



	def generate_form(self, form):
		form = "".join(c for c in form if c!=" ")
		verses = form.split("|")

		poem = []
		for v in verses:
			metrum = [ (PRIMARY if m=="-" else UNSTRESSED) for m in v ]
			verse = self.model.generate_verse(metrum)
			poem.append(verse)

		print(poem)
		print("\n".join("".join(v) for v in poem))

	
		


import pickle
import os.path
def main():
	from sys import argv, stderr, stdin, stdout
	if not os.path.exists("vse.p") or True:
		text = stdin.read()
		normed = normalize(text)
		print("normalizován text")
		ls = [ text2syl(s) for s in normed ]
		print("sylabifikace")
		la = [ accentize(s) for s in ls ]
		print("akcenty")
		syll = [ item for sublist in ls for item in sublist ]
		accents = [ item for sublist in la for item in sublist ]
		print("flatten")
#		pickle.dump( (syll, accents), open("vse.p", "wb"))
#		print("uloženo")
	else:
		syll, accents = pickle.load(open("vse.p", "rb"))

	print("predzpracovane_nacteno")
	m = NGramAccentualSyllabicModel(syll, accents, N=2)

	pg = PoemGenerator(m)
	pg.generate_form(PoemGenerator.dactyl)



if __name__ == "__main__":
	main()

