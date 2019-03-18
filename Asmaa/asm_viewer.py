# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
##############################################################################

from gi.repository import Gtk, Gdk, GLib, GObject, Pango
from asm_contacts import bookDB, Othman, listDB
import asm_customs, asm_araby, asm_path, asm_config
from os.path import join, basename
import asm_popup

# class صفحة الكتب المفتوحة-----------------------------------------------------------------------

class ViewerBooks(Gtk.Notebook):
    
    # a التصفح--------------------------------------------
    
    def convert_browse(self, *a):
        for n in range(self.get_n_pages()):
            ch = self.get_nth_page(n)
            ch.convert_browse()
        
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
    
    def editbk_cb(self, *a):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        ch.editbk_cb()
    
    def search_on_page(self, text):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        ch.search_on_page(text)
    
    def search_on_active(self, text):
        n = self.get_current_page()
        ch = self.get_nth_page(n)
        ch.search_on_active(text)
    
    def __init__(self, parent):
        self.session = [[], None]
        Gtk.Notebook.__init__(self)
        self.set_border_width(5)
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
                self.parent.notebook.set_current_page(0)
                if self.parent.notebook.get_current_page() == 1: 
                    self.parent.opened.remove(1L)
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
        self.view_title_tag1.set_property('foreground', self.parent.theme.color_tit)
        self.view_title_tag1.set_property('font', self.parent.theme.font_tit)
        self.view_quran_tag1.set_property('foreground', self.parent.theme.color_qrn)
        self.view_quran_tag1.set_property("paragraph-background", self.parent.theme.color_bg_qrn)
        self.view_quran_tag1.set_property('font', self.parent.theme.font_qrn)
        self.view_search_tag1.set_property('background', self.parent.theme.color_fnd)
        self.view_terms_tag1.set_property('foreground', self.parent.theme.color_tit)
        self.view_title_tag2.set_property('foreground', self.parent.theme.color_tit)
        self.view_title_tag2.set_property('font', self.parent.theme.font_tit)
        self.view_quran_tag2.set_property('foreground', self.parent.theme.color_qrn)
        self.view_quran_tag2.set_property("paragraph-background", self.parent.theme.color_bg_qrn)
        self.view_quran_tag2.set_property('font', self.parent.theme.font_qrn)
        self.view_search_tag2.set_property('background', self.parent.theme.color_fnd)
        self.view_terms_tag2.set_property('foreground', self.parent.theme.color_tit)
    
    def search_on_active(self, text):
        if text == u'': return
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
        
    def search_on_page(self, text):
        self.show_page(self.all_in_page[1])
        self.search_now(text)
        
    def search_now(self, text):
        search_tokens = []
        star_iter1 = self.view_nasse_bfr1.get_start_iter()
        end_iter1 = self.view_nasse_bfr1.get_end_iter()
        star_iter2 = self.view_nasse_bfr2.get_start_iter()
        end_iter2 = self.view_nasse_bfr2.get_end_iter()
        self.view_nasse_bfr1.remove_tag_by_name("search1", star_iter1, end_iter1)
        self.view_nasse_bfr2.remove_tag_by_name("search2", star_iter2, end_iter2)
        nasse1 = self.view_nasse_bfr1.get_text(star_iter1, end_iter1, True).split()
        nasse2 = self.view_nasse_bfr2.get_text(star_iter2, end_iter2, True).split()
        if text == u'': 
            return
        else:
            txt = asm_araby.fuzzy(text)
            for term in nasse1: 
                if txt in asm_araby.fuzzy(term.decode('utf8')):
                    search_tokens.append(term)
            for term in nasse2: 
                if txt in asm_araby.fuzzy(term.decode('utf8')):
                    search_tokens.append(term)
        asm_customs.with_tag(self.view_nasse_bfr1, self.view_search_tag1, search_tokens, 1)
        asm_customs.with_tag(self.view_nasse_bfr2, self.view_search_tag2, search_tokens, 1)


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
        self.stack.set_transition_type(self.style_browse_prev)
        if self.db.first_page() == self.all_in_page[1]: return
        self.show_page(self.db.first_page())
        id_page = self.all_in_page[1]
        try: self.store_index.foreach(self.index_highlight, id_page)
        except: pass
        ch = self.stack.get_visible_child_name()
        if ch == "n1": self.stack.set_visible_child_name("n2")
        else: self.stack.set_visible_child_name("n1")
        GObject.timeout_add(200, self.reset_event)
    
    def previous_page(self, *a):
        self.stack.set_transition_type(self.style_browse_prev)
        if self.db.previous_page(self.current_id) == self.all_in_page[1]: return
        self.show_page(self.db.previous_page(self.current_id))
        id_page = self.all_in_page[1]
        try: self.store_index.foreach(self.index_highlight, id_page)
        except: pass
        ch = self.stack.get_visible_child_name()
        if ch == "n1": self.stack.set_visible_child_name("n2")
        else: self.stack.set_visible_child_name("n1")
        GObject.timeout_add(200, self.reset_event)
    
    def next_page(self, *a):
        self.stack.set_transition_type(self.style_browse_next)
        if self.db.next_page(self.current_id) == self.all_in_page[1]: return
        self.show_page(self.db.next_page(self.current_id))
        id_page = self.all_in_page[1]
        try: self.store_index.foreach(self.index_highlight, id_page)
        except: pass
        ch = self.stack.get_visible_child_name()
        if ch == "n1": self.stack.set_visible_child_name("n2")
        else: self.stack.set_visible_child_name("n1")
        GObject.timeout_add(200, self.reset_event)
    
    def last_page(self, *a):
        self.stack.set_transition_type(self.style_browse_next)
        if self.db.last_page() == self.all_in_page[1]: return
        self.show_page(self.db.last_page())
        id_page = self.all_in_page[1]
        try: self.store_index.foreach(self.index_highlight, id_page)
        except: pass
        ch = self.stack.get_visible_child_name()
        if ch == "n1": self.stack.set_visible_child_name("n2")
        else: self.stack.set_visible_child_name("n1")
        GObject.timeout_add(200, self.reset_event)
    
    def back_to_old(self, *a):
        if len(self.opened_old) == 1: return
        n = self.opened_old.pop()
        self.stack.set_transition_type(self.style_browse_prev)
        self.show_page(self.opened_old[-1])
        ch = self.stack.get_visible_child_name()
        if ch == "n1": self.stack.set_visible_child_name("n2")
        else: self.stack.set_visible_child_name("n1")
        self.opened_new.append(n)
        
    def advance_to_new(self, *a):
        if len(self.opened_new) == 0: return
        n = self.opened_new.pop()
        self.stack.set_transition_type(self.style_browse_prev)
        self.show_page(n)
        ch = self.stack.get_visible_child_name()
        if ch == "n1": self.stack.set_visible_child_name("n2")
        else: self.stack.set_visible_child_name("n1")
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
        self.stack.set_visible_child_name("n2")
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
                    #self.scroll_index.get_hadjustment().set_lower(True)
            id_page = model.get_value(i, 0)
            tit = model.get_value(i, 1).decode('utf8')

            if self.current_id < id_page: self.stack.set_transition_type(self.style_browse_next)
            elif self.current_id > id_page: self.stack.set_transition_type(self.style_browse_prev)
            elif self.current_id == id_page: return
            self.show_page(id_page)
            ch = self.stack.get_visible_child_name()
            if ch == "n1": 
                self.stack.set_visible_child_name("n2")
                asm_customs.with_tag(self.view_nasse_bfr1, self.title_select_tag1, [tit,], 1, self.view_nasse1)
            else: 
                self.stack.set_visible_child_name("n1")
                asm_customs.with_tag(self.view_nasse_bfr2, self.title_select_tag2, [tit,], 1, self.view_nasse2)
            GObject.timeout_add(200, self.reset_event)
            
   
    def ok_search(self, *a):  
        model, i = self.sel_search.get_selected()
        if i:
            p = model.get_path(i)
            if model.iter_has_child(i) :
                if self.tree_search.row_expanded(p):
                    self.tree_search.collapse_row(p)
                else: self.tree_search.expand_row(p, False)
            id_page = model.get_value(i, 0)
            
            if self.current_id < id_page: self.stack.set_transition_type(self.style_browse_next)
            elif self.current_id > id_page: self.stack.set_transition_type(self.style_browse_prev)
            elif self.current_id == id_page: return
            self.show_page(id_page)
            ch = self.stack.get_visible_child_name()
            if ch == "n1": 
                self.stack.set_visible_child_name("n2")
            else: 
                self.stack.set_visible_child_name("n1")
    
    def show_page(self, id_page):
        self.all_in_page = self.db.get_text_body(id_page)#rowid, id, text, part, page, hno, sora, aya, na
        self.has_commment(id_page)
        titles = self.db.titles_page(self.all_in_page[1])
        ch = self.stack.get_visible_child_name()
        if ch == "n1": 
            self.view_nasse_bfr2.set_text(self.all_in_page[2])
            self.view_nasse_bfr2.insert(self.view_nasse_bfr2.get_end_iter(), u" \n")
            try: asm_customs.with_tag(self.view_nasse_bfr2, self.view_title_tag2, titles)
            except: pass 
        else:
            self.view_nasse_bfr1.set_text(self.all_in_page[2])
            self.view_nasse_bfr1.insert(self.view_nasse_bfr1.get_end_iter(), u" \n")
            try: asm_customs.with_tag(self.view_nasse_bfr1, self.view_title_tag1, titles)
            except: pass
        self.is_tafsir(self.all_in_page)
        self.current_id = self.all_in_page[0]
        self.ent_page.set_text(str(self.all_in_page[4]))
        self.ent_part.set_text(str(self.all_in_page[3]))
        text = self.parent.entry_search.get_text().decode('utf8')
        if text != u'': 
            self.search_now(text)
        if len(self.opened_old) == 0: self.opened_old.append(id_page)
        elif id_page != self.opened_old[-1]: self.opened_old.append(id_page)
        self.stack.show_all()
        self.scroll_nasse1.get_vadjustment().set_value(0.0)
        self.scroll_nasse2.get_vadjustment().set_value(0.0)
    
    def reset_event(self, *a):
        self.scroll_nasse1.get_vadjustment().set_lower(True)
        self.scroll_nasse2.get_vadjustment().set_lower(True)
        self.scroll_nasse1.get_vadjustment().set_value(0.0)
        self.scroll_nasse2.get_vadjustment().set_value(0.0)
    
    def scroll_event(self, sc, ev):
