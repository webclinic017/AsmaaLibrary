# -*- coding: utf-8 -*-

#a############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  #########
#a############################################################################

from os.path import join
import os
from gi.repository import Gtk, GObject
import asm_araby, asm_customs, asm_popup
from asm_viewer import OpenBook
from asm_tablabel import TabLabel
from asm_contacts import bookDB, Othman, listDB
import cPickle
import sqlite3

# class عارض نتائج البحث-------------------------------------------------------------------

class ShowResult(Gtk.VPaned):
   
    def __init__(self, parent):
        self.db = None
        self.db_list = listDB()
        self.ls_term = []
        self.parent = parent
        self.cursive = False
        self.results_books = []
        self.stop_n = 1
        self.build()
    
    def show_result(self, *a):
        model, i = self.sel_result.get_selected()
        if i:
            if self.db != None:
                self.db.close_db()
                del self.db
            id_page = model.get_value(i, 0)
            self.id_book = model.get_value(i, 6)
            self.book = self.db_list.file_book(self.id_book)
            self.nm_book = model.get_value(i, 2).decode('utf8')
            self.db = bookDB(self.book, self.id_book)
            self.show_page(id_page)
    
    def search(self, text, dict_perf, dict_field, selected_books):
        self.cursive = dict_perf['cursive']
        text = text.replace('"','')
        text = text.replace("'","")
        ls_term = []
        if dict_field['nass']: 
            field = 'nass'
            table = 'pages'
        else: 
            field = 'tit'
            table = 'titles'
        if dict_perf['with_tachkil'] == True: 
            cond = '{} LIKE ?'.format(field,)
        else:
            cond = 'fuzzy({}) LIKE ?'.format(field,)
            text = asm_araby.fuzzy_plus(text)
        if dict_perf['identical'] == True:  pfx, sfx = '% ', ' %'
        else: pfx, sfx = '%', '%'
        if dict_perf['cursive'] == True:
            condition = 'fuzzy({}) LIKE ?'.format(field,)
            ls_term.append(pfx+text+sfx)
        else: 
            for a in text.split(u' '):
                ls_term.append(pfx+a+sfx)
            if dict_perf['one_term'] == True:
                condition = ' OR '.join([cond]*len(ls_term))
            else :
                condition = ' AND '.join([cond]*len(ls_term))
        for a in ls_term:
            self.ls_term.append(a.replace('%', ''))
        n = 1
        s = 1
        for a in selected_books:
            if self.stop_n == 0: break
            s += 1
            book = join(asm_customs.MY_DIR, u'books', a[1], a[0]+u'.asm')
            con = sqlite3.connect(book)
            con.create_function('fuzzy', 1, asm_araby.fuzzy_plus)
            cur = con.cursor()
            if table == 'pages': len_book = len(cur.execute('SELECT id FROM pages').fetchall())
            else: len_book = len(cur.execute('SELECT id FROM titles').fetchall())
            parts = len_book/200
            remainder = len_book-(200*parts)
            v = 0
            while v in range(parts+1):
                while (Gtk.events_pending()): Gtk.main_iteration()
                p1 = v*200
                p2 = (v+1)*200
                if v < parts:
                    cond = 'id BETWEEN {} and {}'.format(p1, p2)
                elif v == parts:
                    cond = 'id BETWEEN {} and {}'.format(p1, remainder)
                elif v > parts:
                    pass  
                if table == 'pages':
                    cur.execute("""SELECT id, part, page FROM pages WHERE {} AND {}""".format(cond, condition), ls_term)
                    i_pgs = cur.fetchall()
                    for i in i_pgs:
                        j = i[0]
                        try: pg = int(i[2])
                        except: pg = 1
                        try: pr = int(i[1])
                        except: pr = 1
                        cur.execute('SELECT tit FROM titles WHERE id<=?', (j,)) 
                        try: tit = cur.fetchall()[-1][0]
                        except: tit = '......'
                        self.store_results.append([j, n, a[0], tit, pr, pg, a[2]])
                        n += 1
                        self.lab_n_result.set_text('عدد النتائج : {}'.format(n-1, ))
                else:
                    cur.execute("""SELECT id, tit FROM titles WHERE {} AND {}""".format(cond, condition), ls_term)
                    i_tits = cur.fetchall()
                    for i in i_tits:
                        self.store_results.append([i[0], n, a[0], i[1], 0, 0, a[2]])
                        n += 1
                        self.lab_n_result.set_text('عدد النتائج : {}'.format(n-1, ))
                v += 1
            self.progress.set_fraction(float(s)/(float(len(selected_books))))
            cur.close()
            con.close()
        self.progress.set_fraction(0.0)
        self.hb_stop.hide()
        if len(self.store_results)>0:
            for a in self.store_results:
                self.results_books.append([a[0], a[1], a[2], a[3], a[4], a[5], a[6]])
            output = open(join(asm_customs.HOME_DIR, u'آخر بحث.pkl'), 'wb')
            cPickle.dump(self.results_books, output)
            output.close()
   
    def sav_result_cb(self, *a):
        nm = self.sav_result_entry.get_text().decode('utf8')
        if nm == u"":
            asm_customs.erro(self.parent, "أدخل الاسم أولا.")
        elif nm in os.listdir(asm_customs.HOME_DIR): 
            asm_customs.erro(self.parent, "يوجد بحث محفوظ بنفس الاسم !!")
        else:
            output = open(join(asm_customs.HOME_DIR, nm+u'.pkl'), 'wb')
            cPickle.dump(self.results_books, output)
            output.close()
        self.sav_result_entry.set_text("")

    
    def first_page(self, *a):
        self.show_page(self.db.first_page())
    
    def previous_page(self, *a):
        self.show_page(self.db.previous_page(self.current_id))
    
    def next_page(self, *a):
        self.show_page(self.db.next_page(self.current_id))
    
    def last_page(self, *a):
        self.show_page(self.db.last_page())
    
    def show_page(self, id_page):
        self.all_in_page = self.db.get_text_body(id_page)#rowid, id, text, part, page, hno, sora, aya, na
        self.view_nasse_bfr.set_text(self.all_in_page[2])
        titles = self.db.titles_page(self.all_in_page[1])
        asm_customs.with_tag(self.view_nasse_bfr, self.view_title_tag, titles)
        self.is_tafsir(self.all_in_page)
        self.current_id = self.all_in_page[0]
        self.view_nasse.scroll_to_iter(self.view_nasse_bfr.get_start_iter(), 0.0, True, 0.5, 0.5)
        if len(self.ls_term) == 0: 
            return
        match_start = asm_customs.with_tag(self.view_nasse_bfr, self.view_search_tag, self.ls_term, 1)
        if match_start:
            self.view_nasse.scroll_to_iter(match_start, 0.0, False, 0.5, 0.5)
    
    def is_tafsir(self, all_in_page):
        try: sora, aya, na = all_in_page[6], all_in_page[7], all_in_page[8]
        except: sora = 0
        if sora > 0 and sora < 115:
            try: na = int(na)
            except: na = 1
            nasse_quran = ' '.join(Othman().get_ayat(sora,aya,aya+na))
            self.view_nasse_bfr.insert(self.view_nasse_bfr.get_start_iter(), u" \nـــــــــــــــــــ\n")
            self.view_nasse_bfr.insert_with_tags(self.view_nasse_bfr.get_start_iter(), nasse_quran, self.view_quran_tag)
    
    def search_in_result(self, *a):
        text = self.sav_result_entry.get_text().decode('utf8')
        sr = ShowResult(self.parent)
        self.parent.viewerbook.append_page(sr,TabLabel(sr, u'بحث عن :'+text))
        self.parent.viewerbook.set_current_page(-1)
        n = 0
        s = 0
        for a in self.store_results:
            while (Gtk.events_pending()): Gtk.main_iteration()
            n += 1
            if self.stop_n == 0: break
            book = self.db_list.file_book(a[6])
            db = bookDB(book, a[6])
            res = db.search_in_page(a[0], text)
            if res == True:
                s += 1
                sr.store_results.append([a[0], s, a[2], a[3], a[4], a[5], a[6]])
            sr.progress.set_fraction(float(n)/(float(len(self.store_results))))
            sr.lab_n_result.set_text('عدد النتائج : {}'.format(s, ))
        sr.progress.set_fraction(0.0)
        sr.hb_stop.hide()
        if len(sr.store_results)>0:
            for a in sr.store_results:
                sr.results_books.append([a[0], a[1], a[2], a[3], a[4], a[5], a[6]])
            output = open(join(asm_customs.HOME_DIR, u'آخر بحث.pkl'), 'wb')
            cPickle.dump(sr.results_books, output)
            output.close()

    def open_new_tab(self, *a):
        n = self.parent.viewerbook.get_n_pages()
        for s in range(n):
            ch = self.parent.viewerbook.get_nth_page(s)
            if self.parent.viewerbook.get_tab_label(ch).nm == self.nm_book:
                self.parent.viewerbook.set_current_page(s)
                self.parent.notebook.set_current_page(1)
                return
        sr = OpenBook(self.parent, self.book, self.id_book)
        self.parent.viewerbook.append_page(sr,TabLabel(sr, self.nm_book))
        self.parent.viewerbook.set_current_page(-1)
        self.parent.notebook.set_current_page(1)
        sr.set_index()
        sr.show_page(self.all_in_page[1])
    
    def stop_search(self, *a):
        self.stop_n = 0
        self.hb_stop.hide()
        
    def build(self, *a):
        Gtk.VPaned.__init__(self)
        vb = Gtk.VBox(False, 7)
        self.view_nasse = asm_customs.ViewClass()
        self.view_nasse_bfr = self.view_nasse.get_buffer()
        self.view_nasse.connect_after("populate-popup", asm_popup.populate_popup, self.parent)
        self.view_title_tag = self.view_nasse_bfr.create_tag("title")
        self.view_quran_tag = self.view_nasse_bfr.create_tag("quran")
        self.view_search_tag = self.view_nasse_bfr.create_tag("search")
        self.view_terms_tag = self.view_nasse_bfr.create_tag("terms")
        self.view_title_tag.set_property('foreground', self.parent.theme.color_tit) 
        self.view_title_tag.set_property('font', self.parent.theme.font_tit)
        self.view_quran_tag.set_property('foreground', self.parent.theme.color_qrn) 
        self.view_quran_tag.set_property("paragraph-background", self.parent.theme.color_bg_qrn)
        self.view_quran_tag.set_property('font', self.parent.theme.font_qrn)
        self.view_search_tag.set_property('background', self.parent.theme.color_fnd) 
        self.view_terms_tag.set_property('foreground', self.parent.theme.color_tit)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.view_nasse)
        self.pack1(scroll, True, False)
        hb = Gtk.HBox(False, 7)
        open_in_tab = Gtk.ToolButton(stock_id=Gtk.STOCK_FILE)
        open_in_tab.set_tooltip_text('افتح في لسان مستقل')
        open_in_tab.connect('clicked', self.open_new_tab)
        hb.pack_start(open_in_tab, False, False, 0)
        sav_result_btn = Gtk.ToolButton(stock_id=Gtk.STOCK_SAVE)
        hb.pack_start(sav_result_btn, False, False, 0)
        sav_result_btn.connect('clicked', self.sav_result_cb)
        self.sav_result_entry = Gtk.Entry()
        hb.pack_start(self.sav_result_entry, False, False, 0)
        self.search_result_btn = Gtk.ToolButton(stock_id=Gtk.STOCK_FIND)
        self.search_result_btn.set_tooltip_text('بحث في نتائج البحث')
        hb.pack_start(self.search_result_btn, False, False, 0)
        self.search_result_btn.connect('clicked', self.search_in_result)
        self.lab_n_result = Gtk.Label('عدد النتائج : 0')
        hb.pack_start(self.lab_n_result, False, False, 0)
        self.hb_stop = Gtk.HBox(False, 7)
        btn_stop = asm_customs.tool_button(join(asm_customs.ICON_DIR, u'stp.png'), 'أوقف عملية البحث', self.stop_search)
        self.hb_stop.pack_start(btn_stop, False, False, 0)
        self.progress = Gtk.ProgressBar()
        self.hb_stop.pack_start(self.progress, True, True, 0)
        hb.pack_start(self.hb_stop, True, True, 0)
        vb.pack_start(hb, False, False, 0)
        
        self.store_results = Gtk.ListStore(int,int,str,str,int,int, int)
        self.tree_results = asm_customs.TreeIndex()
        self.tree_results.set_model(self.store_results)
        self.sel_result = self.tree_results.get_selection()
        self.tree_results.connect("cursor-changed", self.show_result)
        self.tree_results.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        raq = Gtk.TreeViewColumn('الرقم', Gtk.CellRendererText(), text=1)
        raq.set_max_width(50)
        self.tree_results.append_column(raq)
        books = Gtk.TreeViewColumn('الكتاب', Gtk.CellRendererText(), text=2)
        self.tree_results.append_column(books)
        books.set_max_width(400)
        elbab = Gtk.TreeViewColumn('الباب', Gtk.CellRendererText(), text=3)
        self.tree_results.append_column(elbab)
        elbab.set_max_width(400)
        elbaher = Gtk.TreeViewColumn('الجزء', Gtk.CellRendererText(), text=4)
        self.tree_results.append_column(elbaher)
        elbaher.set_max_width(30)
        elgharadh = Gtk.TreeViewColumn('الصفحة', Gtk.CellRendererText(), text=5)
        self.tree_results.append_column(elgharadh)
        elgharadh.set_max_width(50)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_results)
        scroll.set_size_request(-1, 200)
        vb.pack_start(scroll, True, True, 0)
        self.pack2(vb, False, True)
        self.show_all()
        
