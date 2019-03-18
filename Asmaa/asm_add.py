# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
##############################################################################

import os, re
from shutil import copyfile
import asm_customs, asm_path
from gi.repository import Gtk, GObject, Pango
from os.path import join, exists, getsize
from asm_contacts import listDB
from asm_import_bok import DB_from_MDB
import asm_import_bok
import sqlite3

# class إضافة كتاب--------------------------------------------------------------

class AddBooks(Gtk.Dialog):
    
    def add_bok(self, *args):
        self.progress.set_fraction(0.0)
        self.progress.set_text('')
        add_dlg = Gtk.FileChooserDialog("اختر ملفات الشاملة",
                                      buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT))
        cl_button = add_dlg.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        def cll(widget,*a):
            for i in add_dlg.get_filenames():
                self.store_add.append([i.decode('utf8'), os.path.basename(i)])
        cl_button.connect('clicked',cll)
        ff = Gtk.FileFilter()
        ff.set_name('جميع الملفات المدعومة')
        ff.add_pattern('*.[Bb][Oo][Kk]')
        ff.add_pattern('*.[Aa][Ss][Mm]')
        add_dlg.add_filter(ff)
        ff = Gtk.FileFilter()
        ff.set_name('ملفات الشاملة (bok)')
        ff.add_pattern('*.[Bb][Oo][Kk]')
        add_dlg.add_filter(ff)
        ff = Gtk.FileFilter()
        ff.set_name('ملفات أسماء (asm)')
        ff.add_pattern('*.[Aa][Ss][Mm]')
        add_dlg.add_filter(ff)
        add_dlg.set_select_multiple(True)
        add_dlg.run()
        add_dlg.destroy()
        
    def add_doc(self, *args):
        self.progress.set_fraction(0.0)
        self.progress.set_text('')
        add_dlg = Gtk.FileChooserDialog("اختر ملفات الشاملة",
                                      buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT))
        cl_button = add_dlg.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        def cll(widget,*a):
            for i in add_dlg.get_filenames():
                self.store_add_doc.append([i, os.path.basename(i)])
        cl_button.connect('clicked',cll)
        ff = Gtk.FileFilter()
        ff.set_name('الملفات المدعومة')
        ff.add_pattern('*.[Dd][Oo][Cc][Xx]')
        ff.add_pattern('*.[Hh][Tt][Mm][Ll]')
        ff.add_pattern('*.[Tt][Xx][Tt]')
        ff.add_pattern('*.[Oo][Dd][Tt]')
        add_dlg.add_filter(ff)
        ff = Gtk.FileFilter()
        ff.set_name('جميع الملفات')
        ff.add_pattern('*')
        add_dlg.add_filter(ff)
        add_dlg.set_select_multiple(True)
        add_dlg.run()
        add_dlg.destroy()

    def start_convert(self, *a):
        if self.notebook.get_current_page() == 0:
            self.btn_convert.set_sensitive(False)
            self.btn_stop.set_sensitive(True)
            self.stop_n = 0
            self.import_book()
