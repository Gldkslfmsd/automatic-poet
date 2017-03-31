# Automatic poet

Automatic generator of accentual-syllabic poetry for Czech using N-gram model based on syllables.

## How to use it?

This project uses Python3, make sure you have NLTK and Punkt tokenizer installed. If `kytice` is a textfile containing
Czech text, then just type:

```
python3 automatic_poet.py -t kytice -N 3
```

Then you'll see:

```
reading text...
normalizing text...
splitting text to syllables...
accentizing...
creating model...
model ready!
 peklo  v sobě  nepo za  nic 
 v jedné  hlasy  vložte  je  nic 
 v hrobě  jiné  než  jak  máti 
 světla  blýskají  jí  po ti 
```

## Notice the help message

```
$ python3 automatic_poet.py --help
usage: automatic_poet.py [-h] [-N N] [-t TEXT] [-s SAVE_MODEL] [-l LOAD_MODEL]
                         [-p PATTERN] [--rhyme-pattern RHYME_PATTERN]
                         [-c USE_COMMON_PATTERN] [-r REPEAT]

optional arguments:
  -h, --help            show this help message and exit
  -N N                  N-gram model for given N will be used
  -t TEXT, --text TEXT  Textfile in UTF-8 encoding to open and create language
                        model.
  -s SAVE_MODEL, --save-model SAVE_MODEL
                        Language model will be created from text and saved to
                        a binary file for reusing. (Creation can take longer
                        time, this option can help to save it.)
  -l LOAD_MODEL, --load_model LOAD_MODEL
                        Language model will be loaded from binary file. Then
                        --text and -N arguments will be ignored.
  -p PATTERN, --pattern PATTERN
                        Pattern of stressed ('-') and non-stressed ('.')
                        syllables in a poem. Verses are separated by '|'.
                        Example: '-.-.|-.-.|-'
  --rhyme-pattern RHYME_PATTERN
                        Pattern of rhymes in a poem. Example: if we have
                        4-verse poem, 0123 is no rhyme, 0022 means first and
                        second pair of verses will rhyme
  -c USE_COMMON_PATTERN, --use-common-pattern USE_COMMON_PATTERN
                        Use common poem pattern. "trochee" for
                        "-.-.-.|-.-.-.|-.-.-.|-.-.-" with rhyme 0022 (this is
                        default), "dactyl" for
                        "-..-..-..|-..-..-.|-..-..-..|-..-..-." rhymed 0121.
  -r REPEAT, --repeat REPEAT
                        Repeat generation REPEAT number of times for more
                        strophes, default is once.
```

## Want to know more?

See report in `report` directory.

## Author and licence

Dominik Macháček

Creative Commons, 2017