#        if ev.type == Gdk.EventType.SCROLL: print "scroll"
#        if ev.direction == Gdk.ScrollDirection.SMOOTH: print "Up"
        if asm_config.getn('mouse_browse') == 0: return
        vadj = sc.get_vadjustment()
        p = vadj.get_page_size()
        m = vadj.get_upper()-p
        v = vadj.get_value()
        if m == v:
            if self.vadj_page_next == 5:
                self.next_page()
                self.vadj_page_next = 0
            else:
                self.vadj_page_next += 1
        elif v <= 1.0:
            if self.vadj_page_prev == 5:
                if ev.get_scroll_deltas()[2] == -1.0:
                    self.previous_page()
                if ev.get_scroll_deltas()[2] == 1.0:
                    self.next_page()
                self.vadj_page_prev = 0
            else:
                self.vadj_page_prev += 1
        else:
            self.vadj_page_next = 0
            self.vadj_page_prev = 0
    
    def convert_browse(self, *a):
        ls = [1, 2, 5, 10, 15, 20, 30]
        self.stack.set_transition_duration(ls[asm_config.getn('time_browse')]*100)
        GObject.source_remove(self.timeo)
        self.timeo = GLib.timeout_add(100/((asm_config.getn('auto_browse'))*8), self.autoScroll, None)
        if asm_config.getn('style_browse') == 0:
            self.style_browse_next = Gtk.StackTransitionType.NONE
            self.style_browse_prev = Gtk.StackTransitionType.NONE
        elif asm_config.getn('style_browse') == 1:
            self.style_browse_next = Gtk.StackTransitionType.CROSSFADE
            self.style_browse_prev = Gtk.StackTransitionType.CROSSFADE
        elif asm_config.getn('style_browse') == 2:
            self.style_browse_next = Gtk.StackTransitionType.SLIDE_LEFT
            self.style_browse_prev = Gtk.StackTransitionType.SLIDE_RIGHT
        elif asm_config.getn('style_browse') == 3:
            self.style_browse_next = Gtk.StackTransitionType.SLIDE_UP
            self.style_browse_prev = Gtk.StackTransitionType.SLIDE_DOWN 
