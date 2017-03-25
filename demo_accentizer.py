from czech_word_accentizer import accentize
from syllable_model import text2syl

# JIZVY Václav Nebřenský 
# http://nebrensky.info/okenko/index.html

jizvy = """
Padlo dítě v širém poli
brečí že to silně bolí
Neplač tolik, milé robě
kvůli na koleni skobě
horší jizva je na duši
Zatím to fakan netuší
Zaplať pánbůh za věk dětský
připraví na větší pecky
""".lower().splitlines()

demosent="vykoupal-li on sebe i jeho ve vodě z řeky"
demosent="sporů mezi havlem a zákonodárným sborem postupně příbývalo"
demosent="""místo padlého klausova kabinetu zformoval prezident svoji
úřednickou vládu což posílilo jeho roli v politice ale jen na omezenou
dobu"""
#print(text2syl(demosent))


def demo(demosent):
	syl = text2syl(demosent)
	a = accentize(syl)
	print([s+"/"+b for s,b in zip(syl,a)])

for j in jizvy:
	demo(j)


