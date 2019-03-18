# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
##############################################################################

from gi.repository import Gtk, GObject, Pango
import asm_customs, asm_araby, asm_path, asm_stemming
from asm_contacts import listDB, bookDB
from whoosh import index
from whoosh.fields import Schema, ID, TEXT
from whoosh.analysis import StandardAnalyzer, StemFilter
from whoosh.lang.porter import stem
from whoosh.qparser import QueryParser, OperatorsPlugin
from os.path import exists, join
import os, re
import indexer




normalize_tb = {
    65: 97, 66: 98, 67: 99, 68: 100, 69: 101, 70: 102,
    71: 103, 72: 104, 73: 105, 74: 106, 75: 107, 76: 108,
    77: 109, 78: 110, 79: 111, 80: 112, 81: 113, 82: 114,
    83: 115, 84: 116, 85: 117, 86: 118, 87: 119, 88: 120,
    89: 121, 90: 122, 1600: None, 1569: 1575, 1570: 1575, 1571: 1575,
    1572: 1575, 1573: 1575, 1574: 1575, 1577: 1607, # teh marboota ->    haa
    1611: None, 1612: None, 1613: None, 1614: None, 1615: None,
    1616: None, 1617: None, 1618: None, 1609: 1575}
rm_prefix = re.compile(u"^(?:ا?[وف]?((?:[بك]?ال|لل?)|[اينت])?)")

rm_suffix = re.compile(u"(?:ا[نت]|[يهة]|ها|ي[هنة]|ون)$")
def removeArabicSuffix(word):
    if len(word) > 4:
        w = rm_suffix.sub("", word, 1)
        if len(w) > 2:
            return w
    return word
def removeArabicPrefix(word):
    if len(word) > 3:
        w = rm_prefix.sub("", word, 1)
        if len(w)>2:
            return w
    return word
def stemArabic(word):
    return removeArabicPrefix(removeArabicSuffix(unicode(word).translate(normalize_tb)))





def stemfn(word): return asm_stemming.get_root(stem(word))[0][0]
analyzer = StandardAnalyzer(expression = ur"[\w\u064e\u064b\u064f\u064c\u0650\u064d\u0652\u0651\u0640]+\
(?:\.?[\w\u064e\u064b\u064f\u064c\u0650\u064d\u0652\u0651\u0640]+)*") | StemFilter(stemArabic)

schema = Schema(title=TEXT(stored=False, analyzer=analyzer), 
                content=TEXT(stored=False, analyzer=analyzer), 
                page=ID(stored=True))

if not exists(asm_path.INDEX_DIR_rw):
        os.mkdir(asm_path.INDEX_DIR_rw)

