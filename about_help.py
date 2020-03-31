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

def about_program(widget):
	about = gtk.AboutDialog()
	about.set_program_name('"The event log"')
	about.set_version("0.2")
	about.set_comments("Event log - log data display program")
	about.run()
	about.destroy()
	
def _help(widget):
	subprocess.Popen(['yelp', "/home/xubuntu/job_example/finished_work/help_books"])