#        sz = self.parent.get_size()
#        self.box_view1.set_size_request(-1, sz[1])
#        self.box_view2.set_size_request(-1, sz[1])
    
    def has_commment(self, id_page):
        if self.db.show_comment(id_page) != None and self.db.show_comment(id_page) != []:
            img = Gtk.Image.new_from_file(join(asm_path.ICON_DIR, u'com_full.png'))
        else:
            img = Gtk.Image.new_from_file(join(asm_path.ICON_DIR, u'com_empty.png'))
        self.comment_btn.set_image(img)
        self.comment_btn.show_all()
    
    def is_tafsir(self, all_in_page):
        try: sora, aya, na = all_in_page[6], all_in_page[7], all_in_page[8]
        except: sora = 0
        if sora > 0 and sora < 115:
            try: na = int(na)
            except: na = 1
            nasse_quran = ' '.join(self.othman.get_ayat(sora,aya,aya+na))
            ch = self.stack.get_visible_child_name()
            if ch == "n2":
                self.view_nasse_bfr1.insert(self.view_nasse_bfr1.get_start_iter(), u" \n")
                self.view_nasse_bfr1.insert_with_tags(self.view_nasse_bfr1.get_start_iter(), 
                                                 nasse_quran, self.view_quran_tag1)
            else:
                self.view_nasse_bfr2.insert(self.view_nasse_bfr2.get_start_iter(), u" \n")
                self.view_nasse_bfr2.insert_with_tags(self.view_nasse_bfr2.get_start_iter(), 
                                                 nasse_quran, self.view_quran_tag2)
    
    def move_to_page(self, *a):
        dlg = Gtk.Dialog(parent=self.parent)
        dlg.set_icon_name("asmaa")
        dlg.set_position(Gtk.WindowPosition.MOUSE)
        dlg.set_title('انتقل إلى صفحة محدّدة')
        parts_all, pages_all = self.db.parts_pages(self.all_in_page[3])
        ent_page = Gtk.Entry()
        lab_page = Gtk.Label(u"عدد الصفحات "+str(pages_all))
        ent_page.set_text(str(self.all_in_page[4]))
        ent_part = Gtk.Entry()
        lab_part = Gtk.Label(u"عدد الأجزاء "+str(parts_all))
        ent_part.set_text(str(self.all_in_page[3]))
        clo = asm_customs.ButtonClass("ألغ")
        clo.connect('clicked',lambda *a: dlg.destroy())
        move = Gtk.Button("انتقل")
        def replace_cb(widget):
            n_page = int(ent_page.get_text())
            n_part = int(ent_part.get_text())
            id_page = self.db.go_to_page(n_part, n_page)
            if id_page == None: 
                for n in range(20):
                    id_page = self.db.go_to_nearer_page(n_part, n_page, n+1)
                    if id_page != None: break
            if id_page == None: 
                asm_customs.erro(self.parent, "لا يمكن الذهاب إلى الصفحة المحددة")
                return
            if self.current_id < id_page[0]: self.stack.set_transition_type(self.style_browse_next)
            elif self.current_id > id_page[0]: self.stack.set_transition_type(self.style_browse_prev)
            elif self.current_id == id_page[0]: return
            self.show_page(id_page[0])
            ch = self.stack.get_visible_child_name()
            if ch == "n1": 
                self.stack.set_visible_child_name("n2")
            else: 
                self.stack.set_visible_child_name("n1")
            dlg.destroy()
        move.connect('clicked', replace_cb)
        ent_page.connect('activate', replace_cb)
        ent_part.connect('activate', replace_cb)
        box = dlg.vbox
        box.set_border_width(5)
        hb = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        hb.pack_start(ent_page, False, False, 3)
        hb.pack_start(lab_page, False, False, 3)
        box.pack_start(hb, False, False, 3)
        hb = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        hb.pack_start(ent_part, False, False, 3)
        hb.pack_start(lab_part, False, False, 3)
        box.pack_start(hb, False, False, 3)
        hb = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        hb.pack_start(move, False, False, 0)
        hb.pack_end(clo, False, False, 0)
        box.pack_end(hb, False, False, 0)
        dlg.show_all()
        
    
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
    
    def autoScroll(self, *a):
        if not self.autoScrolling: return True
        ch = self.stack.get_visible_child_name()
        if ch == "n1":
            vadj = self.scroll_nasse1.get_vadjustment()
        else:
            vadj = self.scroll_nasse2.get_vadjustment()
        m = vadj.get_upper()-vadj.get_page_size()
        n = min(m, vadj.get_value()+0.1)
        if n == m: self.btn_autoScroll.set_active(False)
        vadj.set_value(n)
        return True
    
    def autoScrollCb(self, b, *a):
        self.autoScrolling = b.get_active()
        
    # a تحرير الكتاب المفتوح----------------------------------
    
    def editbk_cb(self, *a):
        self.parent.editbook.close_db()
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
            img = Gtk.Image.new_from_file(join(asm_path.ICON_DIR, u'com_full.png'))
            self.comment_btn.set_image(img)
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
            img = Gtk.Image.new_from_file(join(asm_path.ICON_DIR, u'com_empty.png'))
            self.comment_btn.set_image(img)
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
        self.vadj_page_next = 0
        self.vadj_page_prev= 0
        self.hp = Gtk.HPaned()
        self.parent.connect("check-resize", self.convert_browse)
        
        # a الفهرس-----------------------------------
        vbox = Gtk.VBox(False, 3)
        self.tree_index = asm_customs.TreeIndex()
        cell = Gtk.CellRendererText()
        cell.set_property("ellipsize", Pango.EllipsizeMode.END)
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
        cell.set_property("ellipsize", Pango.EllipsizeMode.END)
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
        self.stack = Gtk.Stack()
        vbox.pack_start(self.stack, True, True, 0)
        #-------------------------------------
        self.view_nasse1 = asm_customs.ViewClass()
        self.view_nasse_bfr1 = self.view_nasse1.get_buffer()
        self.view_nasse1.connect_after("populate-popup", asm_popup.populate_popup, self.parent)
        self.scroll_nasse1 = Gtk.ScrolledWindow()
