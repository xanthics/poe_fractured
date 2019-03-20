import pyperclip
import tkinter as tk
from bases import bases
from mod_table import table


class App:
	def __init__(self):
		self.old = ''
		self.root = tk.Tk()
		self.root.title("Fractured mod scanner")
		# display clipboard stats
		self.clipboard_item = tk.Label(self.root, text="Copy a fractured item to your keyboard", borderwidth=2, relief="groove")
		self.clipboard_item.grid(column=0, row=0, rowspan=4)
		# display base type
		self.base_type = tk.Label(self.root, text="", borderwidth=2, relief="groove", font='TkFixedFont')
		self.base_type.grid(column=1, row=0)
		self.base_type.grid_remove()
		# display first fractured mod and possible outcomes
		self.first = tk.Label(self.root, text="", borderwidth=2, relief="groove", justify='left', font='TkFixedFont')
		self.first.grid(column=1, row=1)
		self.first.grid_remove()
		# display second fractured mod and possible outcomes
		self.second = tk.Label(self.root, text="", borderwidth=2, relief="groove", justify='left', font='TkFixedFont')
		self.second.grid(column=1, row=2)
		self.second.grid_remove()
		# display third fractured mod and possible outcomes
		self.third = tk.Label(self.root, text="", borderwidth=2, relief="groove", justify='left', font='TkFixedFont')
		self.third.grid(column=1, row=3)
		self.third.grid_remove()

		self.fracture_stat = [self.first, self.second, self.third]

		self.update_item()
		self.root.mainloop()

	def update_item(self):
		now = pyperclip.paste()
		# check for new item
		if self.old != now:
			# update our last seen clip
			self.old = now
			# hide all extra boxes, they will show again when they have data
			self.base_type.grid_remove()
			self.first.grid_remove()
			self.second.grid_remove()
			self.third.grid_remove()
			# remove windows carriage returns
			now = now.replace('\r', '').strip()
			nowsplit = now.split('\n')
			# make sure 'Fractured Item' is in our clipboard
			if 'Fractured Item' not in nowsplit:
				self.clipboard_item['text'] = "Copy a fractured item to your keyboard"
				self.root.after(1000, self.update_item)
				return
			# update main window item text
			self.clipboard_item['text'] = now
			modcount = 0
			base = ''
			for line in nowsplit:
				if line in bases:
					self.base_type['text'] = 'Basetype: {}'.format(bases[line])
					base = bases[line]
					self.base_type.grid()
				if '(fractured)' in line:
					mod = line.replace(' (fractured)', '')
					self.fracture_stat[modcount]['text'] = 'Mod name: {}\n'.format(mod)
					self.fracture_stat[modcount]['text'] += self.findmods(base, mod)
					self.fracture_stat[modcount].grid()
					modcount += 1

		self.root.after(1000, self.update_item)

	def findmods(self, base, mod):
		lookups = {
			"Has 1 Abyssal Socket": "Has 1 Abyssal Socket",
			"% chance to gain Onslaught for 3 seconds when Hit": "#% chance to gain Onslaught for 3 seconds when Hit",
			"% chance to gain Onslaught for 4 seconds on Kill": "#% chance to gain Onslaught for 4 seconds on Kill",
			"% chance to Recover 10% of Maximum Mana when you use a Skill": "#% chance to Recover 10% of Maximum Mana when you use a Skill",
			"% of Damage taken gained as Mana over 4 seconds when Hit": "#% of Damage taken gained as Mana over 4 seconds when Hit",
			"% Chance to Trigger Level 18 Summon Spectral Wolf on Kill": "#% Chance to Trigger Level 18 Summon Spectral Wolf on Kill",
			"% chance to Hinder Enemies on Hit with Spells, with 30% reduced Movement Speed": "#% chance to Hinder Enemies on Hit with Spells, with 30% reduced Movement Speed",
			"% chance to gain Phasing for 4 seconds on Kill": "#% chance to gain Phasing for 4 seconds on Kill",
			"% chance to Gain Unholy Might for 4 seconds on Melee Kill": "#% chance to Gain Unholy Might for 4 seconds on Melee Kill",
			"% chance to Cast Level 20 Fire Burst on Hit": "#% chance to Cast Level 20 Fire Burst on Hit",
			"Your Hits inflict Decay, dealing 500 Chaos Damage per second for 8 seconds": "Your Hits inflict Decay, dealing 500 Chaos Damage per second for 8 seconds",
			"% chance to Intimidate Enemies for 4 seconds on Hit": "#% chance to Intimidate Enemies for 4 seconds on Hit",
			"% chance for Poisons inflicted with this Weapon to deal 100% more Damage": "#% chance for Poisons inflicted with this Weapon to deal 100% more Damage",
			"% chance for Bleeding inflicted with this Weapon to deal 100% more Damage": "#% chance for Bleeding inflicted with this Weapon to deal 100% more Damage"
		}
		val = ''
		if "Minions have " in mod and "% chance to Hinder Enemies on Hit with Spells, with 30% reduced Movement Speed" in mod:
			val = "Minions have #% chance to Hinder Enemies on Hit with Spells, with 30% reduced Movement Speed"
		else:
			for l in lookups:
				if l in mod:
					val = lookups[l]
					break
		if not val:
			val = mod
			for n in range(10):
				if str(n) in val:
					val = val.replace(str(n), '#')
			val = val.replace('#.#', '#')
			while '##' in val:
				val = val.replace('##', '#')
		if val in table[base]:
			ret = '{:>8}|{}\n'.format('Count', "Result")
			for idx in range(len(table[base][val])):
				v = table[base][val][idx][1].split('\n')
				ret += '{:>7}+|{}\n'.format(0 if not idx else table[base][val][idx-1][0], v[0])
				for _v in v[1:]:
					ret += '{:>8}|{}\n'.format('', _v)
		else:
			ret = '"{}" is an unrecognized mod for "{}"\n'.format(val, base)
		return ret[:-1]


if __name__ == '__main__':
	main = App()
