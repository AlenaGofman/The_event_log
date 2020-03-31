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

#user selection
buf = []
syscall = []
any_type = []
user = []
typesss = []

#user authentication
buf_type = []
type_event = []
_data = []
_time = []
event = {}
any_type2 = []
exe_any = {}
uid = {}
acct = {}
success = {}
res = {}
exe_syscall = {}

#----
path_type = {}
_type = []
