#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jeremy Parks
# Note: Requires Python 3.7.x or newer
import pyperclip
from tkinter import *
from tkinter.ttk import *
from bases import bases
from mod_table import table


class App:
	def __init__(self):
		# Sorted list of bases (longest to shortest) for handling magic items
		self.base_list = sorted(bases.keys(), key=len, reverse=True)
		# keep track of what we have already seen on the clipboard
		self.old = ''
		# set up window
		self.root = Tk()
		self.root.title("Fractured mod scanner")
		# set a theme
#		self.root.style = Style(self.root)
#		print(self.root.style.theme_names())
#		self.root.style.theme_use("default")
#		print(self.root.style.theme_use())
		# transparent
#		self.root.wait_visibility(self.root)
#		self.root.wm_attributes('-alpha', 0.3)
		# display clipboard stats
		self.clipboard_item = Label(self.root, text="Copy a fractured item to your keyboard", borderwidth=2, relief="groove", justify='center')
		self.clipboard_item.grid(sticky="ns", column=0, row=0, rowspan=10)
		self.clipboard_item.grid_columnconfigure(0, weight=1)
		# display base type
		self.base_type = Label(self.root, text="", borderwidth=2, relief="groove", font='TkFixedFont', anchor="w")
		self.base_type.grid(sticky='we', column=1, row=0)
		self.base_type.grid_columnconfigure(0, weight=1)
		self.base_type.grid_remove()
		# keep track of all the stat windows we create
		self.fracture_stat = []
		# enter timer function
		self.update_item()
		self.root.mainloop()

	# Watches the clipboard and updates the window as necessary
	def update_item(self):
		# get data from clipboard
		now = pyperclip.paste()
		# check for new item
		if self.old != now:
			# update our last seen clip
			self.old = now
			# hide all extra boxes, they will show again when they have data
			self.base_type.grid_remove()
			for square in self.fracture_stat:
				square.grid_remove()
			# remove windows carriage returns
			now = now.replace('\r', '').strip()
			nowsplit = now.split('\n')
			# make sure 'Fractured Item' is in our clipboard
			# if not, display hint and create timer
			if 'Fractured Item' not in nowsplit:
				self.clipboard_item['text'] = "Copy a fractured item to your keyboard\nData is from PyPoE via RePoE"
				self.root.after(1000, self.update_item)
				return
			# update main window item text
			self.clipboard_item['text'] = now
			modcount = 0
			base = ''
			# TODO: better logic for finding item mods
			# TODO: support for non-fractured mods
			baseline = ''
			if nowsplit[0] == 'Rarity: Magic':
				# Check if line is the name of a known item base
				if any(substring in nowsplit[1] for substring in bases.keys()):
					baseline = next(substring for substring in bases.keys() if substring in nowsplit[1])
			elif nowsplit[0] in ['Rarity: Rare', 'Rarity: Unique']:
				baseline = nowsplit[2]
			else:
				print("Error with item: {}".format(nowsplit))
				return
			if baseline in bases:
				self.base_type['text'] = 'Basetype: {}'.format(bases[baseline])
				base = bases[baseline]
				self.base_type.grid()

			for line in nowsplit:
				# Check if line is a fractured mod
				if ' (fractured)' in line:
					if len(self.fracture_stat) <= modcount:
						# display first fractured mod and possible outcomes
						self.fracture_stat.append(Label(self.root, text="", borderwidth=2, relief="groove", justify='left', font='TkFixedFont', anchor="w"))
						self.fracture_stat[modcount].grid(sticky='we', column=1, row=modcount+1)
						self.fracture_stat[modcount].grid_columnconfigure(0, weight=1)
					# Look up mod in our table and display information about it
					mod = line.replace(' (fractured)', '')
					self.fracture_stat[modcount]['text'] = 'Mod name: {}\n'.format(mod)
					self.fracture_stat[modcount]['text'] += self.findmods(base, mod)
					self.fracture_stat[modcount].grid()
					modcount += 1
		# call this function again in 1 second
		self.root.after(1000, self.update_item)

	# Given a base type and a mod, return formatted information about it
	def findmods(self, base, mod):
		# Some mods have static numbers in them.  Check those first before processing mod
		lookups = {
			"% Chance to Trigger Level 18 Summon Spectral Wolf on Kill": "#% Chance to Trigger Level 18 Summon Spectral Wolf on Kill",
			"% chance for Bleeding inflicted with this Weapon to deal 100% more Damage": "#% chance for Bleeding inflicted with this Weapon to deal 100% more Damage",
			"% chance for Poisons inflicted with this Weapon to deal 100% more Damage": "#% chance for Poisons inflicted with this Weapon to deal 100% more Damage",
			"% chance to Cast Level 20 Fire Burst on Hit": "#% chance to Cast Level 20 Fire Burst on Hit",
			"% chance to Gain Unholy Might for 4 seconds on Melee Kill": "#% chance to Gain Unholy Might for 4 seconds on Melee Kill",
			"% chance to Hinder Enemies on Hit with Spells, with 30% reduced Movement Speed": "#% chance to Hinder Enemies on Hit with Spells, with 30% reduced Movement Speed",
			"% chance to Intimidate Enemies for 4 seconds on Hit": "#% chance to Intimidate Enemies for 4 seconds on Hit",
			"% chance to Recover 10% of Maximum Mana when you use a Skill": "#% chance to Recover 10% of Maximum Mana when you use a Skill",
			"% chance to gain Onslaught for 3 seconds when Hit": "#% chance to gain Onslaught for 3 seconds when Hit",
			"% chance to gain Onslaught for 4 seconds on Kill": "#% chance to gain Onslaught for 4 seconds on Kill",
			"% chance to gain Phasing for 4 seconds on Kill": "#% chance to gain Phasing for 4 seconds on Kill",
			"% of Damage taken gained as Mana over 4 seconds when Hit": "#% of Damage taken gained as Mana over 4 seconds when Hit",
			"Has 1 Abyssal Socket": "Has 1 Abyssal Socket",
			"Socketed Gems have +3.5% Critical Strike Chance": "Socketed Gems have +3.5% Critical Strike Chance",
			"Triggers Level 20 Spectral Spirits when Equipped": "Triggers Level 20 Spectral Spirits when Equipped",
			"Your Hits inflict Decay, dealing 500 Chaos Damage per second for 8 seconds": "Your Hits inflict Decay, dealing 500 Chaos Damage per second for 8 seconds"		}
		val = ''
		if "Minions have " in mod and "% chance to Hinder Enemies on Hit with Spells, with 30% reduced Movement Speed" in mod:
			val = "Minions have #% chance to Hinder Enemies on Hit with Spells, with 30% reduced Movement Speed"
		else:
			for l in lookups:
				if l in mod:
					val = lookups[l]
					break
		# If mod is not one of the special cases replace all the numbers with '#'
		if not val:
			val = mod
			for n in range(10):
				if str(n) in val:
					val = val.replace(str(n), '#')
			val = val.replace('#.#', '#')
			while '##' in val:
				val = val.replace('##', '#')
		# Check if mod is in our lookup table
		if val in table[base]:
			ret = '{:>8}|{}\n'.format('Count', "Result")
			for idx in range(len(table[base][val])):
				v = table[base][val][idx][1].split('\n')
				ret += '{:>7}+|{}\n'.format(1 if not idx else table[base][val][idx-1][0] + 1, v[0])
				for _v in v[1:]:
					ret += '{:>8}|{}\n'.format('', _v)
		else:
			ret = '"{}" on "{}" is unrecognized.\nIf it isn\'t part of a hybrid, you have a "dead mod".\n'.format(val, base)
		return ret[:-1]


if __name__ == '__main__':
	main = App()
