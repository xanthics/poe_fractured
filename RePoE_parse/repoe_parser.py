#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jeremy Parks
# Note: Requires Python 3.7.x or newer
import json
from os.path import join


# Finds the correct entry for mods that have multiple variations
def findname(modmin, modmax, modlist):
	for v in modlist:
		if len(v['condition'][0]) > 1:
			if v['condition'][0]['min'] <= modmin and modmax <= v['condition'][0]['max']:
				return v
		if 'min' in v['condition'][0] and modmin >= v['condition'][0]['min']:
			return v
		if 'max' in v['condition'][0] and modmax <= v['condition'][0]['max']:
			return v
		if not v['condition'][0] and v['string']:
			return v
	print("{} - {}\n{}".format(modmin, modmax, '\n'.join([str(x) for x in modlist])))


# takes path to RePoE data as only parameter
def process_json(path='C:\\git\\RePoE\\data'):
	with open(join(path, 'stat_translations.json'), 'r') as f:
		plaintext = json.load(f)
	with open(join(path, 'synthesis_implicits.json'), 'r') as f:
		synthesis = json.load(f)
	with open(join(path, 'mods.json'), 'r') as f:
		mods = json.load(f)

	value_transforms = {
		"per_minute_to_per_second_2dp_if_required": 1/60,
		"per_minute_to_per_second_2dp": 1/60,
		"per_minute_to_per_second": 1/60,
		"milliseconds_to_seconds": 1/1000,
		"divide_by_one_hundred": 1/100,
		"negate": -1,
		"canonical_stat": 1
	}

	readable_name = {}
	synthesized_implicits = {}
	mods_full = {}

	for mod in plaintext:
		for idm in mod['ids']:
			readable_name[idm] = mod['English']

	for mod in mods:
		mods_full[mod] = mods[mod]['stats']

	counter = 0
	for mod in synthesis:
		synthesized_implicits[(mod['stat']['id'], abs(mod['stat']['value']), counter)] = (mod['mods'], mod['item_classes'], mod['stat']['value'])
		counter += 1

	output = {}
	for k in sorted(synthesized_implicits):
		if k[0] not in readable_name:
			lookup = {
				'essence_buff_elemental_damage_taken_+%': 'essence_display_elemental_damage_taken_while_not_moving_+%',
				'essence_buff_ground_fire_damage_to_deal_per_second': 'essence_display_drop_burning_ground_while_moving_fire_damage_per_second'
			}
			key = lookup[k[0]]
		else:
			key = k[0]

		if len(readable_name[key]) > 1:
			tval = 1 if synthesized_implicits[k][2] > 0 else -1
			form = findname(tval, tval, readable_name[key])
		else:
			form = readable_name[key][0]
		mult_ = 1
		if form['index_handlers'][0]:
			mult_ = abs(value_transforms[form['index_handlers'][0][0]])
		modstr = form['string'].format(*form['format'])
		for base in synthesized_implicits[k][1]:
			if base not in output:
				output[base] = {}
			if modstr not in output[base]:
				output[base][modstr] = []

			out = []
			for smod in synthesized_implicits[k][0]:
				temp = []
				for tmod in mods_full[smod]:
					sform = findname(tmod['min'], tmod['max'], readable_name[tmod['id']])
					if not sform:
						continue
					vals = []
					mult = 1
					if sform['index_handlers'][0]:
						mult = value_transforms[sform['index_handlers'][0][0]]
					if len(mods_full[smod]) > 1 and all([readable_name[entry['id']][0]['string'] == readable_name[mods_full[smod][0]['id']][0]['string'] for entry in mods_full[smod][1:]]):
						for entry in mods_full[smod]:
							if entry['min'] == entry['max']:
								vals.append('{}'.format(round(entry['min'] * mult, 2)))
							else:
								vals.append('({} - {})'.format(round(entry['min'] * mult, 2), round(entry['max'] * mult, 2)))
					else:
						if tmod['min'] == tmod['max']:
							vals.append('{}'.format(round(tmod['min'] * mult, 2)))
						else:
							vals.append('({} - {})'.format(round(tmod['min'] * mult, 2), round(tmod['max'] * mult, 2)))
					if not sform['string'].format(*vals):
						print(sform)
					newmod = sform['string'].format(*vals)
					if newmod not in temp:
						temp.append(newmod)
				out.append(', '.join(temp))
			output[base][modstr].append((round(k[1] * mult_, 2), '\n'.join(out)))
	sp = []
	buf = 'table = {\n'
	for base in sorted(output):
		buf += '\t"{}": {{\n'.format(base)
		for mod in sorted(output[base]):
			buf += '\t\t"{}": {},\n'.format(mod, output[base][mod])
			if any([str(x) in mod for x in [1, 2, 3, 4, 5, 6, 7, 8, 9]]):
				if mod not in sp:
					sp.append(mod)
		buf += '\t},\n'
	buf += '}'
	for s in sorted(sp):
		print('"{0}": "{0}",'.format(s))
	with open('..\\mod_table.py', 'w') as f:
		f.write(buf)


if __name__ == '__main__':
	process_json()
