# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
##############################################################################

from gi.repository import Gtk
import asm_customs
from asm_contacts import bookDB, listDB

class EditBitaka(Gtk.Dialog):
    
    def quit_dlg(self, *a):
        self.destroy()
        self.db.close_db()
        del self.db
    
    def save_cb(self, *a):
        txt_bitaka = self.view_bitaka_bfr.get_text(self.view_bitaka_bfr.get_start_iter(),
                            self.view_bitaka_bfr.get_end_iter(), False).decode('utf8')
        txt_info = self.view_info_bfr.get_text(self.view_info_bfr.get_start_iter(),
                            self.view_info_bfr.get_end_iter(), False).decode('utf8')
        name = self.ent_name.get_text().decode('utf8')
        short_name = self.ent_name_sh.get_text().decode('utf8')
        self.db.save_info(name, short_name, txt_bitaka, txt_info)
        asm_customs.info(self.parent, 'تم حفظ المعلومات الجديدة')
    
    def __init__(self, parent, id_book):
        self.parent = parent
        book = listDB().file_book(id_book)
        self.db = bookDB(book, id_book)
        Gtk.Dialog.__init__(self, parent=self.parent)
        self.set_icon_name("asmaa")
        self.connect('destroy', self.quit_dlg)
        area = self.get_content_area()
        area.set_spacing(5)
        self.set_border_width(5)
        self.set_title('تعديل معلومات الكتاب')
        self.set_default_size(500, 600)
        box = Gtk.Box(spacing=6,orientation=Gtk.Orientation.VERTICAL)
        
        hbox = Gtk.HBox(False, 3)
        self.n_n = Gtk.Label('اسم الكتاب')
        hbox.pack_start(self.n_n, False, False, 0) 
        self.ent_name = Gtk.Entry()
        self.ent_name.set_text(self.db.info_book()[0])
        hbox.pack_start(self.ent_name, True, True, 0)
        box.pack_start(hbox, False, False, 0)
        
        hbox = Gtk.HBox(False, 3)
        self.n_ns = Gtk.Label('اسم مختصر')
        hbox.pack_start(self.n_ns, False, False, 0) 
        self.ent_name_sh = Gtk.Entry()
        self.ent_name_sh.set_text(self.db.info_book()[1])
        hbox.pack_start(self.ent_name_sh, True, True, 0)
        box.pack_start(hbox, False, False, 0)
        
        box.pack_start(Gtk.HSeparator(), False, False, 0)
        
        self.view_bitaka = Gtk.TextView()
        self.view_bitaka.set_wrap_mode(Gtk.WrapMode.WORD)
        self.view_bitaka.set_right_margin(5)
        self.view_bitaka.set_left_margin(5)
        self.view_bitaka_bfr = self.view_bitaka.get_buffer()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.view_bitaka)
        self.bitaka_book = self.db.info_book()[3]
        self.view_bitaka_bfr.set_text(self.bitaka_book)
        hbox = Gtk.HBox(False, 3)
        hbox.pack_start(Gtk.Label('بطاقة الكتاب'), False, False, 0)
        sample_btn = Gtk.ToggleButton("عينة")
        def sample_cb(w):
            if sample_btn.get_active():
                self.bitaka_book = self.view_bitaka_bfr.get_text(self.view_bitaka_bfr.get_start_iter(),
                            self.view_bitaka_bfr.get_end_iter(), False).decode('utf8')
                self.view_bitaka_bfr.set_text('اسم الكتاب :\nالمؤلف :\nالناشر :\nالطبعة :\n\
التحقيق :\nعدد الأجزاء :\nمصدر الكتاب :\nترقيم الكتاب :')
            else:
                self.view_bitaka_bfr.set_text(self.bitaka_book)
        sample_btn.connect('toggled', sample_cb)
        hbox.pack_end(sample_btn, False, False, 0)
        box.pack_start(hbox, False, False, 0)
        box.pack_start(scroll, True, True, 0)
        
        self.view_info = Gtk.TextView()
        self.view_info.set_wrap_mode(Gtk.WrapMode.WORD)
        self.view_info.set_right_margin(5)
        self.view_info.set_left_margin(5)
        self.view_info_bfr = self.view_info.get_buffer()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.view_info)
        self.info_book = self.db.info_book()[4]
        self.view_info_bfr.set_text(self.info_book)
        hbox = Gtk.HBox(False, 3)
        hbox.pack_start(Gtk.Label('نبذة عن الكتاب'), False, False, 0)
        sample_btn1 = Gtk.ToggleButton("عينة")
        def sample_cb1(w):
            if sample_btn1.get_active():
                self.info_book = self.view_info_bfr.get_text(self.view_info_bfr.get_start_iter(),
                            self.view_info_bfr.get_end_iter(), False).decode('utf8')
                self.view_info_bfr.set_text('موضوع الكتاب\nسبب التأليف\nمكانة الكتاب العلمية\nكلام العلماء في تقريضه')
            else:
                self.view_info_bfr.set_text(self.info_book)
        sample_btn1.connect('toggled', sample_cb1)
        hbox.pack_end(sample_btn1, False, False, 0)
        box.pack_start(hbox, False, False, 0)
        box.pack_start(scroll, True, True, 0)
        
        hbox = Gtk.Box(spacing=5,orientation=Gtk.Orientation.HORIZONTAL)
        save_btn = asm_customs.ButtonClass("حفظ")
        save_btn.connect('clicked', self.save_cb)
        hbox.pack_start(save_btn, False, False, 0)
        clo = asm_customs.ButtonClass("إغلاق")
        clo.connect('clicked', self.quit_dlg)
        hbox.pack_end(clo, False, False, 0)
        box.pack_start(hbox, False, False, 0)
        
        area.pack_start(box, True, True, 0)
        self.show_all()