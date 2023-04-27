import requests
import time

def pad(v, n):
	s = str(v)
	return s + (' ' * (n-len(s)))

class Card:
	def __init__(self, name):
		self.name = name
		self.sets = []
		self.price = None

	def add_set_price(self, _set, price):
		if price is not None:
			self.sets.append(_set)
			if self.price is None:
				self.price = float(price)
			else:
				self.price = min(self.price,  float(price))

	def prset(self):
		if len(self.sets):
			return ','.join(self.sets)
		return '?'


class Want:
	def __init__(self, card, qty):
		self.card = card 
		self.qty = qty

	def subtotal(self):
		if self.card.price:
			return self.qty * self.card.price
		return '?'

	def __repr__(self):
		return "".join([
			pad(str(self.qty) + 'x', 5),
			pad(self.card.name, 60),
			pad('(' + self.card.prset() + ')', 35),
			str(self.subtotal())])


def gurl(url):
	r = requests.get(url)
	time.sleep(0.07) # respect api limits
	return r.json()

wants = {}
with open('wants.txt') as fin:
	for l in fin.readlines():
		sp = l.strip().replace('\t',' ').split(' ')
		qty, name = int(sp[0]), ' '.join([_.strip() for _ in sp[1:]])
		wants[name.lower()] = Want(Card(name), qty)

l_sets = gurl('https://api.scryfall.com/sets')['data']
for idx, _st in enumerate(l_sets):
	set_type = _st['set_type']
	if (set_type not in ['memorabilia', 'token', 'funny', 'arsenal', 'alchemy', 'spellbook', 'planechase', 'treasure_chest']) and _st['card_count'] > 100:
		code = _st['code']
		print(f"Collecting set {code} [{1 + idx}/{len(l_sets)}]")

		for _cd in gurl(f"https://api.scryfall.com/cards/search?q=s%3A{code}&order=eur")['data']:
			_name = _cd['name']
			_eu_price = _cd['prices']['eur']			

			if _name.lower() in wants:
				card = wants[_name.lower()].card
				card.add_set_price(code, _eu_price)
				wants[_name.lower()].card = card

for w in wants.values():
	print(w)


