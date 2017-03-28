from czech_word_accentizer import PRIMARY, SECONDARY, UNSTRESSED

from nltk.probability import FreqDist, MLEProbDist
from collections import defaultdict
from itertools import product

def lam_zero():
	return 0

def lam_mle():
	return MLEProbDist(FreqDist())

def lam_defdict():
	return defaultdict(lam_zero)

class NmoGram:
	"""(N-1)-gram. """
	
	Nmo = None	
	def __init__(self,syl_acc):
		""":arg syl_acc: an (N-1) tuple of pairs (syllable, accent)
		After freezing, self.primary will be a probability distribution
		for generating of next syllable with primary stress from previous (N-1)-syllables.
		self.secondary and self.unstressed analogically.
		"""
		self.is_frozen = False
		self.syl_acc = syl_acc
		self.primary = defaultdict(lam_zero)
		self.secondary = defaultdict(lam_zero)
		self.unstressed = defaultdict(lam_zero)

	def add_next(self, syll_acc):
		"""In corpus we have seen an (N-1)-tuple of self.syl_acc followed by 
		:arg syll_acc."""
		if self.is_frozen:
			raise ValueError("can't add next to frozen nmo_tuple")
		syll, acc = syll_acc
		if acc == PRIMARY:
			self.primary[syll_acc] += 1
		elif acc == SECONDARY:
			self.secondary[syll_acc] += 1
		else:
			self.unstressed[syll_acc] += 1
		
	def freeze(self):
		"""After freeze, this instance is read-only."""
		if self.is_frozen:
			raise ValueError("already frozen")
		self.is_frozen = True
		self.primary_secondary = MLEProbDist(
			FreqDist(self.primary) + FreqDist(self.secondary)
			)
		self.unstressed_secondary = MLEProbDist(
			FreqDist(self.unstressed) + FreqDist(self.secondary)
			)

		self.primary = MLEProbDist(FreqDist(self.primary))
		self.secondary = MLEProbDist(FreqDist(self.secondary))
		self.unstressed = MLEProbDist(FreqDist(self.unstressed))

	def generate_next(self, stress):
		if not self.is_frozen:
			raise ValueError("you must freeze it before")
		if stress == PRIMARY:
			d = self.primary
		elif stress == SECONDARY:
			d = self.secondary
		elif stress == UNSTRESSED:
			d = self.unstressed
		elif stress in (PRIMARY+SECONDARY, SECONDARY+PRIMARY):
			d = self.primary_secondary
		else:
			d = self.unstressed_secondary
		return d.generate()



class NGramAccentualSyllabicModel:

	START = ("^", None)
	END = ("$",None)

	def create_nmo_gram(self, syll_acc):
		n = NmoGram(syll_acc)
		n.Nmo = self.N-1
		return n

	def n_grams(self, seq):
		""":arg seq: arbitrary sequence
		:returns sequence of N-tuples/N-grams from sequence"""
		s = [self.START]*(self.N-1) + list(seq) + [self.END]*(self.N-1)
		return zip(*(s[i:] for i in range(self.N)))

	def __init__(self, syllables, accents, N=1):
		""":arg syllables: a list of syllables from text
		:arg accents: a list of accents-marks corresponding with syllables
		:arg N: a positive integer"""
		self.N = N
#		self.NmoGram.Nmo = N-1
		
		# init is a dict from N-tuples of stress symbols -> N-grams of syllables
		# it's used for generating the very first syllables in a poem
		init = defaultdict(lam_defdict)
		nmo_grams = {}

		for ngram in self.n_grams(zip(syllables,accents)):
			*nmo_g, n = ngram
			nmo_g = tuple(nmo_g)
			if not nmo_g in nmo_grams:
				nmo_grams[nmo_g] = self.create_nmo_gram(nmo_g)

			nmo_grams[nmo_g].add_next(n)

			acc = tuple(s[1] for s in ngram)
			syl = tuple(s[0] for s in ngram)
			init[acc][ngram] += 1

		for n in nmo_grams.values():
			n.freeze()

		self.nmo_grams = nmo_grams

		self.init = defaultdict(lam_mle)
		for k in init.keys():
			self.init[k] = MLEProbDist(FreqDist(init[k]))

		# allowing secondary stress instead of primary or unstressed syllables...
		for sec in product([SECONDARY, ""], repeat=self.N):
			if sec==("",)*self.N: continue
			for key in product([PRIMARY, UNSTRESSED], repeat=self.N):
				add = tuple(SECONDARY if s==SECONDARY else k for s,k in zip(sec,key))
				self.init[tuple(k+s for k,s in zip(key,sec))] = MLEProbDist(
					FreqDist(init[key]) + FreqDist(init[add])
					)

	def generate_init(self, stress_Ntuple):
		return self.init[stress_Ntuple].generate()

	def generate_next(self, last_nmo_gram, stress):
		return self.nmo_grams[last_nmo_gram].generate_next(stress)


	def generate_verse(self, metrum, allow_secondary=True):
		if allow_secondary:
			metrum = [ m+SECONDARY for m in metrum ]
		
		i = self.generate_init(tuple(metrum[:self.N]))
		verse = list(i)
		for i,m in enumerate(metrum[self.N:]):
			j=i+self.N
			x = (('za ', 'secondary'),)
			#y = self.nmo_grams[x].generate()
			
			try:
				k = tuple(verse[-self.N+1:]) if self.N>1 else ()
				n = self.generate_next(k, m)
			except IndexError:
				n = self.generate_init(tuple(metrum[j-self.N+1:j+1]))
				for i in n:
					verse.append(i)
			#except KeyError:
			#	pass
			#	raise
			else:
				verse.append(n)
		#verse_str = "".join(s for s,_  in verse)
		return verse



