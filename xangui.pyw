#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jeremy Parks
# Note: Requires Python 3.7.x or newer
# 		Plugin GUI framework for python projects

from tkinter import *
from tkinter.ttk import *
from fractured_watcher import FractureApp


class App:
	def __init__(self):
		# set up window
		self._root = Tk()
		self._root.title("Xan-GUI")
		self._root.protocol("WM_DELETE_WINDOW", self._onclosing)
		try:
			self._state = {'alpha': '1', 'theme': 'dark clam', 'clear': '1'}
			with open('settings.txt', 'r') as f:
				for line in f:
					line = line.strip().split(',')
					self._state[line[0]] = line[1]
		except (FileNotFoundError, IndexError):
			self._state = {'alpha': '1', 'theme': 'clam', 'clear': '1'}

		self._root.style = Style(self._root)
		self._themes = list(self._root.style.theme_names())
		self._customthemes()
		if self._state['theme'] in self._root.style.theme_names():
			self._root.style.theme_use(self._state['theme'])
		else:
			self._root.style.theme_use('default')

		# Set up our notebook.  There should be one for each window we want plus options
		self._root.tabbed = Notebook(self._root)
		self._tabbed_list = []
		self._root.tabbed.pack(fill=BOTH, expand=True)
		for tab in ['Fractured Mods', 'Options']:
			newtab = Frame(self._root.tabbed)
			self._tabbed_list.append(newtab)
			self._root.tabbed.add(newtab, text=tab)

		# create options first so that module windows can add to it
		self._options()
		self._fractured = FractureApp(self._tabbed_list[0], self._tabbed_list[-1], self._state['clear'])
		self._root.mainloop()

	def _onclosing(self):
		with open('settings.txt', 'w') as f:
			self._state['clear'] = self._fractured.autoclear
			for val in ['alpha', 'theme', 'clear']:
				f.write('{},{}\n'.format(val, self._state[val]))

		self._root.destroy()

	def _customthemes(self):
		s = self._root.style
		widgets = ['TButton', 'TCheckbutton', 'TCombobox', 'TEntry', 'TFrame', 'TLabel', 'TLabelframe', 'TMenubutton', 'TNotebook', 'TNotebook.Tab','TPanedwindow', 'Horizontal.TProgressbar', 'Vertical.TProgressbar',
				   'TRadiobutton', 'Horizontal.TScale', 'Vertical.TScale', 'Horizontal.TScrollbar', 'Vertical.TScrollbar', 'TSeparator', 'TSizegrip', 'Treeview']
		for theme in s.theme_names():

			newname = 'dark {}'.format(theme)
			self._themes.append(newname)
			s.theme_create(newname, theme)

			for e in widgets:
				vals = {}
				for v in ['foreground', 'background', 'activebackground', 'activeforeground', 'activeforeground', 'highlightbackground', 'highlightcolor', 'selectbackground', 'selectforeground', 'troughcolor']:
					oldval = s.lookup(e, v)
					if oldval:
						r, g, b = self._root.winfo_rgb(oldval)
						r = 65535 - r
						g = 65535 - g
						b = 65535 - b
						vals[v] = '#{:04x}{:04x}{:04x}'.format(r, g, b)
				s.theme_settings(newname, {e: {'configure': vals}})

	def _updateAlpha(self, event):
		self._state['alpha'] = event
		numevent = float(event)
		self._root.alphavalue['text'] = '{:.2f}'.format(numevent)
		self._root.wm_attributes('-alpha', numevent)

	def _updateTheme(self, event):
		self._state['theme'] = event
		self._root.style.theme_use(event)

	# Create an options screen on the last tab
	def _options(self):
		optiontab = self._tabbed_list[-1]
		# set transparency
		Label(optiontab, text="Transparency", borderwidth=2, relief="groove").grid(column=0, row=0)
		self._root.wm_attributes('-alpha', self._state['alpha'])
		Scale(optiontab, from_=.1, to=1, value=self._state['alpha'], orient=HORIZONTAL, command=self._updateAlpha).grid(column=1, row=0)
		self._root.alphavalue = Label(optiontab, text="1", borderwidth=2, relief="groove")
		self._root.alphavalue.grid(column=2, row=0)
		# set theme
		Label(optiontab, text="Theme", borderwidth=2, relief="groove").grid(column=0, row=1)
		OptionMenu(optiontab, StringVar(optiontab), self._root.style.theme_use(), *self._themes, command=self._updateTheme).grid(column=1, row=1)


if __name__ == '__main__':
	main = App()
