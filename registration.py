#!/usr/bin/env python
# coding=UTF-8

import pygtk
pygtk.require('2.0')
import gtk
import re
import os
import time
import datetime
import random
import subprocess
import sys
import gobject
import pango
import string

import integ_simple
import about_help
import create_ID

main_window = None
filename = None
page_setup = None
settings = None
file_changed = False
buffer = None
statusbar = None

calendar = gtk.Calendar()
year,month,day = calendar.get_date()
month=month+1
currentDate = datetime.date(year, month, day)
text = currentDate.strftime("%d.%m.%Y")
time_start = text
time_end = text

file_tmp = "Obschee"
user_id = []
file_id_change = []

ID=0
LAST_SAVE = '.'
LAST_SAVE2 = '.'

#Obschee
os.system("ausearch -i -ts "+time_start+" -te "+time_end+" -m USER_AUTH >" + file_tmp)
os.system("echo ---- >>" +file_tmp)

class AuditLog:
	interface = """
		<ui>
			<menubar name="MenuBar">
				<menu action="Report type">
					<menuitem action="User authentication"/>
					<separator/>
					<menuitem action="Save as HTML"/>
					<menuitem action="Save in a text format"/>
					<separator/>
					<menuitem action="Close"/>
				</menu>
				<menu action="Reference">
					<menuitem action="Help"/>
					<separator/>
					<menuitem action="About program"/>
				</menu>
			</menubar>
		</ui>
		"""
	
	def updateTable(self, t, file_id):
		if(self.treeView):
			self.sw.remove(self.treeView)
		if(t == 1):
			self.treeView = gtk.TreeView(create_ID.create_model_ID(file_id))
			self.sw.add(self.treeView)
			self.treeView.set_rules_hint(True)
			create_ID.reportToID(self.treeView)
			self.treeView.show()
			self.window.set_title("User authentication report")
	
	def changeTable(self, t):
		global ID
		ID = t
		self.update_entry(False)
		
	def __init__(self):
		self.sw = gtk.ScrolledWindow()
		self.sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.treeView = None
		
		'''Create a new window'''
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		uimanager = gtk.UIManager()
		accelgroup = uimanager.get_accel_group()
		self.window.add_accel_group(accelgroup)
		self.actiongroup = gtk.ActionGroup("uimanager")
		self.actiongroup.add_actions([
			("User authentication", None, "_User authentication", "<control>A", None, lambda x: self.changeTable(1)),
			("Save as HTML", gtk.STOCK_SAVE, "_Save as HTML", "<control>S", None, self.do_save_as),
			("Save in a text format", None, "_Save in a text format", None, None, self.do_save_as_text),
			("Close", gtk.STOCK_QUIT, "_Close",  None, "Quit the Application", lambda w: gtk.main_quit()),
			("Report type", None, "_Report type"), 
			("Help", None, "_Help", "F1", None, about_help._help),
			("About program", None, "_About program", None, None, about_help.about_program),
			("Reference", None, "_Reference")
		])
		uimanager.insert_action_group(self.actiongroup, 0)
		uimanager.add_ui_from_string(self.interface)
		menubar = uimanager.get_widget("/MenuBar")
		
		self.window.set_size_request(1000, 500)
		self.window.set_border_width(10)
		self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
		self.window.set_title("The event log")
		self.window.connect("destroy", self.destroy)
		
		main_vbox = gtk.VBox(False, 10)
		main_hbox = gtk.HBox(False, 10)
		self.window.add(main_hbox)
		main_hbox.pack_start(main_vbox, True, True, 0)
		
		self.calendar = gtk.Calendar()
		self.calendar2 = gtk.Calendar()
		self._connect_signals()
		self._connect_signals2()
		
		frame = gtk.Frame("Report time")
		vbox=gtk.VBox(False, 0)
		frame.add(vbox)
		hbox = gtk.HBox(False, 0)
		vbox.pack_start(hbox, False, False, 10)
		
		label = gtk.Label("with: ")
		label.set_alignment(0, 0.5)
		hbox.pack_start(label, False, False, 10)
		self.entry = gtk.Entry()
		self.entry.set_editable(True)
		hbox.pack_start(self.entry, False, False, 0)
		self.button = gtk.Button(label = '^')
		hbox.pack_start(self.button, False, False, 0)
		self.clicked_handle = self.button.connect('clicked', self.show_widget)
		
		currentDate = datetime.date(year, month, day)
		text = currentDate.strftime("%d.%m.%Y")
		teeext = currentDate.strftime("%Y, %m, %d")
		self.entry.set_text(text)
		
		label = gtk.Label("time: ")
		label.set_alignment(0, 0.5)
		hbox.pack_start(label, False, False, 10)
		self.entryTime1 = gtk.Entry()
		hbox.pack_start(self.entryTime1, False, False, 0)
		
		label = gtk.Label("to: ")
		label.set_alignment(0, 0.5)
		hbox.pack_start(label, False, False, 10)
		self.entry2 = gtk.Entry()
		self.entry2.set_editable(False)
		hbox.pack_start(self.entry2, False, False, 0)
		self.button2 = gtk.Button(label = '^')
		hbox.pack_start(self.button2, False, False, 0)
		self.clicked_handle = self.button2.connect('clicked', self.show_widget2)
		
		self.entry2.set_text(text)
		
		label = gtk.Label("time: ")
		label.set_alignment(0, 0.5)
		hbox.pack_start(label, False, False, 10)
		self.entryTime2 = gtk.Entry()
		hbox.pack_start(self.entryTime2, False, False, 10)
		
		frameUser = gtk.Frame("Users")
		vbox=gtk.VBox(False, 0)
		frameUser.add(vbox)
		hbox = gtk.HBox(False, 0)
		vbox.pack_start(hbox, False, False, 10)
		
		#User selection
		File = open(file_tmp, "rb")
		self.combobox = gtk.ComboBox()
		self.liststore = gtk.ListStore(str)
		cell = gtk.CellRendererText()
		self.combobox.pack_start(cell)
		self.combobox.add_attribute(cell, 'text', 0)
		self.combobox.set_wrap_width(5)
		for leng in File.xreadlines():
			integ_simple.buf.append(leng)
			m = re.match("type=([\w]+).*msg=audit.(\d+\.\d+\.\d+) (\d+:\d+:\d+).*pid=([\w]+).*uid=([\w]+).*auid=([\w]+).*exe=([^\s]+)", leng)
			if m:
				uid = m.group(5)
				syscall = [uid]
				for p in syscall:
					integ_simple.typesss.append(p)
		for st in ['All users']:
			self.liststore.append([st])
			for l in set(integ_simple.typesss):
				self.liststore.append([l])
		self.combobox.set_model(self.liststore)
		self.combobox.connect('changed', self.changed_cb)
		self.combobox.set_active(0)
		hbox.pack_start(self.combobox, False, False, 20)
		
		main_vbox.pack_start(menubar, False, True, 0)
		main_vbox.pack_start(frame, False, False, 0)
		main_vbox.pack_start(frameUser, False, False, 0)
		main_vbox.pack_start(self.sw, True, True, 0)
		
		self.window.show_all()
		
		#для календаря №1
		self.cwindow = gtk.Window (gtk.WINDOW_TOPLEVEL)
		self.cwindow.set_position (gtk.WIN_POS_MOUSE)
		self.cwindow.set_decorated (False)
		self.cwindow.set_modal (True)
		self.cwindow.add(self.calendar)
		
		#для календаря №2
		self.ccwindow = gtk.Window (gtk.WINDOW_TOPLEVEL)
		self.ccwindow.set_position (gtk.WIN_POS_MOUSE)
		self.ccwindow.set_decorated (False)
		self.ccwindow.set_modal (True)
		self.ccwindow.add(self.calendar2)
		
		menubar.show()
		
	def _connect_signals(self):
		self.day_selected_handle = self.calendar.connect ('day-selected', self.choice_date)
		self.day_selected_handle = self.calendar.connect ('day-selected', self.hide_widget)
		
	def _connect_signals2(self):
		self.day_selected_handle2 = self.calendar2.connect ('day-selected', self.choice_date)
		self.day_selected_handle2 = self.calendar2.connect ('day-selected', self.hide_widget2)
		
	def changed_cb(self, combobox):
		self.model = combobox.get_model()
		self.index = combobox.get_active()
		self.model_new = self.model[self.index][0]
		self.update_entry()
		return
	
	def choice_date(self, *args):
		year1, month1, day1 = self.calendar.get_date()
		month1 = month1 + 1
		currentDate = datetime.date(year1, month1, day1)
		self.text = currentDate.strftime("%d.%m.%Y")
		
		year2, month2, day2 = self.calendar2.get_date()
		month2 = month2 + 1
		currentDate2 = datetime.date(year2, month2, day2)
		self.text2 = currentDate2.strftime("%d.%m.%Y")
		
		if ((self.text > text)or(day1 > day)or(month1 > month)or(year1 > year)):
			day1 = day
			month1 = month
			year1 = year
			self.entry.set_text(text)
		else:
			self.entry.set_text(self.text)
			if ((self.text > self.text2)or(day1 > day2)or(month1 > month2)or(year1 > year2)):
				day1 = day2
				month1 = month2
				year1 = year2
				self.entry.set_text(self.text)
		
		if ((self.text2 > text)or(day2 > day)or(month2 > month)or(year2 > year)):
			day2 = day
			month2 = month
			year2 = year
			self.entry2.set_text(text)
		else:
			self.entry2.set_text(self.text2)
			if ((self.text2 < self.text)or(day2 < day1)or(month2 < month1)or(year2 < year1)):
				day2 = day1
				month2 = month1
				year2 = year1
				self.entry.set_text(self.text2)
		
		self.update_entry()
	
	def update_entry(self, user=True):
		if (ID == 0):
			return
		
		self.time_start = self.entry.get_text()
		self.time_end = self.entry2.get_text()
		self.timewith = self.entryTime1.get_text()
		self.timeto = self.entryTime2.get_text()
		
		if self.model_new == 'All users':
			user=False
			user_id = self.model_new
		else:
			self.user_name = self.model_new
			user_id = self.user_name
		
		cmd='ausearch -i'
		if (self.time_start != ""):
			cmd += ' -ts' + self.time_start
		if (self.time_end != ""):
			cmd += ' -te' + self.time_end
		if (self.timewith != ""):
			cmd += ' -ts' + self.timewith
		if (self.timeto != ""):
			cmd += ' -te' + self.timeto
		
		if (user == False):
			self.user_name = ''
			x = ''
			self.combobox.set_active(0)
		
		if ID == 1:
			if user_id == 'All users':
				file_id_change = "DataTm"
				os.system("ausearch -i -ts "+self.timewith+" "+self.time_start+" -te "+self.timeto+" "+self.time_end+" -m USER_AUTH >" + file_id_change)
			else:
				file_id_change = "DataTm"
				os.system("ausearch -i -ts "+self.timewith+" "+self.time_start+" -te "+self.timeto+" "+self.time_end+" -m USER_AUTH -ui "+user_id+" >" + file_id_change)
		self.delete_time()
		self.updateTable(ID, file_id_change)
		
	def hide_widget(self, *args):
		self.cwindow.hide_all()
	
	def hide_widget2(self, *args):
		self.ccwindow.hide_all()
	
	def show_widget(self, *args):
		self.cwindow.show_all()
	
	def show_widget2(self, *args):
		self.ccwindow.show_all()
		
	def set_text(self, text):
		buffer.set_text(text)
		global file_changed
		file_changed = False
		
	def save_file(self, save_filename, ID):
		period='period'
		if (self.time_start != ""):
			period += ' with: ' + self.time_start
		if (self.time_end != ""):
			period += ' to ' + self.time_end
		if (self.timewith != ""):
			period += ' with ' + self.timewith
		if (self.timeto != ""):
			period += ' to ' + self.timeto
		Model = self.treeView.get_model()
		row_count = len(Model)
		col_count = len(self.treeView.get_columns())
		File = open(save_filename, 'w')
		File.write('<HTML><HEAD>')
		if (ID == 1):
			File.write('<TITLE>User authentication report</TITLE>')
		File.write('</HEAD><BODY>')
		if (ID == 1):
			File.write('<h2>User authentication report ')
			File.write("period: with "+self.time_start+" "+self.timewith+" to "+self.time_end+" "+self.timeto+'</h2>')
		File.write('<TABLE border=1>')
		File.write('<meta http-equiv="content-type" content="text/html; charset=utf-8" />')
		
		i = 0
		while(i < col_count):
			File.write('<TH>')
			value = self.treeView.get_column(i).get_title()
			File.write(value)
			File.write('</TH>')
			i+=1
		
		i = 0
		while (i < row_count):
			tree_iter = Model.get_iter(i)
			j = 0
			File.write('<TR>')
			while(j < col_count):
				File.write('\t\t<TD>')
				value = Model.get_value(tree_iter, j)
				File.write('\t\t'+value+'\n')
				File.write('\t\t</TD>\n')
				j+=1
			File.write('</TR>')
			i+=1
				
		File.write('</TABLE></BODY></HTML>')
		File.close()
		
	def save_file_text(self, save_filename, ID):
		period='period'
		if (self.time_start != ""):
			period += ' with: ' + self.time_start
		if (self.time_end != ""):
			period += ' to ' + self.time_end
		if (self.timewith != ""):
			period += ' with ' + self.timewith
		if (self.timeto != ""):
			period += ' to ' + self.timeto
		
		Model = self.treeView.get_model()
		row_count = len(Model)
		col_count = len(self.treeView.get_columns())
		File = open(save_filename, 'w')
		if (ID == 1):
			File.write('User authentication report ')
			File.write("period: with "+self.time_start+" "+self.timewith+" to "+self.time_end+" "+self.timeto+"\n\n")
		i = 0
		while(i < col_count):
			value = self.treeView.get_column(i).get_title()
			File.write(value + ' ')
			i+=1
		i = 0
		while (i < row_count):
			tree_iter = Model.get_iter(i)
			File.write('\n')
			j = 0
			while(j < col_count):
				value = Model.get_value(tree_iter, j)
				File.write(value + ' ')
				j+=1
			i+=1
		File.close()
	
	def do_save_as(self, save_filename):
		global LAST_SAVE
		dialog = gtk.FileChooserDialog("Save as HTML..", main_window, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		path_name = LAST_SAVE
		dialog.set_current_folder(path_name)
		name = '.html'
		dialog.set_current_name(name)
		dialog.set_default_response(gtk.RESPONSE_OK)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			save_filename = dialog.get_filename()
			(LAST_SAVE, name) = os.path.split(save_filename)
			self.save_file(save_filename, ID)
			print save_filename, 'Saved.'
		elif response == gtk.RESPONSE_CANCEL:
			print 'Closed, file is not saved.'
		dialog.destroy()
	
	def do_save_as_text(self, save_filename):
		global LAST_SAVE2
		dialog = gtk.FileChooserDialog("Save as TEXT..", main_window, gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		path_name = LAST_SAVE2
		dialog.set_current_folder(path_name)
		name2 = '.txt'
		dialog.set_current_name(name2)
		dialog.set_default_response(gtk.RESPONSE_OK)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			save_filename = dialog.get_filename()
			(LAST_SAVE2, name) = os.path.split(save_filename)
			self.save_file_text(save_filename, ID)
			print dialog.get_filename(), 'Saved.'
		elif response == gtk.RESPONSE_CANCEL:
			print 'Closed, file is not saved.'
		dialog.destroy()
	
	def on_erro(self, widget):
		md = gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, "Date not selected correctly")
		md.run()
		md.destroy()
	
	def delete_time(self):
		self.entryTime1.set_text("")
		self.entryTime2.set_text("")
	
	def destroy(self, widget, data=None):
		gtk.main_quit()
		return False
	
def main():
	gtk.main()
	file_id_change = []
	os.remove(file_tmp)

if __name__ == "__main__":
	lvexample = AuditLog()
	lvexample = main()
