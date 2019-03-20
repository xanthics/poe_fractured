#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jeremy Parks
# Note: Requires Python 3.7.x or newer
import json
import re


def cleanhtml(raw_html):
	cleanr = re.compile('<(?!(br|li)).*?>')
	cleantext = re.sub(cleanr, '', raw_html)
	return cleantext


items = {}
with open('poedb.json', 'r') as f:
	vals = json.load(f)
	table = {}
	for v in vals['data']:
		temp = [cleanhtml(x).replace('&ndash;', ' - ').replace('<br>', ', ').replace('<li>', '\n').strip() for x in v]
		if int(temp[1]) < 0:
			temp[0] = temp[0].replace('increased', 'reduced').replace('+', '-')
			temp[1] = str(int(temp[1]) * -1)
		for base in temp[2].split(','):
			base = base.strip()
			if base[-1] == 's' and base not in ['Gloves', "Boots"]:
				base = base[:-1]
			if base not in items:
				items[base] = {}
			if temp[0] not in items[base]:
				items[base][temp[0]] = []
			items[base][temp[0]].append((temp[1], temp[3]))

sp = []
buf = 'table = {\n'
for base in items:
	buf += '\t"{}": {{\n'.format(base)
	for mod in items[base]:
		buf += '\t\t"{}": {},\n'.format(mod, items[base][mod])
		if any([str(x) in mod for x in [1,2,3,4,5,6,7,8,9]]):
			if mod not in sp:
				sp.append(mod)
	buf += '\t},\n'
buf += '}'
for s in sp:
	print('"{0}": "{0}",'.format(s))
with open('..\\mod_table.py', 'w') as f:
	f.write(buf)
