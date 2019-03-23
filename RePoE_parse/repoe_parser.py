#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jeremy Parks
# Note: Requires Python 3.7.x or newer
import json
from os.path import join


# takes path to RePoE as only parameter
def process_json(path='C:\\git\\RePoE\\data'):
	with open(join(path, 'stat_translations.json'), 'r') as f:
		plaintext = json.load(f)
	with open(join(path, 'synthesis_implicits.json'), 'r') as f:
		synthesis = json.load(f)
	with open(join(path, 'mods.json'), 'r') as f:
		mods = json.load(f)

	pt = {}
	sy = {}
	m = {}

	for mod in plaintext:
		for id in mod['ids']:
			pt[id] = mod['English']

	for mod in mods:
		m[mod] = mods[mod]['stats']

	for mod in synthesis:
		sy[(mod['stat']['id'], abs(mod['stat']['value']))] = (mod['mods'], mod['item_classes'], mod['stat']['value'])

	output = {}
	for k in sorted(sy):
		if k[0] not in pt:
			lookup = {
				'essence_buff_elemental_damage_taken_+%': 'essence_display_elemental_damage_taken_while_not_moving_+%',
				'essence_buff_ground_fire_damage_to_deal_per_second': 'essence_display_drop_burning_ground_while_moving_fire_damage_per_second'
			}
			key = lookup[k[0]]
		else:
			key = k[0]

		if sy[k][2] < 0 and len(pt[key]) > 1:
			form = pt[key][1]
		else:
			form = pt[key][0]
		modstr = form['string'].format(*form['format'])
		for base in sy[k][1]:
			if base not in output:
				output[base] = {}
			if modstr not in output[base]:
				output[base][modstr] = []

			out = []
			for smod in sy[k][0]:
				vals = []
				for entry in m[smod]:
					if entry['min'] == entry['max']:
						vals.append(str(entry['min']))
					else:
						vals.append('({} - {})'.format(entry['min'], entry['max']))
				if m[smod][0]['min'] < 0 and len(pt[m[smod][0]['id']]) > 1:
					sform = pt[m[smod][0]['id']][1]
				else:
					sform = pt[m[smod][0]['id']][0]
				out.append(sform['string'].format(*vals))
			output[base][modstr].append((k[1], '\n'.join(out)))
		# ('100', '+(8 - 10) to maximum Life')
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
