# -*- coding: utf-8 -*-

#a############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  #########
#a############################################################################

from os.path import join
import os
from asm_contacts import listDB
from gi.repository import Gtk
import asm_config, asm_customs


# class نافذة التفضيلات----------------------------------------------------------       
        
class Preference(Gtk.Dialog):
    
    def __init__(self, parent):
        self.parent = parent
        self.db = listDB()
        self.build()        
    
    def refresh(self, *a):
        n = self.parent.viewerbook.get_n_pages()
        for a in range(n):
            ch = self.parent.viewerbook.get_nth_page(a)
            ch.change_font()
        v = self.parent.notebook.get_n_pages()
        for c in range(v):
            if c in [4, 5]:
                ch = self.parent.notebook.get_nth_page(c)
                ch.change_font()
            elif c ==3:
                n = self.parent.winspage.get_n_pages()
                for a in range(n):
                    ch = self.parent.winspage.get_nth_page(a)
                    ch.change_font()
        
    def specified(self, *a):
        if self.dfo.get_active():
            self.frame.set_sensitive(False)
            asm_config.setv('tr', '0')
        elif self.dark.get_active():
            self.frame.set_sensitive(False)
            asm_config.setv('tr', '2')
        else:
            self.frame.set_sensitive(True)
            asm_config.setv('tr', '1')
        
    def ch_font(self, btn):
        nconf = btn.get_name()
        dialog = Gtk.FontChooserDialog("اختر خطا")
        dialog.set_font(asm_config.getv(nconf))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            font = dialog.get_font()
            asm_config.setv(nconf, font)
        dialog.destroy()
        self.parent.theme.refresh()
        
