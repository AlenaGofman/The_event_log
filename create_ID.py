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

def create_model_ID(file_id):
	'''create the model - a ListStore'''
	File = open(file_id, "rb")
	for leng in File.xreadlines():
		if leng == '----\n':
			if len(integ_simple.buf) > 0:
				for p in integ_simple.type_event:
					integ_simple.typesss.append(p)
		else:
			integ_simple.buf.append(leng)
			data_time = re.match("type=\w+.*msg=audit.(\d+\.\d+\.\d+) (\d+:\d+:\d+)", leng)
			if data_time:
				_data = data_time.group(1)
				_time = data_time.group(2)
			m = re.match("type=USER_AUTH.*msg=audit.(\d+\.\d+\.\d+) (\d+:\d+:\d+).*uid=([\w]+).*auid=([\w]+).*op=([\w+:]+).*acct=([\w]+).*exe=([^\s]+).*res=([\w]+)", leng)
			if m:
				uid = m.group(3)
				auid = m.group(4)
				event = m.group(5)
				acct = m.group(6)
				exe_any = m.group(7)
				res = m.group(8)
				if res=='failed':
					res='Запрещен'
				else:
					res='Разрешен'
				auid=uid
				any_type = (_data, _time, event, res, auid, exe_any)
				integ_simple.type_event.append(any_type)
			m = re.match("type=SYSCALL.*msg=audit.(\d+\.\d+\.\d+) (\d+:\d+:\d+).*success=([\w]+).*uid=([\w]+).*exe=([^\s]+)", leng)
			if m:
				success = m.group(3)
				uid = m.group(4)
				exe_syscall = m.group(5)
	store = gtk.ListStore(str, str, str, str, str, str)
	for x in integ_simple.type_event:
		store.append([x[0], x[1], x[2], x[3], x[4], x[5]])
	File.close()
	integ_simple.type_event = []
	os.remove(file_id)
	return store

def reportToID(treeView):
	''' create the columns '''
	rendererText = gtk.CellRendererText()
	column = gtk.TreeViewColumn("Дата", rendererText, text=0)
	column.set_sort_column_id(0)
	treeView.append_column(column)
	
	rendererText = gtk.CellRendererText()
	column = gtk.TreeViewColumn("Время", rendererText, text=1)
	column.set_sort_column_id(1)
	treeView.append_column(column)
	
	rendererText = gtk.CellRendererText()
	column = gtk.TreeViewColumn("Событие", rendererText, text=2)
	column.set_sort_column_id(2)
	treeView.append_column(column)
	
	rendererText = gtk.CellRendererText()
	column = gtk.TreeViewColumn("Доступ", rendererText, text=3)
	column.set_sort_column_id(3)
	treeView.append_column(column)
	
	rendererText = gtk.CellRendererText()
	column = gtk.TreeViewColumn("Пользователь", rendererText, text=4)
	column.set_sort_column_id(4)
	treeView.append_column(column)
	
	rendererText = gtk.CellRendererText()
	column = gtk.TreeViewColumn("Путь к документу", rendererText, text=5)
	column.set_sort_column_id(5)
	treeView.append_column(column)
