
from syllable_model import *



class PoemGenerator:

	trochee = ("-. -. -. -.|"*4)[:-1]
	iamb = (".- .- .- .-|"*4)[:-1]
	dactyl = ("-.. -.. -.. | -.. -.. -.|" *2)[:-1]


	def __init__(self, model):
		self.model = model


	def add_rhymes(self, poem, rhymes):
		""":arg poem: output of self.generate_form, e.g.
		[[(' ně', 'primary'), ('jak ', 'unstressed'), (' pras', 'primary'), ('ka', 'unstressed')], 
		[(' si ', 'secondary'), (' však ', 'secondary'), (' kva', 'primary'), ('sit ', 'unstressed')]]
		
		:arg rhymes: tuple of numbers, they're indeces to poem list
		 e.g. (0,0) means that last syllable of 1st verse will be written as the last syllable of 2nd verse so
		 they will rhyme.
		"""
		d = {}
		for i,verse in zip(rhymes, poem):
			if i not in d:
				d[i] = verse[-1]
			else:
				verse[-1] = d[i]
		
		return poem
	
	def poem2text(self, poem):
		""":arg poem: list of verses, where verse is a list of pairs ("syllable", "stress")
		:returns: a single string
		"""
		
		return "\n".join("".join(s for s,_ in verse) for verse in poem)
				

	def generate_form(self, form, rhymes=None):
		form = "".join(c for c in form if c!=" ")
		verses = form.split("|")

		poem = []
		f = False
		for v in verses:
			metrum = [ (PRIMARY if m=="-" else UNSTRESSED) for m in v ]	
			verse = self.model.generate_verse(metrum, allow_secondary=f)
			f = True
			poem.append(verse)
		
		if rhymes:
			self.add_rhymes(poem, rhymes=rhymes)
		
		
		return poem
	
	def generate_poem_text(self, form, rhymes=None):
		p = self.generate_form(form, rhymes)
		return self.poem2text(p)


if __name__ == "__main__":

	# suppres annoying warning from nltk
	import warnings
	warnings.catch_warnings()
	warnings.simplefilter("ignore", category=UserWarning)


	import pickle
	import argparse
	from sys import stderr

	parser = argparse.ArgumentParser()
	parser.add_argument(	
		"-N", help="N-gram model for given N will be used", type=int,
		default=2
		)
	parser.add_argument(
		"-t", "--text", 
		help="Textfile in UTF-8 encoding to open and create language model.",
		type=argparse.FileType('r')
		)

	parser.add_argument(
		'-s', '--save-model',
		help="Language model will be created from text and saved to "
		"a binary file for reusing. (Creation can take longer time, this "
		"option can help to save it.)",
		type=argparse.FileType("wb")
		)

	parser.add_argument(
		'-l', '--load_model',
		help="Language model will be loaded from binary file. Then --text "
		"and -N arguments will be ignored.",
		type=argparse.FileType("rb"),
		default=None
		)
	args = parser.parse_args()

	if args.load_model:
		print("loading model...", file=stderr)
		model = pickle.load(args.load_model)
		print("...model loaded", file=stderr)
	else:
		print("reading text...", file=stderr)
		text = args.text.read()
		print("normalizing text...", file=stderr)
		normed = normalize(text)
		print("splitting text to syllables...", file=stderr)
		ls = [ text2syl(s) for s in normed ]
		print("accentizing...", file=stderr)
		la = [ accentize(s) for s in ls ]
		syll = [ item for sublist in ls for item in sublist ]
		accents = [ item for sublist in la for item in sublist ]

		print("creating model...", file=stderr)
		model = NGramAccentualSyllabicModel(syll, accents, N=args.N)
		print("model ready!", file=stderr)

	if args.save_model:
		print("saving model...", file=stderr)
		pickle.dump(model, args.save_model)
		print("...model saved", file=stderr)

	pg = PoemGenerator(model)
	for _ in range(3):
		p = pg.generate_poem_text("-.-.|-.-.", rhymes=(0,0))
		print(p)
		print()