#        self.scroll_nasse1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll_nasse1.set_shadow_type(Gtk.ShadowType.IN)
#        self.box_view1 = Gtk.Box(spacing=5,orientation=Gtk.Orientation.VERTICAL)
        self.scroll_nasse1.add(self.view_nasse1)
#        self.box_view1.pack_start(self.view_nasse1, True, True, 0)
        self.scroll_event_name1 = self.scroll_nasse1.connect('scroll-event', self.scroll_event)
        self.view_title_tag1 = self.view_nasse_bfr1.create_tag("title1")
        self.view_quran_tag1 = self.view_nasse_bfr1.create_tag("quran1")
        self.view_search_tag1 = self.view_nasse_bfr1.create_tag("search1")
        self.view_terms_tag1 = self.view_nasse_bfr1.create_tag("terms1")
        self.title_select_tag1 = self.view_nasse_bfr1.create_tag("tit_select1")
        self.stack.add_named(self.scroll_nasse1, 'n1')
        #-------------------------------------
        self.view_nasse2 = asm_customs.ViewClass()
        self.view_nasse_bfr2 = self.view_nasse2.get_buffer()
        self.view_nasse2.connect_after("populate-popup", asm_popup.populate_popup, self.parent)
        self.scroll_nasse2 = Gtk.ScrolledWindow()