#        elif self.notebook.get_current_page() == 1:
#            self.btn_convert.set_sensitive(False)
#            self.btn_stop.set_sensitive(True)
#            self.stop_n = 0
#            self.import_docs()
        elif self.notebook.get_current_page() == 1:
            if len(self.store_books) == 0:
                asm_customs.erro(self.parent, 'يجب إظهار قائمة الكتب أولا!')
                return
            self.btn_convert.set_sensitive(False)
            self.btn_stop.set_sensitive(True)
            self.stop_n = 0
            self.import_shamela()
        self.parent.list_books.load_list()
    
    def get_text_from_file(self, myfile, name_file):
        return
    
    def import_docs(self, *a):
        con_ls = sqlite3.connect(asm_path.LISTBOOK_FILE_rw, isolation_level=None)
        cur_ls = con_ls.cursor() 
        if len(self.store_add_doc) == 0: return
        id_group = asm_customs.value_active(self.groups_doc)
        nm_group = asm_customs.value_active(self.groups_doc, 1)
        if id_group == None:
            asm_customs.info(self.parent, "اختر القسم المراد ضم الكتب إليه")
        else:
            self.progress.set_fraction(0.0)
            self.btn_clear.set_sensitive(False)
            self.btn_convert.set_sensitive(False)
            self.btn_remove.set_sensitive(False)
            self.btn_add.set_sensitive(False)
            if not self.is_book_radio.get_active():
                new_book = self.name_book_entry.get_text().decode('utf8')
            n_docs = len(self.store_add_doc)
            f = 0
            no_add = u''
            while len(self.store_add_doc) > 0:
                while (Gtk.events_pending()): Gtk.main_iteration()
                if self.is_book_radio.get_active():
                    new_book = re.sub(u'\..*', u'', self.store_add_doc[0][1])
                    text_book = self.get_text_from_file(self.store_add_doc[0][0], self.store_add_doc[0][1])
                elif self.is_part_radio.get_active():
                    return
                else:
                    return
    
    def import_shamela(self, *a):
        con_ls = sqlite3.connect(asm_path.LISTBOOK_FILE_rw, isolation_level=None)
        cur_ls = con_ls.cursor() 
        self.lab_status.set_text('يجري تحويل special.mdb')
        self.db_sp = DB_from_MDB(join(self.path_shamila, 'Files', 'special.mdb'),
                                  ['com', 'shorts', 'Shrooh'], join(asm_path.HOME_DIR, 'special.db'))
        cur_main = self.db_main.con.cursor()
        self.add_to_listbooks()
        n_books = len(self.selected_books)
        cur_sp = self.db_sp.con.cursor()
        no_add = ''
        v = 0
        for c in self.selected_books:
            while (Gtk.events_pending()): Gtk.main_iteration()
            v += 1
            a = str(c[2])[-1]
            b  = join(self.path_shamila, 'Books', a, str(c[2])+'.mdb')
            if getsize(b) > 50000000: continue
            if self.stop_n == 1: 
                asm_customs.erro(self.parent, 'تم إيقاف عملية التحويل')
                return
            if self.db_bok != None: 
                self.db_bok.destroy_db()
                del self.db_bok
            self.db_bok = DB_from_MDB(b, ['book', 'title'], ':memory:')
            self.lab_status.set_text('({} \ {})  يجري تحويل كتاب {} '.format(v, n_books, c[0]))
            try: asm_import_bok.export_mdb(self.path_shamila, con_ls, cur_ls, cur_main, cur_sp, self.db_bok.cur, c[2])
            except OSError: asm_customs.erro(self.parent, "حزمة mdbtools \nيرجى تثبيتها لأجل استيراد الكتب غير مثبتة"); raise
            except: no_add += '\n'+c[0]; print ('not add {}'.format(str(c[2])+'.mdb',))
            self.progress.set_fraction(float(v)/float(n_books))
        if no_add != u'': asm_customs.erro(self.parent, u'الكتب التي لم يتم إضافتها {}'.format(no_add,))
        self.lab_status.set_text('({} \ {})  لقد انتهت عملية التحويل '.format(v, n_books))
    
    def import_book(self, *a):
        con_ls = sqlite3.connect(asm_path.LISTBOOK_FILE_rw, isolation_level=None)
        cur_ls = con_ls.cursor() 
        if len(self.store_add) == 0: return
        id_group = asm_customs.value_active(self.groups)
        if id_group == None:
            asm_customs.info(self.parent, "اختر القسم المراد ضم الكتب إليه")
        else:
            nm_group = asm_customs.value_active(self.groups, 1).decode('utf8')
            self.progress.set_fraction(0.0)
            self.btn_clear.set_sensitive(False)
            self.btn_convert.set_sensitive(False)
            self.btn_remove.set_sensitive(False)
            self.btn_add.set_sensitive(False)
            n_books = len(self.store_add)
            f = 0
            no_add = u''
            while len(self.store_add) > 0:
                while (Gtk.events_pending()): Gtk.main_iteration()
                book = self.store_add[0][0]
                nm_file = self.store_add[0][1].decode('utf8')
                if nm_file[-4:] == u'.asm':
                    try: 
                        con = sqlite3.connect(book)
                        cur = con.cursor()
                        cur.execute("SELECT * FROM main")
                        info = cur.fetchone()
                        is_tafsir = info[8]
                        nm_book = info[0]
                        new_book = join(asm_path.BOOK_DIR_rw, nm_group, nm_file) 
                        copyfile(book, new_book)
                        self.db.add_book(nm_book, id_group, is_tafsir)
                    except: no_add += u'\n'+nm_file[:-4]; print ('not add {}'.format(book,))
                else:
                    nm_book = nm_file[:-4]
                    if self.db_bok != None: 
                        self.db_bok.destroy_db()
                        del self.db_bok
                    self.db_bok = DB_from_MDB(book, [], ':memory:')
                    self.progress.set_fraction(float(f)/float(n_books))
                    try: asm_import_bok.export_bok(book, nm_group, con_ls, cur_ls, self.db_bok.cur)
                    except OSError: asm_customs.erro(self.parent, "حزمة mdbtools \nيرجى تثبيتها لأجل استيراد الكتب غير مثبتة"); raise
                    except: no_add += u'\n'+nm_book; print ('not add {}'.format(book,))
                i = self.store_add.get_iter_first()
                self.store_add.remove(i)
                f +=1
            self.progress.set_text('انتهى !!')
            self.progress.set_fraction(1.0)
            self.btn_clear.set_sensitive(True)
            self.btn_convert.set_sensitive(True)
            self.btn_remove.set_sensitive(True)
            self.btn_add.set_sensitive(True)
            if no_add != u'': asm_customs.erro(self.parent, u'الكتب التي لم يتم إضافتها {}'.format(no_add,)) 
    
    def select_path(self, *a): 
        save_dlg = Gtk.FileChooserDialog(u'تحديد مجلد', self.parent,
                                    Gtk.FileChooserAction.SELECT_FOLDER,
                                    (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        res = save_dlg.run()
        if res == Gtk.ResponseType.OK:
            new_dir = save_dlg.get_filename().decode('utf8')
            self.entry_shamila.set_text(new_dir)
        save_dlg.destroy()
    
    def show_books(self, *a):
        self.path_shamila = self.entry_shamila.get_text().decode('utf8')
        if self.path_shamila == u'': 
            asm_customs.erro(self.parent, "لم تحدد موقع المكتبة الشاملة")
            return
        else:
            if not exists(join(self.path_shamila, u'Files')) or not exists(join(self.path_shamila, u'Books')):
                asm_customs.erro(self.parent, "موقع الشاملة المحدد غير صحيح")
                return
        self.db_main = DB_from_MDB(join(self.path_shamila, u'Files', u'main.mdb'), ['0bok', '0cat'],
                                    join(asm_path.HOME_DIR, u'main.db'))
        cur_main = self.db_main.con.cursor()
        groups = cur_main.execute('SELECT id, name FROM acat').fetchall()
        self.store_books.clear()
        for a in groups:
            aa = self.store_books.append(None, [True, a[1], a[0]])
            books = cur_main.execute('SELECT bkid, bk FROM abok WHERE cat=?', (a[0],)).fetchall()
            for b in books:
                self.store_books.append(aa, [True, b[1], b[0]])
        self.all_books.set_active(True)
    
    def remove_iter(self, *a):
        (model, i) = self.sel_add.get_selected()
        if i :
            model.remove(i)
    
    def stop_operation(self, *a):
        self.stop_n = 1
        self.btn_convert.set_sensitive(True)
        self.btn_stop.set_sensitive(False)
    
    def select_o(self, model, path, i, fixed):
        bool0 = model.get_value(i,0)
        if bool0 == fixed: 
            nm_book = model.get_value(i, 1)
            id_book = model.get_value(i, 2)
            i0 = model.iter_parent(i)
            if i0 != None: 
                nm_group = model.get_value(i0, 1)
                self.selected_books.append([nm_book, nm_group, id_book])
            return False
    
    def select_inselect(self, model, path, i, bool1):
        bool0 = model.get_value(i,0)
        if bool0 != bool1: 
            model.set_value(i,0, bool1)
            return False
    
    def select_all(self, *a):
        if self.all_books.get_active():
            try: self.store_books.foreach(self.select_inselect, True)
            except: pass
        else:
            try: self.store_books.foreach(self.select_inselect, False)
            except: pass
    
    def add_to_listbooks(self, *a):
        try: self.store_books.foreach(self.select_o, True)
        except: pass
    
    def fixed_toggled(self, cell, path, model):
        itr = model.get_iter((path),)
        fixed = model.get_value(itr, 0)
        if model.iter_has_child(itr):
            n_iters = self.store_books.iter_n_children(itr)
            d = 0
            while d in range(n_iters):
                iter1 = model.get_iter((int(path),d),)
                fixed1 = model.get_value(iter1, 0)
                fixed1 = not fixed
                model.set(iter1, 0, fixed1)
                d += 1
        fixed = not fixed
        model.set(itr, 0, fixed)

    def specified(self, *a):
        if self.is_book_radio.get_active():
            self.name_book_entry.set_sensitive(False)
            self.fasil.set_sensitive(True)
            self.letters.set_sensitive(True)
        elif self.is_part_radio.get_active():
            self.name_book_entry.set_sensitive(True)
            self.fasil.set_sensitive(True)
            self.letters.set_sensitive(True)
        else:
            self.name_book_entry.set_sensitive(True)
            self.fasil.set_sensitive(False)
            self.letters.set_sensitive(False)
            
    def __init__(self, parent):
        self.selected_books = []
        self.db_bok = None
        self.parent = parent
        self.stop_n = 0
        self.db = listDB()
        box = Gtk.Box(spacing=5,orientation=Gtk.Orientation.VERTICAL)
        Gtk.Dialog.__init__(self, parent=self.parent)
        self.resize(480, 500)
        area = self.get_content_area()
        area.set_spacing(5)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file(join(asm_path.ICON_DIR, 'Chamila-32.png'))
        self.set_modal(True)
        self.set_title('نافذة الاستيراد') 
        self.notebook = Gtk.Notebook()
        
        # a استيراد ملفات bok & asm----------------------------
        hb = Gtk.HBox(False, 3)
        self.btn_add = Gtk.Button("جديد")
        self.btn_add.connect('clicked', self.add_bok)
        hb.pack_start(self.btn_add, False, False, 0)
        hb.pack_start(Gtk.Label('«bok, asm»'), True, True, 0)
        self.btn_clear = Gtk.Button("مسح")
        self.btn_clear.connect('clicked', lambda *a: self.store_add.clear())
        hb.pack_end(self.btn_clear, False, False, 0)
        self.btn_remove = Gtk.Button("حذف")
        self.btn_remove.connect('clicked', self.remove_iter)
        hb.pack_end(self.btn_remove, False, False, 0)
        box.pack_start(hb, False, False, 0)
        self.store_add = Gtk.ListStore(str, str)
        self.tree_add = Gtk.TreeView()
        self.sel_add = self.tree_add.get_selection()
        column = Gtk.TreeViewColumn('الكتب',Gtk.CellRendererText(),text = 1)
        self.tree_add.append_column(column)
        self.tree_add.set_model(self.store_add)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_add)
        box.pack_start(scroll, True, True, 0)
        ls = []
        for a in self.db.all_parts():
            ls.append([a[0], a[1]])
        hbox, self.groups = asm_customs.combo(ls, 'ضع هذه الكتب في قسم :', 3)
        box.pack_start(hbox, False, False, 0)
        box.set_border_width(5)
        self.notebook.append_page(box, Gtk.Label('ملفات كتب'))
        
        # a استيراد الملفات النصية----------------------------
        box = Gtk.Box(spacing=5,orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(5)
        hb = Gtk.HBox(False, 3)
        self.btn_add_doc = Gtk.Button("جديد")
        self.btn_add_doc.connect('clicked', self.add_doc)
        hb.pack_start(self.btn_add_doc, False, False, 0)
        hb.pack_start(Gtk.Label('«odt, docx, txt, html»'), True, True, 0)
        self.btn_clear_doc = Gtk.Button("مسح")
        self.btn_clear_doc.connect('clicked', lambda *a: self.store_add.clear())
        hb.pack_end(self.btn_clear_doc, False, False, 0)
        self.btn_remove_doc = Gtk.Button("حذف")
        self.btn_remove_doc.connect('clicked', self.remove_iter)
        hb.pack_end(self.btn_remove_doc, False, False, 0)
        box.pack_start(hb, False, False, 0)
        self.store_add_doc = Gtk.ListStore(str, str)
        self.tree_add_doc = Gtk.TreeView()
        self.sel_add_doc = self.tree_add_doc.get_selection()
        column = Gtk.TreeViewColumn('الملفات',Gtk.CellRendererText(),text = 1)
        self.tree_add_doc.append_column(column)
        self.tree_add_doc.set_model(self.store_add_doc)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_add_doc)
        box.pack_start(scroll, True, True, 0)
        
        hbox = Gtk.Box(spacing=10,orientation=Gtk.Orientation.HORIZONTAL)
        self.is_book_radio = Gtk.RadioButton.new_with_label_from_widget(None, 'كتاب')
        self.is_part_radio = Gtk.RadioButton.new_with_label_from_widget(self.is_book_radio, 'جزء')
        self.is_page_radio = Gtk.RadioButton.new_with_label_from_widget(self.is_part_radio, 'صفحة')
        self.is_book_radio.connect('toggled',self.specified,'0')
        self.is_part_radio.connect('toggled',self.specified,'1')
        self.is_page_radio.connect('toggled',self.specified,'2')
        hbox.pack_start(Gtk.Label('كل ملف يمثل : '), False, False, 0)
        hbox.pack_start(self.is_book_radio, False, False, 0)
        hbox.pack_start(self.is_part_radio, False, False, 0)
        hbox.pack_start(self.is_page_radio, False, False, 0)
        hbox.set_border_width(5)
        box.pack_start(hbox, False, False, 0)
        
        hb = Gtk.HBox(False, 7)
        hb.pack_start(Gtk.Label('اسم الكتاب : '), False, False, 0)
        self.name_book_entry = Gtk.Entry()
        self.name_book_entry.set_sensitive(False)
        hb.pack_start(self.name_book_entry, True, True, 0)
        box.pack_start(hb, False, False, 0)
        
        hb = Gtk.HBox(False, 7)
        self.letters = Gtk.CheckButton('عدد الأحرف في الصفحة')
        hb.pack_start(self.letters, False, False, 0)
        adj = Gtk.Adjustment(3000, 10, 100000, 1, 5.0, 0.0)
        self.n_letters = Gtk.SpinButton()
        self.n_letters.set_adjustment(adj)
        self.n_letters.set_wrap(True)
        self.n_letters.set_sensitive(False)
        hb.pack_start(self.n_letters, False, False, 0)
        box.pack_start(hb, False, False, 0)
        def letters_cb(widget, *a):
            if self.letters.get_active():
                self.n_letters.set_sensitive(True)
            else:
                self.n_letters.set_sensitive(False)
        self.letters.connect('toggled', letters_cb)
        
        hb = Gtk.HBox(False, 7)
        self.fasil = Gtk.CheckButton('رمز فاصل بين الصفحات')
        hb.pack_start(self.fasil, False, False, 0)
        self.separative = Gtk.Entry()
        self.separative.set_sensitive(False)
        hb.pack_start(self.separative, False, False, 0)
        box.pack_start(hb, False, False, 0)
        def fasil_cb(widget, *a):
            if self.fasil.get_active():
                self.separative.set_sensitive(True)
            else:
                self.separative.set_sensitive(False)
        self.fasil.connect('toggled', fasil_cb)
        
        box.pack_start(Gtk.HSeparator(), False, False, 0)
        
        hbox, self.groups_doc = asm_customs.combo(ls, 'ضع هذه الكتب في قسم :', 3)
        box.pack_start(hbox, False, False, 0)
        #self.notebook.append_page(box, Gtk.Label('ملفات نصية'))
        
        # a استيراد الشاملة----------------------------
        box = Gtk.Box(spacing=3,orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(5)
        
        hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        self.entry_shamila = Gtk.Entry()
        b_shamila = Gtk.Button('...')
        b_shamila.connect('clicked', self.select_path)  
        hbox.pack_start(Gtk.Label('مجلد الشاملة'), False, False, 0)
        hbox.pack_start(self.entry_shamila, True, True, 0)
        hbox.pack_start(b_shamila, False, False, 0)
        box.pack_start(hbox, False, False, 0)
        
        hbox = Gtk.Box(spacing=6,orientation=Gtk.Orientation.HORIZONTAL)
        b_show = Gtk.Button('أظهر قائمة الكتب')
        b_show.connect('clicked', self.show_books)  
        hbox.pack_start(b_show, False, False, 0)
        box.pack_start(hbox, False, False, 0)
        
        self.store_books = Gtk.TreeStore(GObject.TYPE_BOOLEAN, GObject.TYPE_STRING, GObject.TYPE_INT)
        self.tree_books = Gtk.TreeView()
        self.tree_books.set_model(self.store_books)
        self.sel_books = self.tree_books.get_selection()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_books)
        scroll.set_size_request(200, -1)
        celltext = Gtk.CellRendererText()
        celltoggle = Gtk.CellRendererToggle()
        celltoggle.set_property('activatable', True)
        columntoggle = Gtk.TreeViewColumn("اختر", celltoggle)
        columntext = Gtk.TreeViewColumn("الكتب", celltext, text = 1 )
        columntoggle.add_attribute( celltoggle, "active", 0)
        celltoggle.connect('toggled', self.fixed_toggled, self.store_books)
        self.tree_books.append_column(columntoggle)
        self.tree_books.append_column(columntext)
        box.pack_start(scroll, True, True, 0)
        
        hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        self.all_books = Gtk.CheckButton('الكل')
        self.all_books.connect('toggled', self.select_all) 
        hbox.pack_start(self.all_books, False, False, 0)
        self.lab_status = Gtk.Label('')
        self.lab_status.set_ellipsize(Pango.EllipsizeMode.END)
        hbox.pack_end(self.lab_status, False, False, 0)
        box.pack_end(hbox, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label('قرص الشاملة'))
        
        hbox = Gtk.Box(spacing=3,orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_border_width(5)
        self.btn_close = asm_customs.ButtonClass("إغلاق")
        self.btn_close.connect('clicked', lambda *a: self.destroy())
        hbox.pack_end(self.btn_close, False, False, 0)
        self.btn_convert = Gtk.Button("تحويل")
        self.btn_convert.connect('clicked', self.start_convert)
        hbox.pack_start(self.btn_convert, False, False, 0)
        self.btn_stop = Gtk.Button("إيقاف")
        self.btn_convert.connect('clicked', self.stop_operation)
        self.btn_stop.set_sensitive(False)
        hbox.pack_start(self.btn_stop, False, False, 0)
        area.pack_start(self.notebook, True, True, 0)
        self.progress = Gtk.ProgressBar()
        area.pack_start(self.progress, False, False, 0)
        area.pack_start(hbox, False, False, 0)
        self.show_all()
        