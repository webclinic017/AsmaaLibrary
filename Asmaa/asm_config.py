# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  #########
##############################################################################

import os.path
from os import mkdir
import ConfigParser

myfile = os.path.expanduser('~/.asmaa/asmaafile.cfg')
config = ConfigParser.RawConfigParser()
config.read(myfile)
section = 'settings'

def load():
    if not config.has_section(section):
        config.add_section(section)
    if not config.has_option(section, 'path'):
        config.set(section, 'path', os.path.expanduser('~/مكتبة أسماء/Listbooks.db'))
    if not config.has_option(section, 'idx_qrn'):
        config.set(section, 'idx_qrn', 1)
    if not config.has_option(section, 'saved_session'):
        config.set(section, 'saved_session', 0)
    if not config.has_option(section, 'start_session'):
        config.set(section, 'start_session', '[[],0,[]]')
    if not config.has_option(section, 'font_tit'):
        config.set(section, 'font_tit', 'KacstOne 15')
    if not config.has_option(section, 'font_bks'):
        config.set(section, 'font_bks', 'KacstOne 15')
    if not config.has_option(section, 'font_nass'):
        config.set(section, 'font_nass', 'Simplified Naskh 22')
    if not config.has_option(section, 'font_oth'):
        config.set(section, 'font_oth', 'Simplified Naskh 22')
    if not config.has_option(section, 'font_qrn'):
        config.set(section, 'font_qrn', 'Amiri Quran 23')
    if not config.has_option(section, 'font_idx'):
        config.set(section, 'font_idx', 'KacstOne 15')
    if not config.has_option(section, 'color_tit'):
        config.set(section, 'color_tit', '#868609091515')
    if not config.has_option(section, 'color_idx'):
        config.set(section, 'color_idx', '#868609091515')
    if not config.has_option(section, 'color_nass'):
        config.set(section, 'color_nass', '#202040400000')
    if not config.has_option(section, 'color_oth'):
        config.set(section, 'color_oth', '#202040400000')
    if not config.has_option(section, 'color_qrn'):
        config.set(section, 'color_qrn', '#202040400000')
    if not config.has_option(section, 'color_bks'):
        config.set(section, 'color_bks', '#868609091515')
    if not config.has_option(section, 'color_bg'):
        config.set(section, 'color_bg', '#fdfdfdfdd7d7')
    if not config.has_option(section, 'color_bgs'):
        config.set(section, 'color_bgs', '#fdfdfdfdd7d7')
    if not config.has_option(section, 'color_sel'):
        config.set(section, 'color_sel', '#ffffffffffff')
    if not config.has_option(section, 'color_bg_sel'):
        config.set(section, 'color_bg_sel', '#9e9ec1c17a7a')
    if not config.has_option(section, 'color_fnd'):
        config.set(section, 'color_fnd', '#fe71fab0870b')
    if not config.has_option(section, 'color_bg_qrn'):
        config.set(section, 'color_bg_qrn', '#fcb2eb47aeb5')
    if not config.has_option(section, 'tr'):
        config.set(section, 'tr','0') # tr = default|custom 4 color&font
    if not config.has_option(section, 'theme'):
        config.set(section, 'theme','0')
    if not config.has_option(section, 'tashkil'):
        config.set(section, 'tashkil', '1')
    if not config.has_option(section, 'help'):
        config.set(section, 'help', '1')
    if not config.has_option(section, 'marks'):
        config.set(section, 'marks', '[]')
    if not config.has_option(section, 'n_group'):
        config.set(section, 'n_group', 0)
    if not config.has_option(section, 'n_book'):
        config.set(section, 'n_book', 0)
    if not config.has_option(section, 'add'):
        config.set(section, 'add', 4)
    if not config.has_option(section, 'site'):
        config.set(section, 'site', 0)
    if not config.has_option(section, 'quran_pos'):
        config.set(section, 'quran_pos', 1)
    if not config.has_option(section, 'view_books'):
        config.set(section, 'view_books', 0)
    with open(myfile, 'wa') as configfile:
        config.write(configfile)

def setv(option, value):
    config.set(section, option, value)
    with open(myfile, 'wa') as configfile:
        config.write(configfile)
   
def getv(option):
    value = config.get(section, option)
    return value

def getn(option):
    value = config.getint(section, option)
    return value

def getf(option):
    value = config.getfloat(section, option)
    return value
  
mydir = os.path.dirname(myfile)
if not os.path.exists(mydir):
    try:  mkdir(mydir)
    except: raise
if not os.path.exists(myfile):
    try: 
        open(myfile,'w+')
    except: raise
load()
