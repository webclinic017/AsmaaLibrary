# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
##############################################################################

from gi.repository import Gtk, Gdk
from asm_contacts import bookDB, Othman, listDB
import asm_customs, asm_araby
from os.path import join, basename
import asm_popup

# class صفحة الكتب المفتوحة-----------------------------------------------------------------------

class ViewerBooks(Gtk.Notebook):
    
    # a التصفح--------------------------------------------

    def first_page(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        ch.first_page()
    
    def previous_page(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        ch.previous_page()
    
    def next_page(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        ch.next_page()
    
    def last_page(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        ch.last_page()
        
    def back_to_old(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n) 
        ch.back_to_old()
        
    def advance_to_new(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        ch.advance_to_new()
        
    def show_bitaka(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        return ch.show_bitaka()
    
    def hide_index(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        if ch.hp.get_position() <= 1:
            ch.hp.set_position(200)
        else: ch.hp.set_position(1)
    
    def __init__(self, parent):
        self.session = [[], None]
        Gtk.Notebook.__init__(self)
        self.set_scrollable(True)
        self.parent = parent
        def add(widget, n, d):
            try: self.session[0].append(n.id_book)
            except: pass
        self.connect("page-added", add)
        def rmv(widget, n, d):
            try: self.session[0].remove(n.id_book)
            except: pass
            if self.get_n_pages() == 0:
                self.parent.back_to_previous_page()
        self.connect("page-removed", rmv)
        def sth(widget, n, d):
            self.session[-1] = d
        self.connect("switch-page", sth)
        self.show_all()    

# class  الكتاب المفتوح-----------------------------------------------------------------------

class OpenBook(Gtk.VBox):
    
    def __init__(self, parent, book, id_book):
        Gtk.VBox.__init__(self, False, 3)
        self.db_list = listDB()
        self.parent = parent
        self.othman = Othman()
        self.id_book = id_book
        self.book = book
        self.nm_book = basename(book)[:-4]
        self.db = bookDB(book, id_book)
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.current_id = 1
        self.opened_new = []
        self.opened_old = []
        self.build()
    
    def show_bitaka(self, *a):
        if self.db.info_book() == None:
            text_info = self.nm_book
        else: text_info = self.db.info_book()
        return text_info
    
    def change_font(self, *a):
        self.view_title_tag.set_property('foreground', self.parent.theme.color_tit)
        self.view_title_tag.set_property('font', self.parent.theme.font_tit)
        self.view_quran_tag.set_property('foreground', self.parent.theme.color_qrn)
        self.view_quran_tag.set_property("paragraph-background", self.parent.theme.color_bg_qrn)
        self.view_quran_tag.set_property('font', self.parent.theme.font_qrn)
        self.view_search_tag.set_property('background', self.parent.theme.color_fnd)
        self.view_terms_tag.set_property('foreground', self.parent.theme.color_tit)
    
    def search_in_book(self, *a):
        text = self.entry_search.get_text().decode('utf8')
        self.store_search.clear()
        self.scroll_index.hide()
        self.scroll_search.show_all()
        phrase = '''fuzzy(nass) LIKE ? ESCAPE "|"'''
        text = asm_araby.fuzzy(text)
        self.search_tokens = asm_araby.tokenize_search(text)
        phrase2 = map(lambda phrase: '%'+phrase.replace('|','||').replace('%','|%')+'%', self.search_tokens)
        if len(phrase2) < 1: return []
        condition = ' AND '.join([phrase]*len(phrase2))
        self.db.search(text, self.store_search, condition, phrase2)
        if len(self.store_search) == 0:
            self.hide_search()
            asm_customs.erro(self.parent, 'لا يوجد نتائج')
            return
        self.hp.set_position(200)
        
    def hide_search(self, *a):
        self.scroll_index.show_all()
        self.scroll_search.hide()
        if len(self.list_index) > 1:
            self.hp.set_position(200)
        else:
            self.hp.set_position(1)
        self.entry_index.set_text('')
        
    def search_in_page(self, *a):
        self.show_page(self.all_in_page[1])
        text = self.entry_search.get_text().decode('utf8')
        search_tokens = []
        nasse = self.view_nasse_bfr.get_text(self.view_nasse_bfr.get_start_iter(), 
                                            self.view_nasse_bfr.get_end_iter(),True).split()
        if text == u'': 
            return
        else:
            txt = asm_araby.fuzzy(text)
            for term in nasse: 
                if txt in asm_araby.fuzzy(term.decode('utf8')):
                    search_tokens.append(term)
        asm_customs.with_tag(self.view_nasse_bfr, self.view_search_tag, search_tokens, 1)
    
    # a التصفح--------------------------------------------

    def index_highlight(self, model, path, i, page_id):
        pid = model.get(i,0)[0]
        if pid == page_id: 
            self.tree_index.expand_to_path(path)
            self.tree_index.scroll_to_cell(path)
            self.sel_index.select_path(path)
            return True 
        else:
            return False

    def first_page(self, *a):
        self.show_page(self.db.first_page())
        id_page = self.all_in_page[1]
        try: self.store_index.foreach(self.index_highlight, id_page)
        except: pass
    
    def previous_page(self, *a):
        self.show_page(self.db.previous_page(self.current_id))
        id_page = self.all_in_page[1]
        try: self.store_index.foreach(self.index_highlight, id_page)
        except: pass
    
    def next_page(self, *a):
        self.show_page(self.db.next_page(self.current_id))
        id_page = self.all_in_page[1]
        try: self.store_index.foreach(self.index_highlight, id_page)
        except: pass
    
    def last_page(self, *a):
        self.show_page(self.db.last_page())
        id_page = self.all_in_page[1]
        try: self.store_index.foreach(self.index_highlight, id_page)
        except: pass
    
    def back_to_old(self, *a):
        if len(self.opened_old) == 1: return
        n = self.opened_old.pop()
        self.show_page(self.opened_old[-1])
        self.opened_new.append(n)
        
    def advance_to_new(self, *a):
        if len(self.opened_new) == 0: return
        n = self.opened_new.pop()
        self.show_page(n)
        if n != self.opened_old[-1]: self.opened_old.append(n)
    
    def set_index(self, *a):
        self.store_index.clear()
        self.list_index = self.db.index_book()
        iters = [None]
        last_iter = None
        last_level = 0
        last_id = self.db_list.get_last(self.id_book)
        if last_id == None or last_id[0] == 0: 
            self.show_page(self.db.first_page()) 
        else:
            self.show_page(last_id[0]) 
        #-----------------------------------
        if len(self.list_index) > 1:
            self.hp.set_position(200)
        else:
            self.hp.set_position(1)
        v = 0
        for i in self.list_index:
            v += 1
            if v%1000 == 999: 
                while (Gtk.events_pending()): Gtk.main_iteration()
            level = i[3]
            if level > last_level: iters.append(last_iter)
            elif level < last_level:
                for j in range(last_level-level): iters.pop()
            try :
                last_iter = self.store_index.append(iters[-1], [i[1], i[2]])
            except :
                pass
            last_level = level
        self.scroll_index.get_hadjustment().set_value(0.0) 
    
    def ok_index(self, *a):  
        model, i = self.sel_index.get_selected()
        if i:
            p = model.get_path(i)
            if model.iter_has_child(i) :
                if self.tree_index.row_expanded(p):
                    self.tree_index.collapse_row(p)
                else: 
                    self.tree_index.expand_row(p, False)
            id_page = model.get_value(i, 0)
            tit = model.get_value(i, 1).decode('utf8')
            self.show_page(id_page)
            asm_customs.with_tag(self.view_nasse_bfr, self.title_select_tag, [tit,], 1, self.view_nasse)
            
            
    def ok_search(self, *a):  
        model, i = self.sel_search.get_selected()
        if i:
            p = model.get_path(i)
            if model.iter_has_child(i) :
                if self.tree_search.row_expanded(p):
                    self.tree_search.collapse_row(p)
                else: self.tree_search.expand_row(p, False)
            id_page = model.get_value(i, 0)
            self.show_page(id_page)
            
    def show_page(self, id_page):
        self.has_commment(id_page)
        self.all_in_page = self.db.get_text_body(id_page)#rowid, id, text, part, page, hno, sora, aya, na
        self.view_nasse_bfr.set_text(self.all_in_page[2])
        titles = self.db.titles_page(self.all_in_page[1])
        try: asm_customs.with_tag(self.view_nasse_bfr, self.view_title_tag, titles)
        except: pass
        self.is_tafsir(self.all_in_page)
        self.current_id = self.all_in_page[0]
        self.ent_page.set_text(str(self.all_in_page[4]))
        self.ent_part.set_text(str(self.all_in_page[3]))
        parts_all, pages_all = self.db.parts_pages(self.all_in_page[3])
        self.parts_all.set_text('/'+str(parts_all))
        self.pages_all.set_text('/'+str(pages_all)+'    ')
        text = self.entry_search.get_text().decode('utf8')
        self.scroll_nasse.get_vadjustment().set_value(0.0)
        if text != u'': 
            tokenize_search = asm_araby.tokenize_search(text)
            asm_customs.with_tag(self.view_nasse_bfr, self.view_search_tag, tokenize_search, 1, self.view_nasse)
        self.view_nasse_bfr.insert(self.view_nasse_bfr.get_end_iter(), u" \n")
        if len(self.opened_old) == 0: self.opened_old.append(id_page)
        elif id_page != self.opened_old[-1]: self.opened_old.append(id_page)
    
    def has_commment(self, id_page):
        if self.db.show_comment(id_page) != None and self.db.show_comment(id_page) != []:
            img = Gtk.Image.new_from_file(join(asm_customs.ICON_DIR, u'com_full.png'))
        else:
            img = Gtk.Image.new_from_file(join(asm_customs.ICON_DIR, u'com_empty.png'))
        self.comment_btn.set_icon_widget(img)
        self.comment_btn.show_all()
    
    def is_tafsir(self, all_in_page):
        try: sora, aya, na = all_in_page[6], all_in_page[7], all_in_page[8]
        except: sora = 0
        if sora > 0 and sora < 115:
            try: na = int(na)
            except: na = 1
            nasse_quran = ' '.join(self.othman.get_ayat(sora,aya,aya+na))
            self.view_nasse_bfr.insert(self.view_nasse_bfr.get_start_iter(), u" \n")
            self.view_nasse_bfr.insert_with_tags(self.view_nasse_bfr.get_start_iter(), 
                                                 nasse_quran, self.view_quran_tag)
    
#    def scroll_event(self, *a):
#        vadj = self.scroll_nasse.get_vadjustment().get_value()
#        if self.nn < 5:
#            self.nn += 1
#            self.scroll_nasse.get_vadjustment().set_value(0.0) 
#        else:
#            if self.vadjustment_page != vadj:
#                self.vadjustment_page = vadj
#            else:
#                if self.n_scroll == 2: 
#                    if self.vadjustment_page == 0.0:
#                        self.previous_page()
#                    else: self.next_page()
#                    self.scroll_nasse.get_vadjustment().set_value(0.0) 
#                    self.n_scroll = 0
#                   .nn  self= 0
#                else: 
#                    self.n_scroll += 1
    
    def move_to_page(self, *a):
        n_page = int(self.ent_page.get_text())
        n_part = int(self.ent_part.get_text())
        id_page = self.db.go_to_page(n_part, n_page)
        if id_page == None: return
        self.show_page(id_page[0])
    
    def search_entry(self, *a):
        text = asm_araby.fuzzy(self.entry_index.get_text().decode('utf8'))
        if text == '':
            self.scroll_index.show_all()
            self.scroll_search.hide()
        else:
            self.scroll_index.hide()
            books = self.db.search_index(text)
            self.store_search.clear()
            c = 1
            for a in books:
                self.store_search.append([a[0], c, a[1], '', 0, 0, '', 0]) 
                c += 1
            self.scroll_search.show_all()
    
#    def autoScroll(self, btn):
#        if not self.autoScrolling: return True
#        vadj = self.scroll_nasse.get_vadjustment()
#        m = vadj.get_upper-vadj.get_page_size
#        n = min(m, vadj.get_value() + 2 )
#        if n == m: btn.set_active(False)
#        vadj.set_value(n)
#        return True
#    
#    def autoScrollCb(self, b, *a):
#        self.autoScrolling = b.get_active()
    
    def editbk_cb(self, *a):
        msg = asm_customs.sure(self.parent, 'عملية تعديل الكتاب عملية دقيقة،\nأي خطأ قد يؤدي لتلف الكتاب،\nهل تريد الاستمرار؟')
        if msg == Gtk.ResponseType.YES:
            self.parent.editbook.close_db()
            self.parent.notebook.set_current_page(8)
            book = self.db_list.file_book(self.id_book)
            self.parent.editbook.add_book(book, self.id_book, self.all_in_page[1])
    
    def comment_cb(self, *a):
        # interface--------------------------------------
        hb = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        box = Gtk.Box(spacing=5,orientation=Gtk.Orientation.VERTICAL)
        dlg = Gtk.Dialog(parent=self.parent)
        dlg.set_icon_name("asmaa")
        dlg.set_default_size(380, 300)
        area = dlg.get_content_area()
        area.set_spacing(6)
        dlg.set_title('التعليق')
        view_comment = Gtk.TextView()
        view_comment_bfr = view_comment.get_buffer()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(view_comment)
        # functions------------------------------------
        id_page = self.all_in_page[1]
        def add_widget():
            chs = hb.get_children()
            for a in chs:
                hb.remove(a)
            if self.db.show_comment(id_page) != None and self.db.show_comment(id_page) != []:
                hb.pack_start(update_btn, False, False, 0)
                hb.pack_start(delete_btn, False, False, 0)
                view_comment_bfr.set_text(self.db.show_comment(id_page)[0])
            else:
                hb.pack_start(save_btn, False, False, 0)
            close_btn = asm_customs.ButtonClass("إغلاق")
            close_btn.connect('clicked',lambda *a: dlg.destroy())
            hb.pack_end(close_btn, False, False, 0)
            dlg.show_all()
        #-----------------------    
        def save_cb(w):
            comment = view_comment_bfr.get_text(view_comment_bfr.get_start_iter(),
                            view_comment_bfr.get_end_iter(), False).decode('utf8')
            if comment == u'': return
            self.db.add_comment(id_page, comment)
            add_widget()
            img = Gtk.Image.new_from_file(join(asm_customs.ICON_DIR, u'com_full.png'))
            self.comment_btn.set_icon_widget(img)
            self.comment_btn.show_all()
        #------------------------    
        def update_cb(w):
            comment = view_comment_bfr.get_text(view_comment_bfr.get_start_iter(),
                            view_comment_bfr.get_end_iter(), False).decode('utf8')
            self.db.update_comment(id_page, comment)
        #-------------------------
        def delete_cb(w):
            self.db.remove_comment(id_page)
            view_comment_bfr.set_text('')
            add_widget()
            img = Gtk.Image.new_from_file(join(asm_customs.ICON_DIR, u'com_empty.png'))
            self.comment_btn.set_icon_widget(img)
            self.comment_btn.show_all()
        #-----------------------------------
        save_btn = asm_customs.ButtonClass("حفظ")
        save_btn.connect('clicked', save_cb)
        update_btn = asm_customs.ButtonClass("حفظ")
        update_btn.connect('clicked', update_cb)
        delete_btn = asm_customs.ButtonClass("حذف")
        delete_btn.connect('clicked', delete_cb)
        #----------------------------
        box.pack_start(scroll, True, True, 0)
        box.pack_start(hb, False, False, 0)
        area.pack_start(box, True, True, 0)
        add_widget()
       
    def build(self, *a):
        self.vadjustment_page = 0.0
        self.hp = Gtk.HPaned()
        
        # a الفهرس-----------------------------------
        vbox = Gtk.VBox(False, 3)
        self.tree_index = asm_customs.TreeIndex()
        cell = Gtk.CellRendererText()
        kal = Gtk.TreeViewColumn('الفهرس', cell, text=1)
        self.tree_index.append_column(kal)
        self.store_index = Gtk.TreeStore(int, str)
        self.tree_index.set_model(self.store_index)
        self.sel_index = self.tree_index.get_selection()
        self.tree_index.connect("cursor-changed", self.ok_index)
        self.scroll_index = Gtk.ScrolledWindow()
        self.scroll_index.set_shadow_type(Gtk.ShadowType.IN)
        self.scroll_index.add(self.tree_index)
        self.scroll_index.get_hadjustment().set_value(0.0) 
        vbox.pack_start(self.scroll_index, True, True, 0)
        #----------------------------------------------
        self.tree_search = asm_customs.TreeIndex()
        cell = Gtk.CellRendererText()
        raq = Gtk.TreeViewColumn('الرقم', cell, text=1)
        self.tree_search.append_column(raq)
        cell = Gtk.CellRendererText()
        kal = Gtk.TreeViewColumn('أغلق النتائج', cell, text=2)
        kal.set_clickable(True)
        kal.connect('clicked', self.hide_search)
        self.tree_search.append_column(kal)
        self.store_search = Gtk.ListStore(int, int, str, str, int, int, str, int)
        self.tree_search.set_model(self.store_search)
        self.sel_search = self.tree_search.get_selection()
        self.tree_search.connect("cursor-changed", self.ok_search)
        self.scroll_search = Gtk.ScrolledWindow()
        self.scroll_search.set_shadow_type(Gtk.ShadowType.IN)
        self.scroll_search.add(self.tree_search)
        self.scroll_search.get_hadjustment().set_value(0.0) 
        vbox.pack_start(self.scroll_search, True, True, 0)
        
        try: self.entry_index = Gtk.SearchEntry()
        except: self.entry_index = Gtk.Entry()
        self.entry_index.set_placeholder_text('بحث في الفهرس')
        self.entry_index.connect('changed', self.search_entry)
        vbox.pack_start(self.entry_index, False, False, 0)
        self.hp.pack1(vbox, True, True)
        
        # a عارض النص-----------------------------------
        vbox = Gtk.VBox(False, 3)
        self.view_nasse = asm_customs.ViewClass()
        self.view_nasse_bfr = self.view_nasse.get_buffer()
        self.view_nasse.connect_after("populate-popup", asm_popup.populate_popup, self.parent)
        self.view_title_tag = self.view_nasse_bfr.create_tag("title")
        self.view_quran_tag = self.view_nasse_bfr.create_tag("quran")
        self.view_search_tag = self.view_nasse_bfr.create_tag("search")
        self.view_terms_tag = self.view_nasse_bfr.create_tag("terms")
        self.title_select_tag = self.view_nasse_bfr.create_tag("tit_select")
        self.scroll_nasse = Gtk.ScrolledWindow()
        self.scroll_nasse.set_shadow_type(Gtk.ShadowType.IN)
        self.scroll_nasse.add_with_viewport(self.view_nasse)
        vbox.pack_start(self.scroll_nasse, True, True, 0)
        hbox = Gtk.HBox(False, 3)
        self.page_n = Gtk.Label('الصفحة')
        hbox.pack_start(self.page_n, False, False, 0) 
        self.ent_page = Gtk.Entry()
        self.ent_page.set_width_chars(5)
        hbox.pack_start(self.ent_page, False, False, 0)
        self.pages_all = Gtk.Label()
        hbox.pack_start(self.pages_all, False, False, 0) 
        self.part_n = Gtk.Label('الجزء') 
        self.ent_part = Gtk.Entry()
        self.ent_part.set_width_chars(5) 
        hbox.pack_start(self.part_n, False, False, 0)
        hbox.pack_start(self.ent_part, False, False, 0) 
        self.parts_all = Gtk.Label()
        hbox.pack_start(self.parts_all, False, False, 0) 
        move_btn = Gtk.ToolButton(stock_id=Gtk.STOCK_JUMP_TO)
        move_btn.set_tooltip_text('الانتقال إلى الصفحة المحددة')
        move_btn.connect('clicked', self.move_to_page)
        hbox.pack_start(move_btn,False,False,2)
        
        search_btn = Gtk.ToolButton(stock_id=Gtk.STOCK_FIND)
        search_btn.set_tooltip_text("البحث في الكتاب")
        search_btn.connect('clicked', self.search_in_book)
        try: self.entry_search = Gtk.SearchEntry()
        except: self.entry_search = Gtk.Entry()
        self.entry_search.set_placeholder_text('بحث في النصّ')
        self.entry_search.connect('changed', self.search_in_page)
        self.entry_search.connect('activate', self.search_in_page)
        hbox.pack_start(search_btn, False, False, 0)
        hbox.pack_start(self.entry_search, False, False, 0)
        
#        img = Gtk.Image.new_from_file(join(asm_customs.ICON_DIR, u'com_empty.png'))
#        self.comment_btn.set_icon_widget(img)
        self.comment_btn = Gtk.ToolButton() 
        self.comment_btn.set_tooltip_text("أظهر التعليق")
        self.comment_btn.connect('clicked', self.comment_cb)
        hbox.pack_start(self.comment_btn, False, False, 0)
        
        self.editbk = Gtk.ToolButton(stock_id=Gtk.STOCK_EDIT) 
        self.editbk.set_tooltip_text("تحرير كتاب")
        self.editbk.connect('clicked', self.editbk_cb)
        hbox.pack_end(self.editbk, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        
#        img = Gtk.Image()
#        img.set_from_stock(Gtk.STOCK_MEDIA_FORWARD, Gtk.IconSize.BUTTON)
#        btn_autoScroll = Gtk.ToggleButton()
#        btn_autoScroll.add(img)
#        hbox.pack_start(btn_autoScroll, False, False, 0)
#        self.autoScrolling = False
#        btn_autoScroll.connect("clicked", self.autoScrollCb)
#        GLib.timeout_add(100, self.autoScroll, btn_autoScroll)
        
        self.hp.pack2(vbox, True, False)
        self.pack_start(self.hp, True, True, 0)
        self.show_all()
        self.scroll_search.hide()
#        self.set_index()
        self.change_font()