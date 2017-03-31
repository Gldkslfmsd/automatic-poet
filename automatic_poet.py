from syllable_model import NGramAccentualSyllabicModel
from czech_word_accentizer import PRIMARY, SECONDARY, UNSTRESSED
from czech_word_accentizer import accentize
from text2syl import text2syl
from normalization import normalize


class PoemGenerator:

	trochee = ("-.-.-.-.|"*4)[:-1]
	iamb = (".-.-.-.-|"*4)[:-1]
	dactyl = ("-..-..-..|-..-..-.|" *2)[:-1]


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
		ptext = "\n".join("".join(s for s,_ in verse) for verse in poem)
		# we replace ~ which was used for joining of unsyllabled
		# prepositions to the next syllable
		return ptext.replace("~"," ")
				

	def generate_form(self, form, rhymes=None, allow_first_secondary=False):
		form = "".join(c for c in form if c!=" ")
		verses = form.split("|")

		poem = []
		# in first verse, secondary stress instead of primary or unstressed
		# is not allowed, in other verses it is
		f = allow_first_secondary
		for v in verses:
			metrum = [ (PRIMARY if m=="-" else UNSTRESSED) for m in v ]	
			verse = self.model.generate_verse(metrum, allow_secondary=f)
			f = True
			poem.append(verse)
		
		if rhymes:
			self.add_rhymes(poem, rhymes=rhymes)
		
		
		return poem
	
	def generate_poem_text(self, form, rhymes=None, **kw):
		p = self.generate_form(form, rhymes, **kw)
		return self.poem2text(p)


	def generate_common_pattern(self, pattern):
		if pattern == "trochee":
			return self.generate_poem_text(self.trochee, rhymes=(0,0,2,2))
		if pattern == "dactyl":
			return self.generate_poem_text(self.dactyl, rhymes=(0,1,2,1), allow_first_secondary=True)



if __name__ == "__main__":

	# suppres annoying warning from nltk
	import warnings
	warnings.catch_warnings()
	warnings.simplefilter("ignore", category=UserWarning)


	import pickle
	import argparse
	from sys import stderr, exit

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

	parser.add_argument(
		'-p', '--pattern',
		help="Pattern of stressed ('-') and non-stressed ('.') syllables in "
		"a poem. Verses are separated by '|'. "
		"Example: '-.-.|-.-.|-'",
		default=PoemGenerator.trochee,
		type=str,
		)

	parser.add_argument(
		'--rhyme-pattern',
		help="Pattern of rhymes in a poem. Example: if we have 4-verse "
		"poem, 0123 is no rhyme, 0022 means first and second pair of "
		"verses will rhyme",
		default="0022",
		type=str,
		)

	parser.add_argument(
		'-c', '--use-common-pattern',
		help='Use common poem pattern. "trochee" for '
		'"-.-.-.|-.-.-.|-.-.-.|-.-.-" with rhyme 0022 (this is default), '
		'"dactyl" for "-..-..-..|-..-..-.|-..-..-..|-..-..-." rhymed 0121.',
		type=str,
		default=None,
		)

	parser.add_argument(
		'-r', '--repeat',
		help='Repeat generation REPEAT number of times for more strophes, default is once.',
		default=1,
		type=int
		)
	args = parser.parse_args()

	# checking verse pattern
	pattern = args.pattern
	if any(map(lambda x: x not in "-.|",pattern)):
		print("invalid pattern, exiting",file=stderr)
		exit(1)

	# cheching lenght of verses
	for s in pattern.split("|"):
		if len(s)<args.N:
			print("verse is too short. N-gram model is used for "
			"N=%s, minimal number of syllables in a verse is %s"
			% (args.N, args.N))
			exit(1)

	# checking rhyme pattern
	try:
		rp = args.rhyme_pattern
		rhymes = tuple(int(r) for r in rp)
	except ValueError:
		print("invalid rhyme pattern, exiting")
		exit(1)
		
	# checking common pattern:
	if args.use_common_pattern and args.use_common_pattern not in ["dactyl", "trochee"]:
		print("invalid common pattern, only 'dactyl' or 'trochee' is available, exiting", file=stderr)
		exit(1)
		
	# checking textfile is present
	if not args.text:
		print("input textfile not specified. Use --help argument to see help-message.", file=stderr)
		exit(1)
		

	# loading and processing data
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
	for _ in range(args.repeat):
		if args.use_common_pattern:
			p = pg.generate_common_pattern(args.use_common_pattern)
		else:
			p = pg.generate_poem_text(pattern, rhymes=rhymes)
		print(p)
		print()


