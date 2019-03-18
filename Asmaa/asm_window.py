# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
##############################################################################

import asm_customs
from gi.repository import Gtk, Gdk
from os.path import join
from asm_contacts import listDB
from asm_about import About
from asm_viewer import ViewerBooks, OpenBook
from asm_listbook import ListBooks
from asm_dict import Explanatory
from asm_tafsir import Tafsir
from asm_tarjama import Tarjama
from asm_marks import SavedMarks
from asm_result import SavedResult
from asm_search import Searcher
from asm_preference import Preference
from asm_organize import Organize
from asm_add import AddBooks
from asm_waraka import Warakat
import asm_config
from asm_theme import MyTheme
from asm_moshaf import ViewerMoshaf
from asm_tablabel import TabLabel
from asm_edit_book import EditBook
from asm_author import Author

Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL)


class AsmaaApp(Gtk.Window): 
    
    ACCEL_CTRL_KEY, ACCEL_CTRL_MOD = Gtk.accelerator_parse("<Ctrl>")
    ACCEL_SHFT_KEY, ACCEL_SHFT_MOD = Gtk.accelerator_parse("<Shift>")
    ACCEL_ALT_KEY, ACCEL_ALT_MOD = Gtk.accelerator_parse("<Alt>")
    
    def __init__(self, *a):
        Gtk.Window.__init__(self)
        self.notebook = Gtk.Notebook()
        self.theme = MyTheme()
        self.db = listDB()
        self.opened = [0]
        self.axl = Gtk.AccelGroup()
        self.add_accel_group(self.axl)
        self.search_win = Searcher(self)
        self.list_books = ListBooks(self)
        self.theme = MyTheme()
        self.viewerbook = ViewerBooks(self)
        self.tafsirpage = Tafsir(self)
        self.organizepage = Organize(self)
        self.warakapage = Warakat(self)
        self.editbook = EditBook(self)
        self.help_book = OpenBook(self, join(asm_customs.MY_DATA, 'Dalil.db'), -1)
        self.help_book.editbk.set_sensitive(False)
        self.help_book.comment_btn.set_sensitive(False)
        self.help_book.set_index()
        self.moshafpage = ViewerMoshaf(self)
        #-------------------------------
        self.winspage = Gtk.Notebook()
        self.dictpage = Explanatory(self)
        self.tarjamapage = Tarjama(self)
        self.authorpage = Author(self)
        self.winspage.append_page(self.dictpage, Gtk.Label('مختار الصحاح'))
        self.winspage.append_page(self.tarjamapage, Gtk.Label('رواة التهذيبين'))
        self.winspage.append_page(self.authorpage, Gtk.Label('تراجم المؤلفين'))
        self.build()
        
    
    def show_bitaka(self, *a):
        hb = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        box = Gtk.Box(spacing=5,orientation=Gtk.Orientation.VERTICAL)
        n = self.notebook.get_current_page()
        if n not in [1, 2, 4, 5, 8]: return
        ch = self.notebook.get_nth_page(n)
        bitaka_book = ch.show_bitaka()[3]
        info_book = ch.show_bitaka()[4]
        dlg = Gtk.Dialog(parent=self)
        dlg.set_icon_name("asmaa")
        dlg.set_default_size(280, 300)
        area = dlg.get_content_area()
        area.set_spacing(6)
        dlg.set_title('بطاقة الكتاب')
        view_info = asm_customs.ViewBitaka()
        view_info_bfr = view_info.get_buffer()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(view_info)
        view_info_bfr.set_text(bitaka_book)
        
        info_btn = asm_customs.ButtonClass("نبذة")
        def info_cb(w):
            if w.get_label().decode('utf8') == u"نبذة":
                view_info_bfr.set_text(info_book)
                w.set_label('بطاقة')
            else:
                view_info_bfr.set_text(bitaka_book)
                w.set_label('نبذة')
        info_btn.connect('clicked', info_cb)
        hb.pack_start(info_btn, False, False, 0)
        
        close_btn = asm_customs.ButtonClass("إغلاق")
        close_btn.connect('clicked',lambda *a: dlg.destroy())
        hb.pack_end(close_btn, False, False, 0)
        box.pack_start(scroll, True, True, 0)
        box.pack_start(hb, False, False, 0)
        area.pack_start(box, True, True, 0)
        dlg.show_all()
        
        
    def listbook_show(self, *a):
        self.notebook.set_current_page(0)
   
    def back_to_previous_page(self, *a):
        if len(self.opened) == 1: return
        del self.opened[-1]
        if self.opened[-1] == 8: 
            del self.opened[-1]
        self.notebook.set_current_page(self.opened[-1])
   
    def back_to_old(self, *a):
        n = self.notebook.get_current_page()
        if n not in [1, 2, 4, 5, 8]: return
        ch = self.notebook.get_nth_page(n)
        ch.back_to_old()
        
    def advance_to_new(self, *a):
        n = self.notebook.get_current_page()
        if n not in [1, 2, 4, 5, 8]: return
        ch = self.notebook.get_nth_page(n)
        ch.advance_to_new()
   
    def switch_page(self, widget, page, n):
        if n != self.opened[-1]: self.opened.append(n)
    
    # a التصفح--------------------------------------------

    def first_page(self, *a):
        n = self.notebook.get_current_page()
        if n not in [1, 2, 4, 5, 8]: return
        ch = self.notebook.get_nth_page(n)
        ch.first_page()
    
    def previous_page(self, *a):
        n = self.notebook.get_current_page()
        if n not in [1, 2, 4, 5, 8]: return
        ch = self.notebook.get_nth_page(n)
        ch.previous_page()
    
    def next_page(self, *a):
        n = self.notebook.get_current_page()
        if n not in [1, 2, 4, 5, 8]: return
        ch = self.notebook.get_nth_page(n)
        ch.next_page()
    
    def last_page(self, *a):
        n = self.notebook.get_current_page()
        if n not in [1, 2, 4, 5, 8]: return
        ch = self.notebook.get_nth_page(n)
        ch.last_page()
    
    def opened_book(self, *a):
        if self.viewerbook.get_n_pages() == 0:
            return
        else:
            self.notebook.set_current_page(1)
    
    def full_screen(self, *a):
        if self.full == 1:
            self.unfullscreen()
            self.full = 0
        else:
            self.fullscreen()
            self.full = 1
    
    def delete_event_cb(self, *a):
        asm_config.setv('quran_pos', self.moshafpage.page_id)
        session = []
        session.append(self.viewerbook.session)
        saved = repr(session)
        asm_config.setv('start_session', saved)
        n = self.viewerbook.get_n_pages()
        for a in range(n):
            ch = self.viewerbook.get_nth_page(a)
            try: ch.db_list.set_last(ch.all_in_page[1], ch.id_book)
            except: pass
        Gtk.main_quit()
        
    def start_session(self, *a):
        session = eval(asm_config.getv('start_session'))
        if asm_config.getn('saved_session') == 0: return
        if session[0] == []: return
        for id_book in session[0][0]:
            book = self.db.file_book(id_book)
            sr = OpenBook(self, book, id_book)
            self.viewerbook.append_page(sr,TabLabel(sr, self.db.tit_book(id_book)[1]))
            self.opened_book()
            sr.set_index()
        self.viewerbook.set_current_page(session[0][1])
        if session[1][-1] in [0, 1, 2, 4]:
            self.notebook.set_current_page(session[1][-1][0])
        else:
            self.notebook.set_current_page(session[1][-2][0])
    
    def show_menu(self, *a):
        self.menu_wins.show_all()
        self.menu_wins.popup(None, None, None, None, 3, 
                            Gtk.get_current_event_time())
            
    def build(self, *a):
        self.full = 0
        self.set_border_width(3)
        self.resize(1080, 600)
        self.maximize()
        self.set_icon_name("asmaa")
        self.connect("delete_event", self.delete_event_cb)
        self.set_title('مكتبة أسماء')
        self.vbox = Gtk.VBox(False, 3)
        
        # a شريط الأدوات------------------------------------------
        self.toolbar = Gtk.Toolbar()

        wins = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Windows-32.png'), "الرجوع إلى النافذة السابقة", 
                                              self.show_menu)
        self.menu_wins = Gtk.Menu()      
        win_quran = Gtk.ImageMenuItem("القرآن الكريم")
        img = Gtk.Image()
        img.set_from_file(join(asm_customs.ICON_DIR, 'Quran-16.png'))
        win_quran.set_image(img)
        win_quran.connect('activate', lambda *a: self.notebook.set_current_page(2))
        win_tafsir = Gtk.ImageMenuItem("التفاسير")
        img = Gtk.Image()
        img.set_from_file(join(asm_customs.ICON_DIR, 'Tafsir-16.png'))
        win_tafsir.set_image(img)
        win_tafsir.connect('activate', lambda *a: self.notebook.set_current_page(4))
        win_list = Gtk.ImageMenuItem("قائمة الكتب")
        img = Gtk.Image()
        img.set_from_file(join(asm_customs.ICON_DIR, 'Books-16.png'))
        win_list.set_image(img)
        win_list.connect('activate', lambda *a: self.notebook.set_current_page(0))
        win_opened = Gtk.ImageMenuItem("الكتب المفتوحة")
        img = Gtk.Image()
        img.set_from_file(join(asm_customs.ICON_DIR, 'Book-Open-16.png'))
        win_opened.set_image(img)
        win_opened.connect('activate', self.opened_book)
        win_waraka = Gtk.ImageMenuItem("أوراق البحث")
        img = Gtk.Image()
        img.set_from_file(join(asm_customs.ICON_DIR, 'Papers-16.png'))
        win_waraka.set_image(img)
        win_waraka.connect('activate', lambda *a: self.notebook.set_current_page(6))
        win_special = Gtk.ImageMenuItem("نوافذ خاصة")
        img = Gtk.Image()
        img.set_from_file(join(asm_customs.ICON_DIR, 'Wins-16.png'))
        win_special.set_image(img)
        win_special.connect('activate', lambda *a: self.notebook.set_current_page(3))
        win_help = Gtk.ImageMenuItem("صفحة المساعدة")
        img = Gtk.Image()
        img.set_from_file(join(asm_customs.ICON_DIR, 'Help-16.png'))
        win_help.set_image(img)
        win_help.connect('activate', lambda *a: self.notebook.set_current_page(5))
        exit1 = Gtk.ImageMenuItem("خروج")
        img = Gtk.Image()
        img.set_from_file(join(asm_customs.ICON_DIR, 'exit-16.png'))
        exit1.set_image(img)
        exit1.connect('activate', Gtk.main_quit)
        self.menu_wins.append(win_quran)
        self.menu_wins.append(win_tafsir)
        self.menu_wins.append(win_list)
        self.menu_wins.append(win_opened)
        self.menu_wins.append(win_waraka)
        self.menu_wins.append(win_special)
        self.menu_wins.append(win_help)
        self.menu_wins.append(Gtk.SeparatorMenuItem())
        self.menu_wins.append(exit1)
        self.toolbar.insert(wins, 0)
        
        self.browse_page = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'browse.png'), "الرجوع إلى النافذة السابقة", 
                                              self.back_to_previous_page)
        self.toolbar.insert(self.browse_page, 1)
        self.toolbar.insert(Gtk.SeparatorToolItem(), 2)
        
        self.Quran = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Quran-32.png'), "المصحف الشريف", 
                                             lambda *a: self.notebook.set_current_page(2))
        self.toolbar.insert(self.Quran, 3)
        self.Tafsir = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Tafsir-32.png'), "صفحة التفاسير", 
                                             lambda *a: self.notebook.set_current_page(4))
        self.toolbar.insert(self.Tafsir, 4)
        self.Books = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Books-32.png'), "قائمة الكتب", 
                                             lambda *a: self.notebook.set_current_page(0))
        self.Books.add_accelerator("clicked",self.axl, Gdk.KEY_Right, self.ACCEL_CTRL_MOD, Gtk.AccelFlags.VISIBLE)
        self.toolbar.insert(self.Books, 5)
        self.Book_open = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Book-Open-32.png'), 
                                     "الكتب ونتائج البحث المفتوحة", self.opened_book)
        self.toolbar.insert(self.Book_open, 6)
        self.Papers = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Papers-32.png'), "أوراق البحث", 
                                              lambda *a: self.notebook.set_current_page(6))
        self.toolbar.insert(self.Papers, 7)
        self.Wins = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Wins-32.png'), "نوافذ خاصة", 
                                              lambda *a: self.notebook.set_current_page(3))
        self.toolbar.insert(self.Wins, 8)
        
        self.toolbar.insert(Gtk.SeparatorToolItem(), 9)

        self.Books_Saved = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Books-Saved-32.png'), 
                                                   "العلامات المرجعية", lambda *a: SavedMarks(self))
        self.toolbar.insert(self.Books_Saved, 10)
        self.Saved_Result = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Saved-Result-32.png'), 
                                                    "النتائج المحفوظة", lambda *a: SavedResult(self))
        self.toolbar.insert(self.Saved_Result, 11)
        self.toolbar.insert(Gtk.SeparatorToolItem(), 12)
        
        self.First = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'First-32.png'), "الصفحة الأولى", 
                                             self.first_page)
        self.toolbar.insert(self.First, 13)
        self.Previous = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Previous-32.png'), "الصفحة السابقة", 
                                                self.previous_page)
        self.toolbar.insert(self.Previous, 14)
        self.Next = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Next-32.png'), "الصفحة التالية", 
                                            self.next_page)
        self.toolbar.insert(self.Next, 15)
        self.Last = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Last-32.png'), "الصفحة الأخيرة", 
                                            self.last_page)
        self.toolbar.insert(self.Last, 16)
        
        self.toolbar.insert(Gtk.SeparatorToolItem(), 17)
        
        self.Undo = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'undo-32.png'), "تراجع إلى التصفح الأقدم", 
                                            self.back_to_old)
        self.toolbar.insert(self.Undo, 18)
        self.Redo = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'redo-32.png'), "تقدم إلى التصفح الأحدث", 
                                            self.advance_to_new)
        self.toolbar.insert(self.Redo, 19)
        
        self.toolbar.insert(Gtk.SeparatorToolItem(), 20)
        
        self.Search_Books = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Search-Books-32.png'), 
                                                    "البحث في المكتبة", lambda *a: self.search_win.show_all())
        self.toolbar.insert(self.Search_Books, 21)
        self.Organiz = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Configs-32.png'), "تنظيم المكتبة", 
                                               lambda *a: self.notebook.set_current_page(7))
        self.toolbar.insert(self.Organiz, 22)
        
        self.toolbar.insert(Gtk.SeparatorToolItem(), 23)

        self.Chamila = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Chamila-32.png'), "إضافة الكتب", 
                                               lambda *a: AddBooks(self))
        self.toolbar.insert(self.Chamila, 24)
        self.Prefers = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Prefers-32.png'), "التفضيلات", 
                                               lambda *a: Preference(self))
        self.toolbar.insert(self.Prefers, 25)
        
        self.toolbar.insert(Gtk.SeparatorToolItem(), 26)
        
        self.Bitaka = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Bitaka-32.png'), "بطاقة الكتاب", 
                                              self.show_bitaka)
        self.toolbar.insert(self.Bitaka, 27)
        self.Help = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'Help-32.png'), "دليل المستخدم", 
                                            lambda *a: self.notebook.set_current_page(5))
        self.toolbar.insert(self.Help, 28)
        self.About = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'About-32.png'), "لمحة عن المكتبة", 
                                             lambda *a: About(self))
        self.toolbar.insert(self.About, 29)
        self.toolbar.insert(Gtk.SeparatorToolItem(), 30)
        
        self.Exit = asm_customs.tool_button(join(asm_customs.ICON_DIR, 'exit-32.png'), "الخروج من المكتبة", 
                                            self.delete_event_cb)
        self.toolbar.insert(self.Exit, 31)
           
        # a--------------------------------
        self.notebook.set_show_tabs(False)
        self.notebook.append_page(self.list_books, Gtk.Label('0'))
        self.notebook.append_page(self.viewerbook, Gtk.Label('1'))
        self.notebook.append_page(self.moshafpage, Gtk.Label('2'))
        self.notebook.append_page(self.winspage, Gtk.Label('3'))
        self.notebook.append_page(self.tafsirpage, Gtk.Label('4'))
        self.notebook.append_page(self.help_book, Gtk.Label('5'))
        self.notebook.append_page(self.warakapage, Gtk.Label('6'))
        self.notebook.append_page(self.organizepage, Gtk.Label('7'))
        self.notebook.append_page(self.editbook, Gtk.Label('8'))
        self.notebook.connect("switch-page", self.switch_page)
        
        self.axl.connect(Gdk.KEY_Right, self.ACCEL_ALT_MOD, Gtk.AccelFlags.VISIBLE, self.previous_page)
        self.axl.connect(Gdk.KEY_Left, self.ACCEL_ALT_MOD, Gtk.AccelFlags.VISIBLE, self.next_page)
        self.axl.connect(Gdk.KEY_Up, self.ACCEL_ALT_MOD, Gtk.AccelFlags.VISIBLE, self.first_page)
        self.axl.connect(Gdk.KEY_Down, self.ACCEL_ALT_MOD, Gtk.AccelFlags.VISIBLE, self.last_page)
        self.axl.connect(Gdk.KEY_F1, 0, Gtk.AccelFlags.VISIBLE, lambda *a: self.notebook.set_current_page(6))
        self.axl.connect(Gdk.KEY_F12, 0, Gtk.AccelFlags.VISIBLE, lambda *a: self.notebook.set_current_page(0))
        self.axl.connect(Gdk.KEY_F7, 0, Gtk.AccelFlags.VISIBLE, lambda *a: self.notebook.set_current_page(2))
        self.axl.connect(Gdk.KEY_F9, 0, Gtk.AccelFlags.VISIBLE, self.viewerbook.hide_index)
        self.axl.connect(Gdk.KEY_F11, 0, Gtk.AccelFlags.VISIBLE, self.full_screen)
        self.axl.connect(Gdk.KEY_F6, 0, Gtk.AccelFlags.VISIBLE, lambda *a: self.search_win.show_all())
        self.axl.connect(Gdk.KEY_F8, 0, Gtk.AccelFlags.VISIBLE, lambda *a: Preference(self))
        self.axl.connect(Gdk.KEY_BackSpace, self.ACCEL_CTRL_MOD, Gtk.AccelFlags.VISIBLE, self.back_to_previous_page)
        
        self.vbox.pack_start(self.toolbar, False, False, 0)
        self.vbox.pack_start(Gtk.Separator(), False, False, 0)
        self.vbox.pack_start(self.notebook, True, True, 0)
        self.add(self.vbox)
        self.show_all()
        self.help_book.scroll_search.hide()
        asm_customs.greet.destroy()
        try: self.start_session()
        except: pass

#----------------------------------------------------

asm = AsmaaApp()   
def main(): 
    Gtk.main()

if __name__ == "__main__":
    main()