# FIXME change 'get_current_color' to 'get_current_rgba'-------------
    def ch_color(self, btn):
        nconf = btn.get_name()
        dialog = Gtk.ColorSelectionDialog("اختر لونا")
        colorsel = dialog.get_color_selection()
        colorsel.set_current_rgba(asm_customs.rgba(asm_config.getv(nconf)))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            color = colorsel.get_current_color().to_string()
            asm_config.setv(nconf, color)
        dialog.destroy()
        self.parent.theme.refresh()
    
    def change_vls(self, btn, nm):
        v = btn.get_active()
        asm_config.setv(nm, v)
    
    def change_path_db(self, *a):
        open_dlg = Gtk.FileChooserDialog(u'تغيير مسار قاعدة البيانات',
                                         self.parent, Gtk.FileChooserAction.OPEN,
                                        (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                         Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        
        Filter = Gtk.FileFilter()
        Filter.set_name(u"قاعدة البيانات")
        Filter.add_pattern("Listbooks.db")
        open_dlg.add_filter(Filter)
        
        res = open_dlg.run()
        if res == Gtk.ResponseType.OK:
            self.e_dest.set_text(open_dlg.get_filenames()[0].decode('utf8')) 
            asm_config.setv('path', open_dlg.get_filenames()[0])          
            asm_customs.info(self.parent, u'يرجى إعادة تشغيل المكتبة ليتغير المسار فعليا!')
        open_dlg.destroy()
    
    def new_db(self,*a): 
        save_dlg = Gtk.FileChooserDialog(u'مسار قاعدة البيانات الجديدة', self.parent,
                                    Gtk.FileChooserAction.SELECT_FOLDER,
                                    (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        res = save_dlg.run()
        if res == Gtk.ResponseType.OK:
            new_dir = join(save_dlg.get_filename().decode('utf8'), u'مكتبة أسماء')
            if os.path.exists(join(new_dir, u'data', u'Listbooks.db')):
                asm_customs.erro(self.parent, u'يوجد مكتبة في هذا الدليل بالفعل')
            else: 
                if not os.path.exists(new_dir):
                    os.mkdir(new_dir)
                if not os.path.exists(join(new_dir, u'data')):
                    os.mkdir(join(new_dir, u'data'))
                if not os.path.exists(join(new_dir, u'books')):
                    os.mkdir(join(new_dir, u'books'))
                if not os.path.exists(join(new_dir, u'index')):
                    os.mkdir(join(new_dir, u'index'))
                self.db.new_db(join(new_dir, 'data', 'Listbooks.db'))
                asm_customs.info(self.parent, u'تم إضافة مكتبة مفرغة جديدة')
        save_dlg.destroy()
    
    def saved_session_cb(self, *a):
        if self.saved_session.get_active():
            asm_config.setv('saved_session', '1')
        else:
            asm_config.setv('saved_session', '0')
             
    def build(self,*a):
        Gtk.Dialog.__init__(self, parent=self.parent)
        self.set_icon_name("asmaa")
        self.set_title("التفضيلات")
        self.resize(500, 300)
        area = self.get_content_area()
        area.set_spacing(6)
        self.connect('delete-event', lambda *a: self.destroy())
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.notebook = Gtk.Notebook()
        self.box0 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box00 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box1 = Gtk.Box(spacing=4, orientation=Gtk.Orientation.VERTICAL)
        self.box2 = Gtk.Box(spacing=4,orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box(spacing=40,orientation=Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(self.box1, False, False, 0)
        hbox.pack_start(self.box2, False, False, 0)
        self.frame = Gtk.Frame()
        self.frame.add(hbox)
        hbox = Gtk.Box(spacing=10,orientation=Gtk.Orientation.HORIZONTAL)
        self.dfo = Gtk.RadioButton.new_with_label_from_widget(None, 'افتراضي')
        self.cos = Gtk.RadioButton.new_with_label_from_widget(self.dfo, 'مخصص')
        self.dark = Gtk.RadioButton.new_with_label_from_widget(self.cos, 'تباين')
        self.dfo.connect('toggled',self.specified,'0')
        self.cos.connect('toggled',self.specified,'1')
        self.dark.connect('toggled',self.specified,'2')
        hbox.pack_start(self.dfo, False, False, 0)
        hbox.pack_start(self.cos, False, False, 0)
        hbox.pack_start(self.dark, False, False, 0)
        hbox.set_border_width(5)
        self.box0.pack_start(hbox, False, False, 0)
        self.box0.pack_start(self.frame, True, True, 0)
       
        list_w1 = [[u'القوائم الجانبية','_idx'], [u'قائمة الكتب','_bks'], [u'نصوص الكتاب','_nass'], 
                   [u'نصوص أخرى','_oth'], [u'العناوين','_tit'], [u'النص القرآني', '_qrn']]
        list_w2 = [[u'لون خلفية العرض','_bg'], [u'لون خط التحديد','_sel'], [u'لون خلفية التحديد','_bg_sel'], 
                   [u'لون تحديد البحث','_fnd'], [u'لون خلفية القوائم','_bgs'], [u'خلفية النص القرآني', '_bg_qrn']]
        
        for a in list_w1:
            hbox = Gtk.Box(spacing=10,orientation=Gtk.Orientation.HORIZONTAL)
            btn1 = Gtk.ToolButton(stock_id = Gtk.STOCK_SELECT_FONT)
            btn1.set_name('font'+a[1])
            btn1.connect('clicked',self.ch_font)
            btn2 = Gtk.ToolButton(stock_id = Gtk.STOCK_SELECT_COLOR)
            btn2.set_name('color'+a[1])
            btn2.connect('clicked',self.ch_color)
            hbox.pack_start(btn2, False, False, 0)
            hbox.pack_start(btn1, False, False, 0)
            hbox.pack_start(Gtk.Label(a[0]), False, False, 0)
            self.box1.pack_start(hbox, False, False, 0)
            
        for a in list_w2:
            hbox = Gtk.Box(spacing=10,orientation=Gtk.Orientation.HORIZONTAL)
            btn = Gtk.ToolButton(stock_id = Gtk.STOCK_SELECT_COLOR)
            btn.set_name('color'+a[1])
            btn.connect('clicked',self.ch_color)
            hbox.pack_start(btn, False, False, 0)
            hbox.pack_start(Gtk.Label(a[0]), False, False, 0)
            self.box2.pack_start(hbox, False, False, 0)
        self.notebook.append_page(self.box0, Gtk.Label('خط ولون'))
        
        vb = Gtk.VBox(False, 6)
        vb.set_border_width(6)
        
        hbox = Gtk.Box(spacing=10,orientation=Gtk.Orientation.HORIZONTAL)
        self.saved_session = Gtk.CheckButton('حفظ الجلسة')
        hbox.pack_start(self.saved_session, False, False, 0)
        if asm_config.getv('saved_session') == '1': self.saved_session.set_active(True)
        else: self.saved_session.set_active(False)
        self.saved_session.connect("toggled", self.saved_session_cb)
        vb.pack_start(hbox, False, False, 0)
        
        hbox = Gtk.Box(spacing=10,orientation=Gtk.Orientation.HORIZONTAL)
        self.add_db = asm_customs.ButtonClass('إنشاء مكتبة مفرغة')
        self.add_db.connect('clicked', self.new_db)
        hbox.pack_start(self.add_db, False, False, 0)
        vb.pack_start(hbox, False, False, 0)
        
        hbox = Gtk.Box(spacing=6,orientation=Gtk.Orientation.HORIZONTAL)
        self.e_dest = Gtk.Entry()
        self.e_dest.set_text(asm_config.getv('path').decode('utf8'))
        self.b_dest = asm_customs.ButtonClass('تغيير مسار المكتبة')
        self.b_dest.connect('clicked', self.change_path_db)  
        hbox.pack_start(self.b_dest, False, False, 0)
        hbox.pack_start(self.e_dest, True, True, 0)
        vb.pack_start(hbox, False, False, 0)
        
        hbox = Gtk.Box(spacing=11,orientation=Gtk.Orientation.HORIZONTAL)
        db_void = Gtk.LinkButton.new_with_label("http://sourceforge.net/projects/asmaa/files/",
                                                'صفحة البرنامج على النت')
        hbox.pack_start(db_void, False, False, 0)
        
        src_prog = Gtk.LinkButton.new_with_label("https://github.com/RaaH/asmaa",
                                                'مصدر البرنامج على النت')
        hbox.pack_start(src_prog, False, False, 0)
        vb.pack_start(hbox, False, False, 0)
        self.notebook.append_page(vb, Gtk.Label('خيارات'))
        
        vb = Gtk.VBox(False, 7)
        vb.set_border_width(5)
        hbox = Gtk.HBox(False, 7)
        self.progress_repair = Gtk.ProgressBar()
        self.store_repair = Gtk.ListStore(str)
        vb.pack_start(self.progress_repair, False, False, 0)
        self.tree_repair = Gtk.TreeView()
        sah1 = Gtk.TreeViewColumn('نتائج الفحص',Gtk.CellRendererText(),text = 0)
        self.tree_repair.append_column(sah1)
        self.tree_repair.set_model(self.store_repair)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.tree_repair)
        vb.pack_start(scroll, True, True, 0)
        vb.pack_start(hbox, False, False, 0)
        siana = asm_customs.ButtonClass("صيانة")
        siana.connect('clicked', lambda *a: self.db.repair(self.store_repair, self.progress_repair))
        hbox.pack_start(siana, False, False, 0)
        self.notebook.append_page(vb, Gtk.Label('صيانة'))
        
        self.box.pack_start(self.notebook, True, True, 0)
        
        clo = asm_customs.ButtonClass("إغلاق")
        clo.connect('clicked', lambda *a: self.hide())
        ref = asm_customs.ButtonClass("تحديث الواجهة")
        ref.connect('clicked', lambda *a: self.parent.theme.refresh())
        ref.connect('clicked', self.refresh)
        hbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_border_width(5)
        hbox.pack_start(ref, False, False, 0)
        hbox.pack_end(clo, False, False, 0)
        self.box.pack_start(hbox, False, False, 0)
        if asm_config.getv('tr') == '1':
            self.cos.set_active(True)
        elif asm_config.getv('tr') == '2':
            self.frame.set_sensitive(False)
            self.dark.set_active(True)
        else:
            self.frame.set_sensitive(False)
            self.dfo.set_active(True)
        area.pack_start(self.box, True, True, 0)
        self.show_all()