#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jeremy Parks
# Note: Requires Python 3.7.x or newer
# 		Plugin GUI framework for python projects

from tkinter import *
from tkinter.ttk import *
from fractured_watcher import FractureApp
from json import load, dump
import os


def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


# TODO: save window location
# TODO: Stay on top
class App:
	def __init__(self):
		# set up window
		self._root = Tk()
		self._root.title("Xan-GUI")
		self._root.iconbitmap(resource_path("favicon.ico"))
		self._root.protocol("WM_DELETE_WINDOW", self._onclosing)
		default_state = {'alpha': '1', 'theme': 'clam', 'clear': '1', 'trigger': '0', 'window state': '200x115+0+0'}
		try:
			with open('settings.json', 'r') as f:
				self._state = load(f)
		except (FileNotFoundError, TypeError):
			self._state = {}
			print("Something went wrong, using defaults.")
		for val in set(default_state.keys()).difference(set(self._state.keys())):
			self._state[val] = default_state[val]
		self._root.geometry(self._state['window state'])
		self._root.geometry("")

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
		# enter timer function
		self._flip = 0  # so that we only change the alpha once per direction
		self._check_trigger()

		self._root.mainloop()

	def _check_trigger(self):
		if self._state['autoalpha'].get() and self._fractured.trigger:
			if self._flip:
				self._flip = ~self._flip
				self._root.wm_attributes('-alpha', 1.0)
		elif not self._flip:
			self._flip = ~self._flip
			self._root.wm_attributes('-alpha', self._state['alpha'])

		self._root.after(1000, self._check_trigger)

	def _onclosing(self):
		with open('settings.json', 'w') as f:
			self._state['window state'] = self._root.geometry()
			self._state['clear'] = self._fractured.autoclear
			self._state['trigger'] = self._state['autoalpha'].get()
			del self._state['autoalpha']
			dump(self._state, f)

		self._root.destroy()

	def _customthemes(self):
		s = self._root.style
		widgets = ['TButton', 'TCheckbutton', 'TCombobox', 'TEntry', 'TFrame', 'TLabel', 'TLabelframe', 'TMenubutton', 'TNotebook', 'TNotebook.Tab', 'TPanedwindow', 'Horizontal.TProgressbar', 'Vertical.TProgressbar',
				   'TRadiobutton', 'Horizontal.TScale', 'Vertical.TScale', 'Horizontal.TScrollbar', 'Vertical.TScrollbar', 'TSeparator', 'TSizegrip', 'Treeview']
		for theme in s.theme_names():

			newname = f'dark {theme}'
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
						vals[v] = f'#{r:04x}{g:04x}{b:04x}'
				s.theme_settings(newname, {e: {'configure': vals}})

	def _updateAlpha(self, event):
		self._state['alpha'] = event
		numevent = float(event)
		self._root.alphavalue['text'] = f'{numevent:.2f}'
		self._root.wm_attributes('-alpha', numevent)

	def _updateTheme(self, event):
		self._state['theme'] = event
		self._root.style.theme_use(event)

	# Create an options screen on the last tab
	def _options(self):
		optiontab = self._tabbed_list[-1]
		# set transparency
		Label(optiontab, text="Transparency", borderwidth=2, relief="groove", justify='right', anchor="w").grid(sticky='we', column=0, row=0)
		self._root.wm_attributes('-alpha', self._state['alpha'])
		Scale(optiontab, from_=.1, to=1, value=self._state['alpha'], orient=HORIZONTAL, command=self._updateAlpha).grid(sticky='we', column=1, row=0)
		self._root.alphavalue = Label(optiontab, text="1", borderwidth=2, relief="groove")
		self._root.alphavalue.grid(column=2, row=0)
		# set theme
		Label(optiontab, text="Theme", borderwidth=2, relief="groove", justify='right', anchor="w").grid(sticky='we', column=0, row=1)
		OptionMenu(optiontab, StringVar(optiontab), self._root.style.theme_use(), *self._themes, command=self._updateTheme).grid(sticky='we', column=1, row=1)
		# set transparency
		autoalpha = IntVar()
		autoalpha.set(self._state['trigger'])
		self._state['autoalpha'] = autoalpha
		Checkbutton(optiontab, text="Full Visibility on state change(10s)", variable=self._state['autoalpha']).grid(sticky='we', column=0, row=2, columnspan=2)


if __name__ == '__main__':
	main = App()
