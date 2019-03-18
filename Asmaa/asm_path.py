# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
##############################################################################

from os.path import join, dirname, realpath, exists, expanduser, getsize
from gi.repository import Gtk
import asm_config, asm_customs
from shutil import copyfile
from os import mkdir
import sqlite3

#a------------------------------------------
def sure_start():
    dlg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING,
                             Gtk.ButtonsType.YES_NO)
    dlg.set_markup('''
    لم يتمكن البرنامج من الاتصال بقاعدة البيانات،
    إذا كنت قد نزلتها بالفعل فربما لم تربطها بالبرنامج، 
    أو قد يكون القرص الموجود عليه القاعدة غير مضموم،
    هل تريد تحديد مسار قاعدة البيانات ؟''')
    db_void = Gtk.LinkButton.new_with_label("http://sourceforge.net/projects/asmaa/files/AsmaaLibrary.tar.gz/download",
                                                'تنزيل قاعدة بيانات للتجربة')
    new_lib = Gtk.Button('إنشاء مكتبة مفرغة')
    dlg.add_action_widget(new_lib, 3)
    def_lib = Gtk.Button('المسار الافتراضي')
    dlg.add_action_widget(def_lib, 4)
    area = dlg.get_content_area()
    area.set_spacing(7)
    hbox = Gtk.HBox(False, 7)
    hbox.pack_end(db_void, False, False, 0)
    area.pack_start(hbox, False, False, 0)
    area.show_all()
    r = dlg.run()
    dlg.destroy()
    return r

PATH0 = dirname(dirname(realpath(__file__))).decode('utf8')
PATH1 = join(u'/', u'usr', u'share', u'asmaa')
PATH2 = join(u'/', u'usr', u'local', u'share', u'asmaa')

#a------------------------------------------------------
if exists(join(PATH0, u'asmaa-data', u'icons', u'tab.png')):
    PATH = PATH0
    
elif exists(join(PATH1, u'asmaa-data', u'icons', u'tab.png')):
    PATH = PATH1
    
elif exists(join(PATH2, u'asmaa-data', u'icons', u'tab.png')):
    PATH = PATH2
    
#a---------------------------------------------------------
if exists(join(PATH1, u'asmaa-library', u'data', u'Listbooks.db')):
    LIBRARY_DIR_r   = join(PATH1, u'asmaa-library')
    BOOK_DIR_r      = join(LIBRARY_DIR_r, u'books')
    DATA_DIR_r      = join(LIBRARY_DIR_r, u'data')
    INDEX_DIR_r     = join(LIBRARY_DIR_r, u'index')
    LISTBOOK_FILE_r = join(LIBRARY_DIR_r, u'data', u'Listbooks.db')
    
elif exists(join(PATH2, u'asmaa-library', u'data', u'Listbooks.db')):
    LIBRARY_DIR_r   = join(PATH2, u'asmaa-library')
    BOOK_DIR_r      = join(LIBRARY_DIR_r, u'books')
    DATA_DIR_r      = join(LIBRARY_DIR_r, u'data')
    INDEX_DIR_r     = join(LIBRARY_DIR_r, u'index')
    LISTBOOK_FILE_r = join(LIBRARY_DIR_r, u'data', u'Listbooks.db')
    
else:
    LIBRARY_DIR_r   = u''
    BOOK_DIR_r      = u''
    DATA_DIR_r      = u''
    INDEX_DIR_r     = u''
    LISTBOOK_FILE_r = u''

#a-------------------------------------------------------
APP_DIR       =   PATH0
HOME_DIR      =   expanduser(u'~/.asmaa')
ASMAA_DIR     =   join(PATH, u'asmaa-data')
ICON_DIR      =   join(ASMAA_DIR, u'icons')
DB_DIR        =   join(ASMAA_DIR, u'db')
QURAN_DB      =   join(DB_DIR, u'Quran.db')
TAFSIR_DB     =   join(DB_DIR, u'Tafsir.db')
AUTHOR_DB     =   join(DB_DIR, u'Author.db')
DALIL_DB      =   join(DB_DIR, u'Dalil.db')
MOEJAM_DB     =   join(DB_DIR, u'Moejam.db')
TARAJIM_DB    =   join(DB_DIR, u'Tarajim.db')
MOSHAF_DIR    =   join(ASMAA_DIR, u'moshaf')

#a-------------------------------------------------------
LIBRARY_DIR_rw = join(HOME_DIR, u'asmaa-library')
LISTBOOK_FILE_rw =   join(LIBRARY_DIR_rw, u'data', u'Listbooks.db')  

#a-------------------------------------------------------
if not exists(LIBRARY_DIR_rw):
    mkdir(LIBRARY_DIR_rw)
if not exists(join(LIBRARY_DIR_rw, u'data')):
    mkdir(join(LIBRARY_DIR_rw, u'data'))
if not exists(join(LIBRARY_DIR_rw, u'books')):
    mkdir(join(LIBRARY_DIR_rw, u'books'))
if not exists(join(LIBRARY_DIR_rw, u'index')):
    mkdir(join(LIBRARY_DIR_rw, u'index'))

#a-------------------------------------------------------    
if exists(LISTBOOK_FILE_r):
    if not exists(LISTBOOK_FILE_rw) or getsize(LISTBOOK_FILE_rw) < getsize(LISTBOOK_FILE_r):
        copyfile(LISTBOOK_FILE_r, LISTBOOK_FILE_rw)
        con = sqlite3.connect(join(LIBRARY_DIR_rw, u'data', u'Listbooks.db'))
        cur = con.cursor()
        cur.execute('UPDATE books SET cat=-1')
        con.commit()
