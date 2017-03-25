#!/usr/bin/env python3

"""Czech word-accentizer -- assign word-stress to Czech sentence."""

# Accentizer is a finite state transducer.
# It takes a sequence of syllables and tranlates it to a sequence of following
# symbols according their stress:
PRIMARY="primary"  
UNSTRESSED="unstressed"
SECONDARY="secondary" 

# We distinguish syllables on input by following types (so in fact the input
# alphabet has only 5 symbols):
# -- primary monosyllabic preposition
# -- enclitic
# -- other monosyllabic word
# -- start-of-word syllable
# -- other 

# primary monosyllabic prepositions -- in Czech they're so called proclitics, they
# take a primary accent from following word 
PMP = """ze od do u bez za ke ve o pro přes ob při nad
před skrz po na pod ku""".split()
PMP = [ " "+p+" " for p in PMP ]

def is_pmp(syllable):
	return syllable in PMP

# NOTE: "se" is an ambiguous word, it can be either a preposition or
# an enclitical reflexive pronoun. An advanced analysis should be used to
# destinguish it, but for simplicity we don't do it and simply mark it as an
# enclitic.

# enclitics -- they usually don't have their own accent
enclitics = [
# an auxiliary "to be"
	" jsem ", " jsi ", " jsme ", " jste ", " bych ", " bys ", " by ", 
# reflexive pronouns:
	" si ", " se ", 
# short forms of personal pronouns in Dative:
	" mi ", " ti ", " mu ", " jí ", " ní ",
# short forms of personal pronouns in Accusative:
	" mě ", " tě ", " ho ", " to ", " tu "
]

def is_enclitic(syllable):
	return syllable in enclitics

def is_monosyllabic_word(syll):
	return syll.startswith(" ") and syll.endswith(" ")

def is_new_word(syll):
	return syll[0] == " "




# states have indices 0 to 3, they transmit following symbols:
states = [ PRIMARY, UNSTRESSED, SECONDARY, PRIMARY ] 
	# read "state 0 transmits PRIMARY stressed syllable" etc.

def initial_state(syll):
	"""syll: a first syllable in a sentence
	returns: the first state
	"""
	if is_pmp(syll):
		return 3
	elif is_monosyllabic_word(syll):
		return 2
	else:
		return 0

def next_state(state, syll):
	"""state: number of current state
	syll: next syllable
	returns: number of next state
	"""
	if state == 0:
		if is_pmp(syll):
			return 3
		elif is_enclitic(syll):
			return 1
		elif is_monosyllabic_word(syll):
			return 2
		elif is_new_word(syll):
			# this shouldn't happen, one syllabic words have secondary
			# stress
			return 1
		else: # normal syllable
			return 1

	elif state == 1:
		if is_pmp(syll):
			return 3
		elif is_enclitic(syll):
			return 2
		elif is_monosyllabic_word(syll):
			return 2
		elif is_new_word(syll):
			return 0
		else: # normal syllable in next word
			return 2
	
	elif state == 2:
		if is_pmp(syll):
			return 3
		elif is_enclitic(syll):
			return 1
		elif is_monosyllabic_word(syll):
			return 2  # let's try this, but I'm not sure here, maybe send it to 0?
		elif is_new_word(syll):
			return 0
		else: # normal syllable in next word
			return 1


	else:  # state == 3
		if is_pmp(syll):
			# two prepositions next to each other usually 
			# doesn't happen, but could (in theory) 
			return 1  		
		elif is_enclitic(syll):
			return 1
		elif is_monosyllabic_word(syll):
			return 1
		elif is_new_word(syll):
			return 1
		else:  # this shouldn't happen, there's always a new word after
			# a preposition
			return 1




def accentize(syllables):
	"""syllables: list of syllables in one sentence, where syllables
	on the beginning of a word start with a space, end-word syllables end
	with a space
	Example:
	"On odešel domů" => [" on "," o","de","šel "," do","mů "]
	"""

	current_state = initial_state(syllables[0])
	accents = [ states[current_state] ]
	for s in syllables[1:]:
		current_state = next_state(current_state, s)
		accents.append(states[current_state])
	
	return accents


