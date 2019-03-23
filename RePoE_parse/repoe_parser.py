#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jeremy Parks
# Note: Requires Python 3.7.x or newer
import json
from os.path import join


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
		"per_minute_to_per_second": 1/60,
		"milliseconds_to_seconds": 1/1000,
		"divide_by_one_hundred": 1/100,
		"negate": 1
	}

	readable_name = {}
	synthesized_implicits = {}
	mods_full = {}

	vals_ = []
	for mod in plaintext:
		for idm in mod['ids']:
			readable_name[idm] = mod['English']

	for mod in mods:
		mods_full[mod] = mods[mod]['stats']

	for mod in synthesis:
		synthesized_implicits[(mod['stat']['id'], abs(mod['stat']['value']))] = (mod['mods'], mod['item_classes'], mod['stat']['value'])

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

		if synthesized_implicits[k][2] < 0 and len(readable_name[key]) > 1:
			form = readable_name[key][1]
		else:
			form = readable_name[key][0]
		mult_ = 1
		if form['index_handlers'][0]:
			mult_ = value_transforms[form['index_handlers'][0][0]]
		modstr = form['string'].format(*form['format'])
		for base in synthesized_implicits[k][1]:
			if base not in output:
				output[base] = {}
			if modstr not in output[base]:
				output[base][modstr] = []

			out = []
			for smod in synthesized_implicits[k][0]:
				if mods_full[smod][0]['min'] < 0 and len(readable_name[mods_full[smod][0]['id']]) > 1:
					sform = readable_name[mods_full[smod][0]['id']][1]
				else:
					sform = readable_name[mods_full[smod][0]['id']][0]
				vals = []
				mult = 1
				if sform['index_handlers'][0]:
					mult = value_transforms[sform['index_handlers'][0][0]]
				for entry in mods_full[smod]:
					if entry['min'] == entry['max']:
						vals.append('{}'.format(round(entry['min'] * mult, 2)))
					else:
						vals.append('({} - {})'.format(round(entry['min'] * mult, 2), round(entry['max'] * mult, 2)))
				out.append(sform['string'].format(*vals))
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