else:
    con = sqlite3.connect(join(LIBRARY_DIR_rw, u'data', u'Listbooks.db'))
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS groups (id_group integer primary key, \
    tit varchar(255), sub INTEGER, cat INTEGER)') 
    cur.execute('CREATE TABLE IF NOT EXISTS books (id_book integer primary key, tit varchar(255), \
    parent INTEGER, fav  INTEGER DEFAULT 0, last  INTEGER DEFAULT 1, cat  INTEGER DEFAULT 0,\
    tafsir  INTEGER DEFAULT 0, indx INTEGER DEFAULT 0)')

# a ---------------------------------------------------------------------------------------

if asm_config.getv('path').decode('utf8') != join(LIBRARY_DIR_rw, u'data', u'Listbooks.db'): 
    if not exists(asm_config.getv('path')): 
        res = sure_start()
        # a تحديد المسار--------------------------
        if res == Gtk.ResponseType.YES:
            open_dlg = Gtk.FileChooserDialog(u'تحديد مسار قاعدة البيانات',
                                             None, Gtk.FileChooserAction.OPEN,
                                            (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
            
            Filter = Gtk.FileFilter()
            Filter.set_name(u"قاعدة البيانات")
            Filter.add_pattern("Listbooks.db")
            open_dlg.add_filter(Filter)
            res = open_dlg.run()
            if res == Gtk.ResponseType.OK:
                asm_config.setv('path', open_dlg.get_filenames()[0])          
                open_dlg.destroy()
                library_path  = asm_config.getv('path')
                LIBRARY_DIR_rw = dirname(dirname(library_path)).decode('utf8')
            else:
                open_dlg.destroy()
                quit()   
            
        # a إلغاء التحديد-------------------------
        elif res == Gtk.ResponseType.NO:
            my_return = 0
            quit()
            
        # a مكتبة مفرغة--------------------------
        elif res == 3:
            save_dlg = Gtk.FileChooserDialog(u'مسار قاعدة البيانات الجديدة', None,
                                        Gtk.FileChooserAction.SELECT_FOLDER,
                                        (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
            res = save_dlg.run()
            if res == Gtk.ResponseType.OK:
                new_dir = join(save_dlg.get_filename().decode('utf8'), u'مكتبة أسماء')
                if exists(join(new_dir, u'data', u'Listbooks.db')):
                    asm_customs.erro(None, u'يوجد مكتبة في هذا الدليل بالفعل')
                else:
                    if not exists(new_dir):
                        mkdir(new_dir)
                    if not exists(join(new_dir, u'data')):
                        mkdir(join(new_dir, u'data'))
                    if not exists(join(new_dir, u'books')):
                        mkdir(join(new_dir, u'books'))
                    if not exists(join(new_dir, u'index')):
                        mkdir(join(new_dir, u'index'))
                    con = sqlite3.connect(join(new_dir, u'data', u'Listbooks.db'))
                    cur = con.cursor()
                    cur.execute('CREATE TABLE groups (id_group integer primary key, \
                    tit varchar(255), sub INTEGER, cat INTEGER)') 
                    cur.execute('CREATE TABLE books (id_book integer primary key, tit varchar(255), \
                    parent INTEGER, fav  INTEGER DEFAULT 0, last  INTEGER DEFAULT 1, cat  INTEGER DEFAULT 0,\
                    tafsir  INTEGER DEFAULT 0, indx INTEGER DEFAULT 0)')
                    asm_config.setv('path', join(new_dir, u'data', u'Listbooks.db'))
                    library_path  = asm_config.getv('path')
                    LIBRARY_DIR_rw = dirname(dirname(library_path)).decode('utf8')
                    asm_customs.info(None, u'تم إضافة مكتبة مفرغة جديدة')
            else:
                y_return = 0
                quit()
            save_dlg.destroy()
            
        # a المسار الافتراضي--------------------------
        elif res == 4:
            asm_config.setv('path', LISTBOOK_FILE_rw)
            
        # a إلغاء التحديد----------------------------    
        else:
            my_return = 0
            quit()
    else:
        library_path = asm_config.getv('path')
        LIBRARY_DIR_rw = dirname(dirname(library_path)).decode('utf8')
    
BOOK_DIR_rw      =   join(LIBRARY_DIR_rw, u'books')
DATA_DIR_rw      =   join(LIBRARY_DIR_rw, u'data')
INDEX_DIR_rw     =   join(LIBRARY_DIR_rw, u'index') 
LISTBOOK_FILE_rw =   join(LIBRARY_DIR_rw, u'data', u'Listbooks.db')  
    
# a إصلاحات------------------------------------------
    
if not exists(join(LIBRARY_DIR_rw, u'books')):
    mkdir(join(LIBRARY_DIR_rw, u'books'))
    
if not exists(join(LIBRARY_DIR_rw, u'index')):
    mkdir(join(LIBRARY_DIR_rw, u'index'))

if not exists(join(LIBRARY_DIR_rw, u'fields-search')):
    mkdir(join(LIBRARY_DIR_rw, u'fields-search'))
    
if not exists(join(LIBRARY_DIR_rw, u'waraka-search')):
    mkdir(join(LIBRARY_DIR_rw, u'waraka-search'))
    