class WinIndexer(Gtk.Dialog):
    
    def __init__(self, parent):
        self.parent = parent
        self.db = listDB()
        self.selected_books = []
        self.build()

    def creat_writer_index(self, id_book):
        new_idx = join(asm_path.INDEX_DIR_rw, str(id_book).decode('utf8'))
        if not exists(new_idx):
            os.mkdir(new_idx)
        ix = index.create_in(new_idx, schema)
        return ix.writer()
    
    def start_indexation(self, *a):
        self.btn_index_start.set_sensitive(False)
        s = 0
        for id_book in self.selected_books:
            s += 1
            writer = self.creat_writer_index(id_book)
            print writer
            self.progress.set_fraction(float(s)/float(len(self.selected_books)))
            filebook = self.db.file_book(id_book)
            db = bookDB(filebook, id_book)
            for a in db.all_page():
                title = u"-".join(db.titles_page(a[0]))
                if title == "": title = u"-"
                content = db.get_text_body(a[0])[2]
                page = str(a[0]).decode('utf8')  
                #indexer.indexing(id_book, title, content, page)
                writer.add_document(title=title, content=content, page=page)
            writer.commit()
            self.db.add_indexed(id_book)
        asm_customs.info(self, u"تمت عملية الفهرسة")
        self.destroy()
    
    def load_books(self, *a):
        self.store_books.clear()
        groups = self.db.all_parts()
        for a in groups:
            while (Gtk.events_pending()): Gtk.main_iteration()
            aa = self.store_books.append(None, [None, a[1], a[0]])
            books = self.db.books_part(a[0])
            for b in books:
                if not self.db.is_indexed(b[0]):
                    self.store_books.append(aa, [None, b[1], b[0]])
    
    def add_to_listbooks(self, model, itr, fixed):
        id_book = model.get_value(itr, 2)
        i = model.iter_parent(itr)
        if i != None: 
            if fixed: 
                if id_book not in self.selected_books:
                    self.selected_books.append(id_book)
            else:
                if id_book in self.selected_books:
                    self.selected_books.remove(id_book)
    
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
                self.add_to_listbooks(model, iter1, fixed1)
                d += 1
        fixed = not fixed
        model.set(itr, 0, fixed)
        self.add_to_listbooks(model, itr, fixed)
    
    def select_o(self, model, path, i, bool1):
        bool0 = model.get_value(i,0)
        if bool0 != bool1: 
            model.set_value(i,0, bool1)
            self.add_to_listbooks(model, i, bool1)
            return False
    
    def select_all(self, *a):
        if self.all_books.get_active():
            try: self.store_books.foreach(self.select_o, True)
            except: pass
        else:
            try: self.store_books.foreach(self.select_o, False)
            except: pass
    
    # a دوال البحث في قائمة الكتب
    
    def search_in_index(self, model, path, i, my_books):
        txt = model.get(i,1)[0].decode('utf8')
        text, path0 = my_books[0], my_books[2]
        if asm_araby.fuzzy(text) in asm_araby.fuzzy(txt) and path.compare(path0) > 0: 
            self.tree_books.expand_to_path(path)
            self.tree_books.scroll_to_cell(path)
            self.sel_books.select_path(path)
            return True 
        else:
            return False
    
    def search_entry_cb(self, *a):
        text = self.entry_search.get_text().decode('utf8')
        model = self.store_books
        i = model.get_iter_first()
        path = model.get_path(i)
        try: self.store_books.foreach(self.search_in_index, [text, model, path, i])
        except: pass
    
    def search_cb(self, *a):
        model, i = self.sel_books.get_selected()
        if not i:
            i = model.get_iter_first()
        path = model.get_path(i)
        text = self.entry_search.get_text().decode('utf8')
        if text == u'': return
        try: self.store_books.foreach(self.search_in_index, [text, model, path, i])
        except: pass
    
    def build(self, *a):
        Gtk.Dialog.__init__(self, parent=self.parent)
        self.set_border_width(3)
        self.set_icon_name("asmaa")
        self.set_title("نافذة الفهرسة")
        self.set_size_request(620, 450)
        self.connect('delete-event', lambda *a: self.destroy())
        vbox = self.vbox

        hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        try: self.entry_search = Gtk.SearchEntry()
        except: self.entry_search = Gtk.Entry()
        self.entry_search.set_placeholder_text('بحث عن كتاب')
        self.entry_search.connect('changed', self.search_entry_cb)
        hbox.pack_end(self.entry_search, False, False, 0)
        search_btn = Gtk.ToolButton(stock_id=Gtk.STOCK_FIND)
        search_btn.connect('clicked', self.search_cb)
        search_btn.set_tooltip_text('ابحث عن النتيجة الموالية')
        hbox.pack_end(search_btn, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        
        self.store_books = Gtk.TreeStore(GObject.TYPE_BOOLEAN, GObject.TYPE_STRING, GObject.TYPE_INT)
        self.tree_books = Gtk.TreeView()
        self.tree_books.set_model(self.store_books)
        self.sel_books = self.tree_books.get_selection()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_books)
        scroll.set_size_request(200, -1)
        celltext = Gtk.CellRendererText()
        celltext.set_property("ellipsize", Pango.EllipsizeMode.END)
        celltoggle = Gtk.CellRendererToggle()
        celltoggle.set_property('activatable', True)
        columntoggle = Gtk.TreeViewColumn("اختر", celltoggle)
        columntext = Gtk.TreeViewColumn("الكتب", celltext, text = 1 )
        columntext.set_expand(True)
        columntoggle.add_attribute( celltoggle, "active", 0)
        celltoggle.connect('toggled', self.fixed_toggled, self.store_books)
        self.tree_books.append_column(columntoggle)
        self.tree_books.append_column(columntext)
        vbox.pack_start(scroll, True, True, 3)
        
        self.progress = Gtk.ProgressBar()
        vbox.pack_start(self.progress, False, False, 3)
        
        hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        self.all_books = Gtk.CheckButton('الكل')
        self.all_books.connect('toggled', self.select_all) 
        hbox.pack_start(self.all_books, False, False, 0)
        
        self.btn_index_start = asm_customs.ButtonClass('فهرسة')
        self.btn_index_start.connect('clicked', self.start_indexation)
        hbox.pack_start(self.btn_index_start, False, False, 0)
        btn_close = asm_customs.ButtonClass('إغلاق')
        #btn_close.set_sensitive(False)
        btn_close.connect('clicked', lambda *a: self.destroy())
        hbox.pack_end(btn_close, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.show_all()
        self.load_books()

# a-----------------------------------
class SearchIndexed():
    
    def search_in_book(self, id_book, text, dict_perf, dict_field, limit):
        if dict_field['nass']: 
            field = 'content'
        else: 
            field = 'title'
        new_index = join(asm_path.INDEX_DIR_rw, str(id_book).decode('utf8'))
        ix = index.open_dir(new_index)
        qp = QueryParser(field, schema=ix.schema)
        op = OperatorsPlugin(And = r"&", Or = r"\|", AndNot = r"&!", AndMaybe = r"&~", Not = r'!')
        qp.replace_plugin(op)
        q = qp.parse(text)
        with ix.searcher() as s:
            results = s.search(q, limit=limit)
            return results
    
    def __init__(self, *a):
        """search"""