# class نافذة البحث-------------------------------------------------------------------

class Searcher(Gtk.Dialog):
   
    def __init__(self, parent):
        self.parent = parent
        self.db = listDB()
        self.selected_books = []
        self.build()
   
    def load_books(self, *a):
        self.store_books.clear()
        groups = self.db.all_parts()
        for a in groups:
            aa = self.store_books.append(None, [None, a[1], a[0]])
            books = self.db.books_part(a[0])
            for b in books:
                self.store_books.append(aa, [None, b[1], b[0]])
    
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
                
    def deselect_all(self, *a):
        try: self.store_books.foreach(self.select_o, False)
        except: pass
        self.all_books.set_active(False)
        self.fav_books.set_active(False)
        
    def select_field(self, btn, *a):
        nm = btn.get_name()
        self.dict_field[nm] = btn.get_active()
           
    def select_perf(self, btn):
        nm = btn.get_name()
        self.dict_perf[nm] = btn.get_active()
    
    def fixed_toggled_field(self, cell, path, model):
        itr = model.get_iter((path),)
        fixed = model.get_value(itr, 0)
        fixed = not fixed
        model.set(itr, 0, fixed)
    
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
    
    def add_all_list(self,*a):
        for w in range(len(self.store_fields)):
            if self.store_fields[w][0] == True:
                nm_field = self.store_fields[w][1].decode('utf8')
                store = cPickle.load(file(join(asm_customs.MY_DIR, u'fields-search', nm_field+u'.pkl')))
                for a in store:
                    if a not in self.selected_books:
                        nm_book = a[0]
                        nm_group = a[1]
                        id_book = a[2]
                        self.selected_books.append([nm_book, nm_group, id_book])
        if self.fav_books.get_active() == True:
            list_fav = listDB().favorite_books()
            for a in list_fav:
                nm_book = a[1].decode('utf8')
                id_book = a[0]
                nm_group = listDB().group_book(a[0]).decode('utf8')
                if [nm_book, nm_group, id_book] not in self.selected_books:
                    self.selected_books.append([nm_book, nm_group, id_book])
        
    def add_to_listbooks(self, model, itr, fixed):
        nm_book = model.get_value(itr, 1).decode('utf8')
        id_book = model.get_value(itr, 2)
        i = model.iter_parent(itr)
        if i != None: 
            nm_group = model.get_value(i, 1).decode('utf8')
            if fixed: 
                if [nm_book, nm_group, id_book] not in self.selected_books:
                    self.selected_books.append([nm_book, nm_group, id_book])
            else:
                if [nm_book, nm_group, id_book] in self.selected_books:
                    self.selected_books.remove([nm_book, nm_group, id_book])
    
    def search(self, *a):
        self.add_all_list()
        text = self.entry_search.get_text().decode('utf8')
        if text == u'':
            asm_customs.erro(self.parent, 'أدخل النص المراد البحث عنه')
        elif self.selected_books == []:
            asm_customs.erro(self.parent, 'أنت لم تحدد أين ستبحث')
        else:
            try:
                if len(self.list_terms) == 50: self.list_terms.pop(0)
                if text in self.list_terms: self.list_terms.remove(text)
                self.list_terms.append(text)
                output = open(join(asm_customs.MY_DIR, u'data', u'last-terms.pkl'), 'wb')
                cPickle.dump(self.list_terms, output)
                output.close()
            except: pass
            self.hide()
            self.parent.notebook.set_current_page(1)
            sr = ShowResult(self.parent)
            self.parent.viewerbook.append_page(sr,TabLabel(sr, u'بحث عن :'+text))
            self.parent.viewerbook.set_current_page(-1)
            sr.search(text, self.dict_perf, self.dict_field, self.selected_books)
    
    # a دوال البحث في قائمة الكتب
    
    def search_in_index(self, model, path, i, my_books):
        txt = model.get(i,1)[0].decode('utf8')
        text, model0, path0, i0 = my_books
        if asm_araby.fuzzy(text) in asm_araby.fuzzy(txt) and path.compare(path0) > 0: 
            self.tree_books.expand_to_path(path)
            self.tree_books.scroll_to_cell(path)
            self.sel_books.select_path(path)
            return True 
        else:
            return False
    
    def search_entry(self, *a):
        text = self.ent_search.get_text().decode('utf8')
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
        text = self.ent_search.get_text().decode('utf8')
        if text == u'': return
        try: self.store_books.foreach(self.search_in_index, [text, model, path, i])
        except: pass
    
    def save_fields(self, *a):
        nm = self.ent_field.get_text().decode('utf8')
        output = open(join(asm_customs.MY_DIR, u'fields-search', nm+u'.pkl'), 'wb')
        cPickle.dump(self. selected_books, output)
        output.close()
        self.ent_field.set_text('')
        self.load_fields()
    
    def load_fields(self, *a):
        self.store_fields.clear()
        for a in os.listdir(join(asm_customs.MY_DIR, u'fields-search')):
            a = a.replace(u'.pkl', u'')
            self.store_fields.append([None, a])
        
    def build(self, *a):
        Gtk.Dialog.__init__(self, parent=self.parent)
        self.set_border_width(6)
        self.set_icon_name("asmaa")
        area = self.get_content_area()
        area.set_spacing(6)
        self.set_title("نافذة البحث")
        self.set_size_request(700,450)
        self.connect('delete-event', lambda w,*a: w.hide() or True)
        
        self.hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        vbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        frame = Gtk.Frame()
        frame.set_label('مجالات البحث.')
        box = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(6)
        self.dict_field = {'nass':True, 'tit':False}
        self.in_nasse = Gtk.RadioButton.new_with_label_from_widget(None, u'في النصوص')
        self.in_nasse.set_name('nass')
        box.pack_start(self.in_nasse, False, False, 0)
        self.in_nasse.connect('toggled', self.select_field, 1)
        self.in_title = Gtk.RadioButton.new_with_label_from_widget(self.in_nasse, u'في العناوين')
        self.in_title.set_name('tit')
        box.pack_start(self.in_title, False, False, 0)
        self.in_title.connect('toggled', self.select_field, 2)
        frame.add(box)
        vbox.pack_start(frame, False, False, 0)
             
        frame = Gtk.Frame()
        frame.set_label('خيارات البحث')
        box = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(6)
        self.dict_perf = {}
        for a in [[u'بدون لواصق', u'identical'],
        [u'عبارة متصلة', u'cursive'], 
        [u'إحدى الكلمات', u'one_term'],  
        [u'مع التشكيل', u'with_tachkil']]:
            btn = Gtk.CheckButton(a[0])
            btn.set_name(a[1])
            box.pack_start(btn, False, False, 0)
            btn.connect('toggled', self.select_perf)
            self.dict_perf[a[1]] = False
        frame.add(box)
        vbox.pack_start(frame, False, False, 0)
        self.hbox.pack_start(vbox, False, False, 0)
        
        vbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        try: self.ent_search = Gtk.SearchEntry()
        except: self.ent_search = Gtk.Entry()
        self.ent_search.set_placeholder_text('بحث عن كتاب')
        self.ent_search.connect('changed', self.search_entry)
        hbox.pack_end(self.ent_search, False, False, 0)
        search_btn = Gtk.ToolButton(stock_id=Gtk.STOCK_FIND)
        search_btn.connect('clicked', self.search_cb)
        search_btn.set_tooltip_text('ابحث عن النتيجة الموالية')
        hbox.pack_end(search_btn, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.store_books = Gtk.TreeStore(GObject.TYPE_BOOLEAN, GObject.TYPE_STRING, GObject.TYPE_INT)
        self.load_books()
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
        vbox.pack_start(scroll, True, True, 0)
        
        hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        col_all = asm_customs.ButtonClass(' ضم')
        col_all.set_tooltip_text('ضم الفهرس')
        def clo_all_cb(widget, *a):
            self.tree_books.collapse_all()
        col_all.connect('clicked', clo_all_cb)
        hbox.pack_start(col_all, False, False, 0)
        null_all = asm_customs.ButtonClass('إلغاء')
        null_all.set_tooltip_text('إلغاء تحديد جميع الكتب')
        null_all.connect('clicked', self.deselect_all)
        hbox.pack_start(null_all, False, False, 0)
        self.fav_books = Gtk.CheckButton('المفضلة')
        self.fav_books.connect('toggled', self.select_all) 
        hbox.pack_end(self.fav_books, False, False, 0)
        self.all_books = Gtk.CheckButton('الكل')
        self.all_books.connect('toggled', self.select_all) 
        hbox.pack_end(self.all_books, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.hbox.pack_start(vbox, True, True, 0)
        
        vbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        rm_field = Gtk.ToolButton(stock_id=Gtk.STOCK_CLEAR)
        rm_field.set_tooltip_text('حذف النطاق المحدد')
        hbox.pack_end(rm_field,False, False, 0)
        def rm_field_cb(widget, *a):
            model, i = self.tree_fields.get_selection().get_selected()
            if i:
                nm = model.get_value(i, 1).decode('utf8')
                os.remove(join(asm_customs.MY_DIR, u'fields-search', nm+'.pkl')) 
                model.remove(i)
        rm_field.connect('clicked', rm_field_cb)
        vbox.pack_start(hbox, False, False, 0)
        self.store_fields = Gtk.ListStore(GObject.TYPE_BOOLEAN, GObject.TYPE_STRING)
        self.load_fields()
        self.tree_fields = Gtk.TreeView(self.store_fields)
        self.tree_fields.set_rules_hint(True)
        celltext = Gtk.CellRendererText()
        celltoggle = Gtk.CellRendererToggle()
        celltoggle.set_property('activatable', True)
        columntoggle = Gtk.TreeViewColumn("اختر", celltoggle)
        columntext = Gtk.TreeViewColumn("النطاق", celltext, text = 1 )
        columntoggle.add_attribute( celltoggle, "active", 0)
        celltoggle.connect('toggled', self.fixed_toggled_field, self.store_fields)
        self.tree_fields.append_column(columntoggle)
        self.tree_fields.append_column(columntext)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_fields)
        vbox.pack_start(scroll,True, True, 0)
        
        hbox = Gtk.Box(spacing=7,orientation=Gtk.Orientation.HORIZONTAL)
        sav_field = Gtk.ToolButton(stock_id=Gtk.STOCK_SAVE)
        sav_field.set_tooltip_text("حفظ نطاق البحث المحدد حالياً")
        sav_field.connect('clicked', self.save_fields)
        hbox.pack_start(sav_field,False, False, 0)
        self.ent_field = Gtk.Entry()
        hbox.pack_start(self.ent_field,False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        self.hbox.pack_start(vbox, False, False, 0)
        
        
        area.pack_start(self.hbox, True, True, 0)
        hbox = Gtk.Box(spacing=10,orientation=Gtk.Orientation.HORIZONTAL)
        try: self.entry_search = Gtk.SearchEntry()
        except: self.entry_search = Gtk.Entry()
        try: self.list_terms = cPickle.load(file(join(asm_customs.MY_DIR, u'data', u'last-terms.pkl')))
        except: self.list_terms = []
        completion = Gtk.EntryCompletion()
        list_ts = Gtk.ListStore(str)
        for a in self.list_terms:
            list_ts.append([a])
        completion.set_model(list_ts)
        completion.set_text_column(0)
        self.entry_search.set_completion(completion)
        self.entry_search.set_placeholder_text('أدخل النص المراد البحث عنه')
        self.btn_search = asm_customs.ButtonClass('بحث')
        self.btn_search.connect('clicked', self.search)
        hbox.pack_start(self.btn_search, False, False, 0)
        hbox.pack_start(self.entry_search, True, True, 0)
        self.btn_close = asm_customs.ButtonClass('إغلاق')
        self.btn_close.connect('clicked', lambda *a: self.hide() or True)
        hbox.pack_end(self.btn_close, False, False, 0)
        area = self.get_content_area()
        area.pack_start(hbox, False, False, 0)
        area.set_spacing(6)