#        self.scroll_nasse2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll_nasse2.set_shadow_type(Gtk.ShadowType.IN)
#        self.box_view2 = Gtk.Box(spacing=5,orientation=Gtk.Orientation.VERTICAL)
        self.scroll_nasse2.add(self.view_nasse2)
#        self.box_view2.pack_start(self.view_nasse2, True, True, 0)
        self.scroll_event_name2 = self.scroll_nasse2.connect('scroll-event', self.scroll_event)
        self.view_title_tag2 = self.view_nasse_bfr2.create_tag("title2")
        self.view_quran_tag2 = self.view_nasse_bfr2.create_tag("quran2")
        self.view_search_tag2 = self.view_nasse_bfr2.create_tag("search2")
        self.view_terms_tag2 = self.view_nasse_bfr2.create_tag("terms2")
        self.title_select_tag2 = self.view_nasse_bfr2.create_tag("tit_select2")
        self.stack.add_named(self.scroll_nasse2, 'n2')
        #----------------------------------------
        hbox = Gtk.HBox(False, 3)
        hbox.pack_start(Gtk.Label('('), False, False, 0) 
        self.ent_page = Gtk.Label()
        hbox.pack_start(self.ent_page, False, False, 0)
        hbox.pack_start(Gtk.Label('/'), False, False, 0) 
        self.ent_part = Gtk.Label()
        hbox.pack_start(self.ent_part, False, False, 0) 
        hbox.pack_start(Gtk.Label(')'), False, False, 0)
        
        move_btn = Gtk.Button()
        move_btn.set_tooltip_text('الانتقال إلى الصفحة المحددة')
        img = Gtk.Image()
        move_btn.connect("clicked", self.move_to_page)
        img.set_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.LARGE_TOOLBAR)
        move_btn.set_image(img)
        hbox.pack_start(move_btn,False,False,10)

        self.comment_btn = Gtk.Button() 
        self.comment_btn.set_tooltip_text("أظهر التعليق")
        self.comment_btn.connect('clicked', self.comment_cb)
        hbox.pack_start(self.comment_btn, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        img = Gtk.Image()
        img.set_from_stock(Gtk.STOCK_MEDIA_FORWARD, Gtk.IconSize.BUTTON)
        self.btn_autoScroll = Gtk.ToggleButton()
        self.btn_autoScroll.add(img)
        self.btn_autoScroll.set_tooltip_text("استعراض آلي")
        hbox.pack_start(self.btn_autoScroll, False, False, 0 )
        self.autoScrolling = False
        self.btn_autoScroll.connect("clicked", self.autoScrollCb)
        self.timeo = GLib.timeout_add(100/((asm_config.getn('auto_browse'))*8), self.autoScroll, None)
        
        self.convert_browse()
        self.hp.pack2(vbox, True, False)
        self.pack_start(self.hp, True, True, 0)
        self.show_all()
        self.scroll_search.hide()
        self.change_font()
        if self.id_book != -1:
            if self.db_list.book_dir(self.id_book) == asm_path.BOOK_DIR_r:
                self.comment_btn.set_sensitive(False)