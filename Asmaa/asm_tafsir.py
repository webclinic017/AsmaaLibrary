# -*- coding: utf-8 -*-

#a############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  #########
#a############################################################################

from gi.repository import Gtk, Pango
import asm_customs, asm_popup, asm_path
from asm_contacts import Othman, listDB, bookDB

# class نافذة التفسير---------------------------------------------------------    

class Tafsir(Gtk.HBox):
    
    def show_tafsir(self, tafsir, sura, aya):
        if self.db != None:
            self.db.close_db()
            del self.db
        if tafsir == -1: book = asm_path.TAFSIR_DB
        else: book = self.listbook.file_book(tafsir)
        self.db = bookDB(book, tafsir)
        id_page = self.db.page_ayat(sura, aya)
        self.show_page(id_page)
    
    def mov_browse(self, id_page):
        self.suras.handler_block(self.change_sura)
        self.ayas.handler_block(self.change_aya)
        all_in_page = self.db.get_text_body(id_page)#rowid, id, text, part, page, hno, sora, aya, na
        if self.notebook.get_current_page() == 0: 
            if all_in_page[6] >= 1 and self.suras.get_active() != all_in_page[6]-1:
                self.suras.set_active(all_in_page[6]-1)
                ayat = asm_customs.value_active(self.suras, 2)
                adj = self.ayas.get_adjustment()
                if ayat == None: ayat = 100
                adj.set_upper(ayat)
                adj.set_value(1)
            self.ayas.set_value(all_in_page[7])
        self.suras.handler_unblock(self.change_sura)
        self.ayas.handler_unblock(self.change_aya)
        
    def show_page(self, id_page):
        all_in_page = self.db.get_text_body(id_page)#rowid, id, text, part, page, hno, sora, aya, na
        self.current_id = all_in_page[0]
        self.part_now = all_in_page[3]
        self.page_now = all_in_page[4]
        self.view_tafsir_bfr.set_text(all_in_page[2])
        try: sora, aya, na = all_in_page[6], all_in_page[7], all_in_page[8]
        except: sora = 0
        if sora > 0 and sora < 115:
            try: na = int(na)
            except: na = 1
            tafsir_quran = ' '.join(self.othman.get_ayat(sora,aya,aya+na))
            self.view_tafsir_bfr.insert(self.view_tafsir_bfr.get_start_iter(), u" \nـــــــــــــــــــ\n")
            self.view_tafsir_bfr.insert_with_tags(self.view_tafsir_bfr.get_start_iter(), 
                                                  tafsir_quran, self.view_quran_tag)
        # add to list browse
        if len(self.opened_old) == 0: 
            self.opened_old.append([id_page, self.tafsirs.get_active()])
        elif ([id_page, self.tafsirs.get_active()]) != self.opened_old[-1]: 
            self.opened_old.append([id_page, self.tafsirs.get_active()])
        # change n aya and n sura
        self.mov_browse(id_page)
        self.scroll_nasse.get_vadjustment().set_value(0.0)
        
    def ok_result(self, *a):
        model, i = self.sel_search.get_selected()
        if i:
            sura = model.get_value(i,0)
            aya = model.get_value(i,1)
            tafsir = asm_customs.value_active(self.tafsirs1, 0)
            self.show_tafsir(tafsir, sura, aya)
                
    def near_page(self, v):
        self.size_font += v
        self.view_tafsir.override_font(Pango.FontDescription("{}".format(self.size_font,))) 
    
    def select_tafsir(self, *a):
        self.nm_book = asm_customs.value_active(self.tafsirs, 1)
        tafsir = asm_customs.value_active(self.tafsirs, 0)
        sura = asm_customs.value_active(self.suras, 0)
        aya = self.ayas.get_value()
        self.show_tafsir(tafsir, sura, aya)
    
    def select_sura(self, w):
        sura = asm_customs.value_active(w, 0)
        ayat = asm_customs.value_active(w, 2)
        adj = self.ayas.get_adjustment()
        adj.set_upper(ayat)
        adj.set_value(1)
        tafsir = asm_customs.value_active(self.tafsirs, 0)
        self.show_tafsir(tafsir, sura, 1)
        
    def select_aya(self, w):
        sura = asm_customs.value_active(self.suras, 0)
        aya = w.get_value()
        tafsir = asm_customs.value_active(self.tafsirs, 0)
        self.show_tafsir(tafsir, sura, aya)
    
    def first_page(self, *a):
        self.show_page(self.db.first_page())
    
    def previous_page(self, *a):
        self.show_page(self.db.previous_page(self.current_id))
    
    def next_page(self, *a):
        self.show_page(self.db.next_page(self.current_id))
    
    def last_page(self, *a):
        self.show_page(self.db.last_page())
    
    def back_to_old(self, *a):
        if len(self.opened_old) == 1: return
        n = self.opened_old.pop()
        self.tafsirs.set_active(self.opened_old[-1][1])
        self.show_page(self.opened_old[-1][0])
        self.opened_new.append(n)
        
    def advance_to_new(self, *a):
        if len(self.opened_new) == 0: return
        n = self.opened_new.pop()
        self.tafsirs.set_active(n[1])
        self.show_page(n[0])
        if n != self.opened_old[-1]: self.opened_old.append(n)
    
    def search_cb(self, *a):
        text = self.search_entry.get_text().decode('utf8')
        if len(text) >= 3:
            all_ayat = Othman().search('"'+text+'"')
            self.store_search.clear()
            if len(all_ayat[0]) == 0:
                asm_customs.erro(self.parent, 'لا يوجد نتيجة'); return
            else: 
                for ayat in all_ayat[0]:
                    i_sura = ayat[0]
                    i_ayat = ayat[1]
                    suras_names = Othman().get_suras_names()
                    sura = suras_names[i_sura-1]
                    self.store_search.append(None, [i_sura, i_ayat, sura[1]])
                    
    def change_font(self, *a):
        self.view_quran_tag.set_property('foreground', self.parent.theme.color_qrn) 
        self.view_quran_tag.set_property("paragraph-background", self.parent.theme.color_bg_qrn)
        self.view_quran_tag.set_property('font', self.parent.theme.font_qrn)
    
    def show_bitaka(self, *a):
        if self.db.info_book() == None:
            text_info = self.nm_book
        else: text_info = self.db.info_book()
        return text_info
    
    def __init__(self, parent):
        self.db = None
        self.current_id = 1
        self.part_now = 1
        self.page_now = 1
        self.nm_book = u'التفسير الميسر'
        self.parent = parent
        self.othman = Othman()
        self.listbook = listDB()
        sura_list = self.othman.get_suras_names()
        self.opened_new = []
        self.opened_old = []
        Gtk.HBox.__init__(self, False, 0)
        vbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        
        store = []
        all_tafsir = self.listbook.all_tafsir()
        for a in all_tafsir: 
            store.append(a)
        store.insert(0, [-1, u'التفسير الميسر'])
        
        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        vb = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        vb.set_border_width(7)
        
        hb, self.tafsirs = asm_customs.combo(store, u'التفسير', 0)
        vb.pack_start(hb, False, False, 0)
        self.tafsirs.set_active(0)
        
        adj = Gtk.Adjustment(1, 1, 7, 1, 5.0, 0.0)
        self.ayas = Gtk.SpinButton()
        self.ayas.set_adjustment(adj)
        self.ayas.connect('activate', self.select_aya)
        
        hb, self.suras = asm_customs.combo(sura_list, u'السورة', 0)
        vb.pack_start(hb, False, False, 0)
        self.suras.set_active(0)
        
        hb = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        lab = Gtk.Label('الآيــــة')
        self.ayas.set_wrap(True)
        self.ayas.set_size_request(140, -1)
        hb.pack_start(lab, False, False, 0)
        hb.pack_end(self.ayas, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        
        show_search = Gtk.Button('أظهر البحث')
        def show_search_cb(w):
            self.notebook.set_current_page(1)
            self.ok_result()
        show_search.connect('clicked', show_search_cb)
        vb.pack_end(show_search, False, False, 0)
        self.notebook.append_page(vb, Gtk.Label('تصفح'))
        
        vb = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        vb.set_border_width(7)
        
        hb, self.tafsirs1 = asm_customs.combo(store, u'التفسير', 0)
        vb.pack_start(hb, False, False, 0)
        self.tafsirs1.set_active(0)
        
        try: self.search_entry = Gtk.SearchEntry()
        except: self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text('بحث في القرآن')
        self.search_entry.connect('activate', self.search_cb)
        hbox = Gtk.HBox(False, 2)
        hbox.pack_start(self.search_entry, True, True, 0)
        vb.pack_start(hbox, False, False, 0)
        
        self.store_search = Gtk.TreeStore(int, int, str)
        self.tree_search = asm_customs.TreeClass()
        self.tree_search.set_model(self.store_search)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('السورة', cell, text=2)
        self.tree_search.append_column(column)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('الآية', cell, text=1)
        self.tree_search.append_column(column)
        self.sel_search = self.tree_search.get_selection()
        self.tree_search.connect("cursor-changed", self.ok_result)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_search)
        
        show_browse = Gtk.Button('أظهر التصفح')
        def show_browse_cb(w):
            self.notebook.set_current_page(0)
            self.select_tafsir()
        show_browse.connect('clicked', show_browse_cb)
        vb.pack_end(show_browse, False, False, 0)
        
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vb.pack_start(scroll, True, True, 0)
        self.notebook.append_page(vb, Gtk.Label('بحث'))
        vbox.pack_start(self.notebook, True, True, 0)
        self.pack_start(vbox, False, False, 3)
        
        self.view_tafsir = asm_customs.ViewClass()
        self.view_tafsir_bfr = self.view_tafsir.get_buffer()
        self.view_tafsir.connect_after("populate-popup", asm_popup.populate_popup, self.parent)
        self.view_quran_tag = self.view_tafsir_bfr.create_tag("quran")
        self.change_font()
        self.scroll_nasse = Gtk.ScrolledWindow()
        self.scroll_nasse.set_shadow_type(Gtk.ShadowType.IN)
        self.scroll_nasse.add(self.view_tafsir)
        self.pack_start(self.scroll_nasse, True, True, 0)
        
        self.tafsirs.connect('changed', self.select_tafsir)
        self.tafsirs1.connect('changed', self.ok_result)
        self.change_sura = self.suras.connect('changed', self.select_sura)
        self.change_aya = self.ayas.connect('changed', self.select_aya)
        self.show_all()
        self.select_aya(self.ayas)




