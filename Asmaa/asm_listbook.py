# -*- coding: utf-8 -*-
from gi.repository import Gtk, Pango
from gi.repository import GdkPixbuf
from asm_contacts import listDB
from asm_viewer import OpenBook
from asm_tablabel import TabLabel
import asm_customs, asm_araby, asm_config, asm_path
import cPickle
from os.path import join
from os import remove


COL_NAME = 0
COL_PIXBUF = 1
COL_ID = 2


# class نافذة قائمة الكتب-----------------------------------------------------------------------

class ListBooks(Gtk.HBox):
    
    def __init__(self, parent):
        self.parent = parent
        self.db = listDB()
        try: self.last_books = cPickle.load(file((join(asm_path.DATA_DIR_rw, u'last-books.pkl'))))
        except: self.last_books = []
        self.build()
   
    def load_list(self, *a):
        self.store_list.clear()
        self.store.clear()
        groups = self.db.all_parts()
        for a in groups:
            self.store.append([a[1], self.particon, a[0]])
            grp = self.store_list.append(None, [a[0], a[1]])
            books = self.db.books_part(a[0])
            for b in books:
                self.store_list.append(grp, [b[0], b[1]])
        
    def select_row(self, tree, tree_sel): 
        model, i = tree_sel.get_selected()
        if i:
            p = model.get_path(i)
            if model.iter_has_child(i):
                if self.tree_list.row_expanded(p):
                    self.tree_list.collapse_row(p)
                else: self.tree_list.expand_row(p, False) 
            elif model.iter_parent(i) or tree == self.tree_last or tree == self.tree_favorite or \
            tree == self.tree_list_search:
                id_book = model.get_value(i, 0)
                nm_book = model.get_value(i, 1).decode('utf8')
                book = self.db.file_book(id_book)
                text_info = self.db.info_book(book)[3]
                if text_info == None:
                    text_info = nm_book
                self.view_info_bfr.set_text(text_info)
    
    def add_to_lasts(self, id_book):
        if len(self.last_books) == 20: self.last_books.pop(0)
        if id_book in self.last_books:
            self.last_books.remove(id_book)
        self.last_books.append(id_book)
        try: 
            output = open(join(asm_path.DATA_DIR_rw, u'last-books.pkl'), 'wb')
            cPickle.dump(self.last_books, output)
            output.close()
        except: pass
        self.load_last()
            
    def avtive_row(self, *a): 
        model, i = self.sel_list.get_selected()
        if i:
            if model.iter_parent(i):
                id_book = model.get_value(i, 0)
                nm_book = model.get_value(i, 1).decode('utf8')
                my_book = self.db.file_book(id_book)
                self.open_book(my_book, nm_book, id_book)
                self.add_to_lasts(id_book)
    
    def ok_search(self, *a):
        model, i = self.sel_list_search.get_selected()
        if i:
            id_book = model.get_value(i,0)
            nm_book = model.get_value(i,1).decode('utf8')
            my_book = self.db.file_book(id_book)
            self.open_book(my_book, nm_book, id_book)
            self.add_to_lasts(id_book)
        
    def open_book(self, my_book, nm_book, id_book):
        n = self.parent.viewerbook.get_n_pages()
        for s in range(n):
            ch = self.parent.viewerbook.get_nth_page(s)
            if self.parent.viewerbook.get_tab_label(ch).nm == nm_book:
                self.parent.viewerbook.set_current_page(s)
                self.parent.notebook.set_current_page(1)
                return
        sr = OpenBook(self.parent, my_book, id_book)
        self.parent.viewerbook.append_page(sr,TabLabel(sr, nm_book))
        self.parent.viewerbook.set_current_page(-1)
        self.parent.notebook.set_current_page(1)
        sr.set_index()
    
    # a دوال المفضلة-------------------------------------------------------------------
                
    def rm_fav_one(self, *a):
        model, i = self.sel_favorite.get_selected()
        if i:
            msg = asm_customs.sure(self.parent, "هل تريد مسح الكتاب المحدد من المفضلة")
            if msg == Gtk.ResponseType.YES:
                id_book = model.get_value(i,0)
                check = self.db.out_favorite(id_book)
                if check == None:
                    model.remove(i)
    
    def ok_fav(self, *a):
        model, i = self.sel_favorite.get_selected()
        if i:
            id_book = model.get_value(i,0)
            nm_book = model.get_value(i,1).decode('utf8')
            my_book = self.db.file_book(id_book)
            self.open_book(my_book, nm_book, id_book)
            self.add_to_lasts(id_book)
    
    def load_fav(self, *a):
        self.store_favorite.clear()
        ls = self.db.favorite_books()
        for a in ls:
            self.store_favorite.append([a[0], a[1]])
        
    # a دوال الكتب الأخيرة-------------------------------------------------------------------
                
    def rm_last_all(self, *a):
        msg = asm_customs.sure(self.parent, "هل تريد مسح قائمة الكتب المفتوحة أخيرا")
        if msg == Gtk.ResponseType.YES:
            remove(join(asm_path.DATA_DIR_rw, u'last-books.pkl'))
            self.last_books = []
            self.store_last.clear()
    
    def ok_last(self, *a):
        model, i = self.sel_last.get_selected()
        if i:
            id_book = model.get_value(i,0)
            nm_book = model.get_value(i,1).decode('utf8')
            my_book = self.db.file_book(id_book)
            self.open_book(my_book, nm_book, id_book)
            self.add_to_lasts(id_book)
    
    def load_last(self, *a):
        self.store_last.clear()
        for a in reversed(self.last_books):
            book = self.db.tit_book(a)
            if book:
                self.store_last.append([book[0], book[1]])
    
    # a دوال البحث في قائمة الكتب
    
    def search_in_index(self, model, path, i, my_list):
        txt = model.get(i,1)[0].decode('utf8')
        text, model0, path0, i0 = my_list
        if asm_araby.fuzzy(text) in asm_araby.fuzzy(txt) and path.compare(path0) > 0: 
            self.tree_list.expand_to_path(path)
            self.tree_list.scroll_to_cell(path)
            self.sel_list.select_path(path)
            self.select_row(self.tree_list, self.sel_list)
            return True 
        else:
            return False
    
    def search_entry_cb(self, *a):
        if self.nb.get_current_page() in [0, 1]:
            self.search_item_cb()
        elif self.nb.get_current_page() in [2, 3]:
            self.search_list_cb()
        
    def search_list_cb(self, *a):
        text = asm_araby.fuzzy(self.search_entry.get_text().decode('utf8'))
        if text == '':
            self.nb.set_current_page(2)
        else:
            books = self.db.search_books(text)
            self.store_list_search.clear()
            for a in books:
                self.store_list_search.append(None, [a[0], a[1]]) 
            self.nb.set_current_page(3)
    
    def search_item_cb(self, *a):
        text = asm_araby.fuzzy(self.search_entry.get_text().decode('utf8'))
        if text == '':
            self.nb.set_current_page(0)
        else:
            books = self.db.search_books(text)
            self.store_books.clear()
            for a in books:
                self.store_books.append([a[1], self.bookicon, a[0]]) 
            self.nb.set_current_page(1)        
    
    def item_part_active(self, widget):
        item = widget.get_selected_items() 
        if len(item) > 0:
            model = widget.get_model()
            id_part = model[item[0]][COL_ID]
            name_part = model[item[0]][COL_NAME].decode('utf8')
            if self.select_part == name_part:
                self.store_books.clear()
                books_part = self.db.books_part(id_part)
                self.nb.set_current_page(1)
                self.show_all()
                v = 0
                for bk in books_part:
                    v += 1
                    if v%200 == 199: 
                        while (Gtk.events_pending()): Gtk.main_iteration()
                    self.store_books.append([bk[1], self.bookicon, bk[0]]) 
            else: self.select_part = name_part
    
    def item_book_select(self, widget):
        item = widget.get_selected_items() 
        if len(item) > 0:
            model = widget.get_model()
            id_book = model[item[0]][COL_ID]
            nm_book = model[item[0]][COL_NAME].decode('utf8')
            my_book = self.db.file_book(id_book)
            text_info = self.db.info_book(my_book)[3]
            if text_info == None:
                text_info = nm_book
            self.view_info_bfr.set_text(text_info)
            if self.select_book == nm_book:
                self.open_book(my_book, nm_book, id_book)
                self.add_to_lasts(id_book)
            else: self.select_book = nm_book
    
    def change_view(self, *a):
        if self.nb.get_current_page() in [0, 1]:
            self.nb.set_current_page(2)
            self.change_view_btn.set_label('عرض الأيقونات')
            asm_config.setv('view_books', 1)
        elif self.nb.get_current_page() in [2, 3]:
            self.nb.set_current_page(0)
            self.change_view_btn.set_label('عرض القائمة')
            asm_config.setv('view_books', 0)
   
    def back_cb(self, *a):
        if self.nb.get_current_page() in [0, 1]:
            self.nb.set_current_page(0)
        elif self.nb.get_current_page() == 2:
            self.tree_list.collapse_all() 
            self.tree_list.collapse_all()
        elif self.nb.get_current_page() ==  3:      
            self.nb.set_current_page(2)
        
    def build(self, *a):
        self.select_part = u''
        self.select_book = u''
        Gtk.HBox.__init__(self, False, 3)
        self.set_border_width(3)
        vb2 = Gtk.VBox(False, 9)
        
        # a أيقونات الكتب--------------------------
        self.vbox_iconview = Gtk.VBox(False, 5)
        hbox = Gtk.HBox(False, 3)
        back = asm_customs.tool_button(join(asm_path.ICON_DIR, 'right.png'), 
                           'الرجوع إلى صفحة الأقسام\nأو\nضم قائمة الكتب', self.back_cb)
        hbox.pack_start(back, False, False, 0)
        try: self.search_entry = Gtk.SearchEntry()
        except: self.search_entry = Gtk.Entry()
        self.search_entry.set_size_request(200, -1)
        self.search_entry.set_placeholder_text('بحث عن كتاب')
        self.search_entry.connect('changed', self.search_entry_cb)
        hbox.pack_start(self.search_entry, False, False, 0)
        self.change_view_btn = Gtk.Button('عرض القائمة')
        self.change_view_btn.connect('clicked', self.change_view)
        hbox.pack_end(self.change_view_btn, False, False, 0)
        self.vbox_iconview.pack_start(hbox, False, False, 0)
        self.nb = Gtk.Notebook()
        self.nb.set_show_tabs(False)
        vbox = Gtk.VBox(False, 0) 
        self.particon = GdkPixbuf.Pixbuf.new_from_file_at_size(join(asm_path.ICON_DIR, 'Groups-128.png'), 128, 128)
        self.bookicon = GdkPixbuf.Pixbuf.new_from_file_at_size(join(asm_path.ICON_DIR, 'Book-128.png'), 96, 96)
        sw = Gtk.ScrolledWindow()
        vbox.pack_start(sw, True, True, 0)
        self.store = Gtk.ListStore(str, GdkPixbuf.Pixbuf, int)
        iconView = Gtk.IconView()
        iconView.set_model(self.store)
        iconView.override_font(Pango.FontDescription('KacstOne 20'))
        iconView.set_text_column(COL_NAME)
        iconView.set_pixbuf_column(COL_PIXBUF)
        iconView.connect("selection_changed", self.item_part_active)
        sw.add(iconView)
        iconView.grab_focus()
        self.nb.append_page(vbox, Gtk.Label('0'))
        
        vbox = Gtk.VBox(False, 0);  
        sw = Gtk.ScrolledWindow()
        vbox.pack_start(sw, True, True, 0)
        self.store_books = Gtk.ListStore(str, GdkPixbuf.Pixbuf, int)
        iconView_books = Gtk.IconView()
        iconView_books.set_model(self.store_books)
        iconView_books.override_font(Pango.FontDescription('KacstOne 16'))
        iconView_books.set_text_column(COL_NAME)
        iconView_books.set_pixbuf_column(COL_PIXBUF)
        iconView_books.connect("selection_changed", self.item_book_select)
        sw.add(iconView_books)
        iconView_books.grab_focus()
        self.nb.append_page(vbox, Gtk.Label('1'))
        self.vbox_iconview.pack_start(self.nb, True, True, 0)
        
        # a قائمة الكتب----------------------------
        self.scroll_browser = Gtk.ScrolledWindow()
        self.tree_list = asm_customs.TreeClass()
        self.sel_list = self.tree_list.get_selection()
        cell = Gtk.CellRendererText()
        kal = Gtk.TreeViewColumn('الكتب', cell, text=1)
        self.tree_list.connect("row-activated", self.avtive_row)
        self.tree_list.append_column(kal)
        self.store_list = Gtk.TreeStore(int, str)
        self.scroll_browser.add(self.tree_list)
        self.tree_list.set_model(self.store_list)
        self.load_list()
        self.nb.append_page(self.scroll_browser, Gtk.Label('2'))
        
        self.scroll_search = Gtk.ScrolledWindow()
        self.tree_list_search = asm_customs.TreeClass()
        self.sel_list_search = self.tree_list_search.get_selection()
        cell = Gtk.CellRendererText()
        kal = Gtk.TreeViewColumn('الكتب', cell, text=1)
        self.tree_list_search.connect("row-activated", self.ok_search)
        self.tree_list_search.append_column(kal)
        self.store_list_search = Gtk.TreeStore(int, str)
        self.scroll_search.add(self.tree_list_search)
        self.tree_list_search.set_model(self.store_list_search)
        self.nb.append_page(self.scroll_search, Gtk.Label('3'))
        
        # a بطاقة كتاب--------------------------------
        self.view_info = asm_customs.ViewBitaka()
        self.view_info_bfr = self.view_info.get_buffer()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.view_info)
        scroll.set_size_request(250, 200)
        vb2.pack_start(scroll, False, False, 0)
        
        # a ------------------------------------------
        self.ntbk = Gtk.Notebook()
        
        # a الكتب الأخيرة------------------------------
        vbox = Gtk.Box(spacing=6,orientation=Gtk.Orientation.VERTICAL)
        vbox.set_border_width(3)
        self.tree_last = asm_customs.TreeIndex()
        self.tree_last.set_size_request(250, -1)
        self.sel_last = self.tree_last.get_selection()
        cell = Gtk.CellRendererText()
        kal = Gtk.TreeViewColumn('الكتب الأخيرة', cell, text=1)
        self.tree_last.append_column(kal)
        self.store_last = Gtk.ListStore(int, str)
        self.load_last()
        self.tree_last.set_model(self.store_last)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_last)
        self.tree_last.connect("row-activated", self.ok_last)
        vbox.pack_start(scroll, True, True, 0)
        
        hbox = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        remove_all = asm_customs.ButtonClass("مسح القائمة")
        remove_all.connect('clicked', self.rm_last_all)
        hbox.pack_start(remove_all, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.ntbk.append_page(vbox, Gtk.Label('الكتب الأخيرة'))
        
        # a المفضلة-----------------------------------
        vbox = Gtk.Box(spacing=6,orientation=Gtk.Orientation.VERTICAL)
        vbox.set_border_width(3)
        self.tree_favorite = asm_customs.TreeIndex()
        self.tree_favorite.set_size_request(250, -1)
        self.sel_favorite = self.tree_favorite.get_selection()
        cell = Gtk.CellRendererText()
        kal = Gtk.TreeViewColumn('الكتب المفضلة', cell, text=1)
        self.tree_favorite.append_column(kal)
        self.store_favorite = Gtk.ListStore(int, str)
        self.load_fav()
        self.tree_favorite.set_model(self.store_favorite)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_favorite)
        self.tree_favorite.connect("row-activated", self.ok_fav)
        vbox.pack_start(scroll, True, True, 0)
        
        self.tree_list.connect("cursor-changed", self.select_row, self.sel_list)
        self.tree_list_search.connect("cursor-changed", self.select_row, self.sel_list_search)
        self.tree_last.connect("cursor-changed", self.select_row, self.sel_last)
        self.tree_favorite.connect("cursor-changed", self.select_row, self.sel_favorite)
        
        remove_one = asm_customs.ButtonClass("حذف من المفضلة")
        remove_one.connect('clicked', self.rm_fav_one)
        hbox = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(remove_one, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.ntbk.append_page(vbox, Gtk.Label('الكتب المفضلة'))
        
        vb2.pack_start(self.ntbk, True, True, 0)
        
        self.pack_start(self.vbox_iconview, True, True, 0)
        self.pack_start(vb2, False, False, 0)
        self.show_all()
        
        #-----------------------------------------
        if asm_config.getn('view_books') == 0:
            pass
        else:
            self.nb.set_current_page(2)
            self.change_view_btn.set_label('عرض الأيقونات')
