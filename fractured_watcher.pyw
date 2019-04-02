#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jeremy Parks
# Note: Requires Python 3.7.x or newer
import pyperclip
from tkinter import *
from tkinter.ttk import *
from bases import bases
from mod_table import table

# TODO: Handle non-fractured mods
# TODO: sum mods and show average needed for each result tier from other 2 items if synthesized.
class FractureApp:
	def __init__(self, rootwindow, optionwindow, clearstate):
		# keep track of recent state changes
		self.trigger = 0
		# update options window
		self.autoclear = self._add_option(optionwindow, clearstate)
		self._countdown = 10
		# Sorted list of bases (longest to shortest) for handling magic items
		self._base_list = sorted(bases.keys(), key=len, reverse=True)
		# keep track of what we have already seen on the clipboard
		self._old = ''
		# set up window
		self._root = rootwindow
		# set a theme
		# display clipboard stats
		self._clipboard_item = Label(self._root, text="Copy a fractured item to your keyboard", borderwidth=2, relief="groove", justify='center')
		self._clipboard_item.grid(sticky="ns", column=0, row=0, rowspan=10)
		self._clipboard_item.grid_columnconfigure(0, weight=1)
		# display base type
		self._base_type = Label(self._root, text="", borderwidth=2, relief="groove", font='TkFixedFont', anchor="w")
		self._base_type.grid(sticky='we', column=1, row=0)
		self._base_type.grid_columnconfigure(0, weight=1)
		self._base_type.grid_remove()
		# keep track of all the stat windows we create
		self._fracture_stat = []
		# enter timer function
		self._update_item()

	# return the current state of trigger.  Intended to be called 1x per second
	@property
	def trigger(self):
		if self.recent_update:
			self.recent_update -= 1

		return self.recent_update

	@trigger.setter
	def trigger(self, val):
		self.recent_update = val+1

	# return the current state of autoclear clipboard
	@property
	def autoclear(self):
		return self.clearcb.get()

	@autoclear.setter
	def autoclear(self, clearcb):
		self.clearcb = clearcb

	# adds relevant options to option window
	@staticmethod
	def _add_option(optionwindow, val):
		# set transparency
		clearcb = IntVar()
		clearcb.set(val)
		Checkbutton(optionwindow, text="Auto Clear Clipboard(10s)", variable=clearcb).grid(sticky='we', column=0, row=3, columnspan=2)
		return clearcb

	# Watches the clipboard and updates the window as necessary
	def _update_item(self):
		# get data from clipboard
		now = pyperclip.paste()
		# check for new item
		if self._old != now:
			# update countdown timer
			self._countdown = 10
			# update our last seen clip
			self._old = now
			# hide all extra boxes, they will show again when they have data
			self._base_type.grid_remove()
			for square in self._fracture_stat:
				square.grid_remove()
			# remove windows carriage returns
			now = now.replace('\r', '').strip()
			nowsplit = now.split('\n')
			# make sure 'Fractured Item' is in our clipboard
			# if not, display hint and create timer
			if 'Fractured Item' not in nowsplit:
				self.trigger = 0
				self._clipboard_item['text'] = "Copy a fractured item to your keyboard\nData is from PyPoE via RePoE"
				self._root.after(1000, self._update_item)
				return
			# we want to be fully visible for self._countdown ticks
			self.trigger = self._countdown
			# update main window item text
			self._clipboard_item['text'] = now
			modcount = 0
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
				print(f"Error with item: {nowsplit}")
				return
			self._base_type['text'] = f'Basetype: {bases[baseline]}'
			base = bases[baseline]
			self._base_type.grid()

			for line in nowsplit:
				# Check if line is a fractured mod
				if ' (fractured)' in line:
					if len(self._fracture_stat) <= modcount:
						# display first fractured mod and possible outcomes
						self._fracture_stat.append(Label(self._root, text="", borderwidth=2, relief="groove", justify='left', font='TkFixedFont', anchor="w"))
						self._fracture_stat[modcount].grid(sticky='we', column=1, row=modcount + 1)
						self._fracture_stat[modcount].grid_columnconfigure(0, weight=1)
					# Look up mod in our table and display information about it
					mod = line.replace(' (fractured)', '')
					self._fracture_stat[modcount]['text'] = f'Mod name: {mod}\n'
					self._fracture_stat[modcount]['text'] += self._findmods(base, mod)
					self._fracture_stat[modcount].grid()
					modcount += 1
		if self.autoclear and self._countdown > -1:
			if not self._countdown:
				pyperclip.copy('')
			self._countdown -= 1
		# call this function again in 1 second
		self._root.after(1000, self._update_item)

	# Given a base type and a mod, return formatted information about it
	@staticmethod
	def _findmods(base, mod):
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
			ret = f'{"Count":>8}|{"Result"}\n'
			for idx in range(len(table[base][val])):
				v = table[base][val][idx][1].split('\n')
				ret += f'{1 if not idx else table[base][val][idx-1][0] + 1:>7}+|{v[0]}\n'
				for _v in v[1:]:
					ret += f'{"":>8}|{_v}\n'
		else:
			ret = f'"{val}" on "{base}" is unrecognized.\nIf it isn\'t part of a hybrid, you have a "dead mod".\n'
		return ret[:-1]
