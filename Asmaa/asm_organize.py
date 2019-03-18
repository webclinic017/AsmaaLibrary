# -*- coding: utf-8 -*-

#a############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
#a############################################################################

from os.path import join, exists
from subprocess import call
from os import mkdir, rename, listdir, unlink
from shutil import rmtree, copyfile
from asm_contacts import listDB
from gi.repository import Gtk
import asm_araby, asm_customs, asm_config
from asm_edit_bitaka import EditBitaka
from asm_edit_tafsir import EditTafsir
from asm_count import Count
from asm_edit_html import EditHTML

# class صفحة التعديل--------------------------------------------------

class Organize(Gtk.Box):
    
    def visible_cb(self, model, itr, data):
        if len(self.theword) == 0: return
        if asm_araby.fuzzy(self.theword[0]) in asm_araby.fuzzy(model.get_value(itr, 1).decode('utf8')):
            return True
        else: return False
        
    def search_cb(self, *a):
        self.theword = [self.search_book.get_text().decode('utf8')]
        self.modelfilter.refilter()
    
    def __init__(self, parent):
        self.parent = parent
        self.db = listDB()
        self.mycount = Count()
        self.size_font = int(self.parent.theme.font_nass[-2:])
        self.list_modifieds = []
        self .build()
    
    def add_to_favory(self, *a):
        model, i = self.sel_book.get_selected()
        if i:
            id_book = model.get_value(i, 0)
            nm_book = model.get_value(i, 1).decode('utf8')
            check = self.db.to_favorite(id_book)
            if check == None: 
                asm_customs.info(self.parent, u'تم إضافة كتاب "{}" للمفضلة'.format(nm_book,))
            self.parent.list_books.load_fav()
    
    def modify_data(self, *a):
        asm_customs.info(self.parent, 'تم تعديل البيانات بنجاح'); return
    
    def remove_group(self,*a):
        model, i = self.sel_group.get_selected()
        if i:
            id_group = model.get_value(i, 0)
            nm_group = model.get_value(i, 1).decode('utf8')
            msg = asm_customs.sure(self.parent, u'''
            سيتم حذف قسم "{}"
            مع جميع كتبه، هل تريد الاستمرار ؟
            '''.format(nm_group,))
            if msg == Gtk.ResponseType.YES:
                check = self.db.remove_group(id_group)
                if check == None:
                    rmtree(join(asm_customs.MY_DIR, u'books', nm_group))
                    self.refresh_groups()
       
    def remove_book(self,*a):
        model0, i0 = self.sel_group.get_selected()
        nm_group = model0.get_value(i0, 1).decode('utf8')
        model, i = self.sel_book.get_selected()
        if i:
            id_book = model.get_value(i, 0)
            nm_book = model.get_value(i, 1).decode('utf8')
            msg = asm_customs.sure(self.parent, u'''
            سيتم حذف كتاب "{}"
            هل تريد الاستمرار ؟
            '''.format(nm_book,))
            if msg == Gtk.ResponseType.YES:
                check = self.db.remove_book(id_book)
                if check == None:
                    unlink(join(asm_customs.MY_DIR, u'books', nm_group, nm_book+u'.asm'))
                    self.ok_group()
    
    def ok_book(self, *a):
        model, i = self.sel_book.get_selected()
        if i:
            nm_book = model.get_value(i, 1).decode('utf8')
            self.entry_book.set_text(nm_book)
            self.id_book = model.get_value(i, 0)
            self.notebk.set_current_page(1)
    
    def ok_group(self, *a):
        model, i = self.sel_group.get_selected()
        if i:
            id_group = model.get_value(i, 0)
            books = self.db.books_part(id_group)
            self.store_books.clear()
            self.names_list = []
            self.modelfilter = self.store_books.filter_new()
            for a in books:
                self.store_books.append([a[0], a[1]])
                self.names_list.append(a[1])
            self.theword = self.names_list[:]
            self.modelfilter.set_visible_func(self.visible_cb, self.theword) 
            self.tree_books.set_model(self.modelfilter)
            self.notebk.set_current_page(0)
    
    def merge_group_cb(self, *a):
        new_group = asm_customs.value_active(self.parts_g, 1)
        id_new = asm_customs.value_active(self.parts_g)
        if new_group == None: return
        new_group = new_group.decode('utf8')
        model, i = self.sel_group.get_selected()
        if i:
            id_old = model.get_value(i, 0)
            old_group = model.get_value(i, 1).decode('utf8')
            self.db.merge_group(id_old, id_new)
            for v in listdir(join(asm_customs.MY_DIR, u'books', old_group)):
                copyfile(join(asm_customs.MY_DIR, u'books', old_group, v), join(asm_customs.MY_DIR, u'books', new_group, v))
            rmtree(join(asm_customs.MY_DIR, u'books', old_group))
            self.refresh_groups()
    
    def move_book_cb(self, *a):
        new_group = asm_customs.value_active(self.parts_b, 1).decode('utf8')
        id_group = asm_customs.value_active(self.parts_b)
        model0, i0 = self.sel_group.get_selected()
        old_group = model0.get_value(i0, 1).decode('utf8')
        if new_group == None: return
        model, i = self.sel_book.get_selected()
        if i:
            id_book = model.get_value(i, 0)
            nm_book = model.get_value(i, 1).decode('utf8')
            self.db.change_group(id_book, id_group)
            copyfile(join(asm_customs.MY_DIR, u'books', old_group, nm_book+u'.asm'), 
                     join(asm_customs.MY_DIR, u'books', new_group, nm_book+u'.asm'))
            unlink(join(asm_customs.MY_DIR, u'books', old_group, nm_book+u'.asm'))
            asm_customs.info(self.parent, u'تم نقل الكتاب "{}" إلى قسم "{}"'.format(nm_book, new_group))
            self.ok_group()
      
    def refresh_groups(self, *a):
        self.store_group.clear()
        for a in self.db.all_parts():
            self.store_group.append([a[0], a[1]])
    
    def new_group(self, *a):
        new_grp = self.entry_group.get_text().decode('utf8')
        if new_grp == '': return
        if exists(join(asm_customs.MY_DIR, u'books', new_grp)): return
        check = self.db.add_part(new_grp)
        if check == None:
            mkdir(join(asm_customs.MY_DIR, u'books', new_grp))
            self.refresh_groups()
        self.entry_group.set_text('')
            
    def rename_group(self, *a):
        new_grp = self.entry_group.get_text().decode('utf8')
        if new_grp == '': return
        model, i = self.sel_group.get_selected()
        if i:
            nm_group = model.get_value(i, 1).decode('utf8')
        check = self.db.rename_part(new_grp, nm_group)
        if check == None:
            rename(join(asm_customs.MY_DIR, u'books', nm_group), join(asm_customs.MY_DIR, u'books', new_grp))
            self.refresh_groups()
    
    def move_group(self, btn, v):
        model, i = self.sel_group.get_selected()
        if i:
            if v == 1:
                i0 = model.iter_next(i)
                model.move_after(i, i0)
            if v == -1:
                i0 = model.iter_previous(i)
                model.move_before(i, i0)
        ls = []
        b = 0
        for a in self.store_group:
            b += 1
            ls.append([b, a[1].decode('utf8')])
        self.db.organiz_groups(ls)
      
    def rename_book(self, *a):
        model0, i0 = self.sel_group.get_selected()
        nm_group = model0.get_value(i0, 1).decode('utf8')
        model, i = self.sel_book.get_selected()
        if i:
            nm_book = model.get_value(i, 1).decode('utf8')
            new_bk = self.entry_book.get_text().decode('utf8')
            if new_bk == '' or new_bk == nm_book: return
            check = self.db.rename_book(new_bk, nm_book)
            self.db.rename_book_in_main(join(asm_customs.MY_DIR, u'books', nm_group, nm_book+u'.asm'), new_bk)
            if check == None:
                rename(join(asm_customs.MY_DIR, u'books', nm_group, nm_book+u'.asm'), 
                       join(asm_customs.MY_DIR, u'books', nm_group, new_bk+u'.asm'))
    
    def edit_tafsir_cb(self, *a):
        book = self.db.file_book(self.id_book)
        info = self.db.info_book(book)
        if info[8] != 1:
            msg = asm_customs.sure(self.parent, 'هذا الكتاب ليس تفسيرا هل تريد جعله كذلك')
            if msg == Gtk.ResponseType.NO:
                return
            else:
                self.db.make_tafsir(book, self.id_book)
        EditTafsir(self.parent, self.id_book)
    
    def editbk_cb(self, *a):
        self.parent.editbook.close_db()
        self.parent.notebook.set_current_page(8)
        book = self.db.file_book(self.id_book)
        self.parent.editbook.add_book(book, self.id_book, 1)
    
    def empty_book_cb(self, *a):
        model, i = self.sel_group.get_selected()
        if i:
            nm_group = model.get_value(i, 1).decode('utf8')
            id_part = model.get_value(i, 0)
            new_bk = self.entry_group.get_text().decode('utf8')
            if new_bk == '' :
                asm_customs.erro(self.parent, 'أدخل اسم الكتاب أولا')
                return
            db = join(asm_customs.MY_DIR, u'books', nm_group, new_bk+u'.asm')
            if exists(db):
                asm_customs.erro(self.parent, 'يوجد كتاب بنفس الاسم')
                return
            self.db.empty_book(db)
            self.db.add_book(new_bk, id_part)
            asm_customs.info(self.parent, 'تم إضافة كتاب فارغ')
        
    def count_cb(self, *a):
        n_group = len(self.db.all_parts())
        n_book = self.db.n_books()
        asm_config.setv('n_group', n_group)
        asm_config.setv('n_book', n_book)
        self.n_group.set_text('عدد الأقسام : {}'.format(n_group))
        self.n_book.set_text('عدد الكتب : {}'.format(n_book)) 
    
    def open_file(self, *a):
        hb = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        box = Gtk.Box(spacing=5,orientation=Gtk.Orientation.VERTICAL)
        dlg = Gtk.Dialog(parent=self.parent)
        dlg.set_icon_name("asmaa")
        dlg.set_default_size(1000, 700)
        area = dlg.get_content_area()
        area.set_spacing(6)
        dlg.set_title('إحصاء الكتب')
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        self.view_html = EditHTML()
        self.view_html.open_html(self.file_html)
        close_btn = asm_customs.ButtonClass("إغلاق")
        close_btn.connect('clicked',lambda *a: dlg.destroy())
        hb.pack_end(close_btn, False, False, 0)
        box.pack_start(self.view_html, True, True, 0)
        box.pack_start(hb, False, False, 0)
        area.pack_start(box, True, True, 0)
        dlg.show_all()
    
    def count_fast(self, *a):
        self.file_html = self.mycount.fast()
        self.open_file()
        
    def count_detail(self, *a):
        self.file_html = self.mycount.detail()
        self.open_file()
        
    def build(self,*a): 
        Gtk.Box.__init__(self,spacing=7,orientation=Gtk.Orientation.VERTICAL)
        hp1 = Gtk.HPaned()
        self.pack_start(hp1, True, True, 0)
        self.tree_group = asm_customs.TreeClass()
        self.sel_group = self.tree_group.get_selection()
        self.tree_group.connect("cursor-changed", self.ok_group)
        cell = Gtk.CellRendererText()
        cell.set_property("wrap-width", 200)
        kal = Gtk.TreeViewColumn('الأقسام', cell, text=1)
        self.tree_group.append_column(kal)
        self.store_group = Gtk.ListStore(int, str)
        self.tree_group.set_model(self.store_group)
        self.refresh_groups()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_group)
        scroll.set_size_request(150, -1)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        hp1.pack1(scroll, False, False)
        
        hp2 = Gtk.HPaned()
        hp1.pack2(hp2, True, True)
        vb = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        self.store_books = Gtk.ListStore(int, str)
        self.tree_books = asm_customs.TreeIndex()
        self.tree_books.connect("cursor-changed", self.ok_book)
        self.sel_book = self.tree_books.get_selection()
        self.tree_books.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        books = Gtk.TreeViewColumn('الكتب', Gtk.CellRendererText(), text=1)
        self.tree_books.append_column(books)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_books)
        scroll.set_size_request(250, -1)
        vb.pack_start(scroll, True, True, 0)
        try: self.search_book = Gtk.SearchEntry()
        except: self.search_book = Gtk.Entry()
        self.search_book.set_placeholder_text('بحث عن كتاب')
        self.search_book.connect('changed', self.search_cb)
        vb.pack_start(self.search_book, False, False, 0)
        hp2.pack1(vb, False, False)
        
        ls = []
        for a in self.db.all_parts():
            ls.append([a[0], a[1]])
            
        self.notebk = Gtk.Notebook()
        self.notebk.set_show_tabs(False)
        vb = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        self.entry_group = Gtk.Entry()
        self.entry_group.set_placeholder_text('أدخل اسما!')
        vb.pack_start(self.entry_group, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_new_g = asm_customs.ButtonClass('قسم جديد')
        btn_new_g.connect('clicked', self.new_group)
        hb.pack_start(btn_new_g, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_rn_g = asm_customs.ButtonClass('تغيير اسم')
        btn_rn_g.connect('clicked', self.rename_group)
        hb.pack_start(btn_rn_g, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_rm_g = asm_customs.ButtonClass('حذف قسم')
        btn_rm_g.connect('clicked', self.remove_group)
        hb.pack_start(btn_rm_g, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_up_g = asm_customs.ButtonClass('حرك لأعلى')
        btn_up_g.connect('clicked', self.move_group, -1)
        hb.pack_start(btn_up_g, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_down_g = asm_customs.ButtonClass('حرك لأسفل')
        btn_down_g.connect('clicked', self.move_group, 1)
        hb.pack_start(btn_down_g, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 7)
        btn_merge_g = asm_customs.ButtonClass('دمج قسم')
        btn_merge_g.connect('clicked', self.merge_group_cb)
        hb.pack_start(btn_merge_g, False, False, 0)
        hb0, self.parts_g = asm_customs.combo(ls, u' إلى :', 0)
        hb.pack_start(hb0, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_empty_book = asm_customs.ButtonClass('كتاب فارغ')
        btn_empty_book.connect('clicked', self.empty_book_cb)
        hb.pack_start(btn_empty_book, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        self.notebk.append_page(vb, Gtk.Label('القسم'))
        
        vb = Gtk.Box(spacing=7,orientation=Gtk.Orientation.VERTICAL)
        self.entry_book = Gtk.Entry()
        self.entry_book.set_placeholder_text('أدخل اسما!')
        vb.pack_start(self.entry_book, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_rn_b = asm_customs.ButtonClass('تغيير اسم')
        btn_rn_b.connect('clicked', self.rename_book)
        hb.pack_start(btn_rn_b, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_rm_b = asm_customs.ButtonClass('حذف كتاب')
        btn_rm_b.connect('clicked', self.remove_book)
        hb.pack_start(btn_rm_b, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 0)
        btn_fav_b = asm_customs.ButtonClass('تفضيل كتاب')
        btn_fav_b.connect('clicked', self.add_to_favory)
        hb.pack_start(btn_fav_b, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 7)
        btn_mov = asm_customs.ButtonClass('نقل كتاب')
        btn_mov.connect('clicked', self.move_book_cb)
        hb.pack_start(btn_mov, False, False, 0)
        hb0, self.parts_b = asm_customs.combo(ls, u' إلى :', 0)
        hb.pack_start(hb0, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 7)
        btn_info = asm_customs.ButtonClass('بطاقة كتاب')
        btn_info.connect('clicked', lambda *a: EditBitaka(self.parent, self.id_book))
        hb.pack_start(btn_info, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 7)
        btn_edit = asm_customs.ButtonClass('تحرير كتاب')
        btn_edit.connect('clicked', self.editbk_cb)
        hb.pack_start(btn_edit, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        hb = Gtk.Box(False, 7)
        btn_tafsir = asm_customs.ButtonClass('تحرير تفسير')
        btn_tafsir.connect('clicked', self.edit_tafsir_cb)
        hb.pack_start(btn_tafsir, False, False, 0)
        vb.pack_start(hb, False, False, 0)
        self.notebk.append_page(vb, Gtk.Label('الكتاب'))
        hp2.pack2(self.notebk, True, True)
        
        hbox = Gtk.Box(spacing=6,orientation=Gtk.Orientation.HORIZONTAL)
        self.rapid_count = asm_customs.ButtonClass('إحصاء سريع')
        self.rapid_count.connect('clicked', self.count_fast)
        self.rapid_count.connect('clicked', self.count_cb)
        self.detail_count = asm_customs.ButtonClass('إحصاء مفصل')
        self.detail_count.connect('clicked', self.count_detail)
        hbox.pack_start(self.rapid_count, False, False, 0)
        hbox.pack_start(self.detail_count, False, False, 0)
        self.n_group = Gtk.Label('- عدد الأقسام : {}'.format(asm_config.getn('n_group')))
        hbox.pack_start(self.n_group, False, False, 0)
        self.n_book = Gtk.Label('،   - عدد الكتب : {}'.format(asm_config.getn('n_book')))
        hbox.pack_start(self.n_book, False, False, 0)
        self.pack_start(hbox, False, False, 0)
        self.show_all()
        