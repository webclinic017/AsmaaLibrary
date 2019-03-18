# -*- coding: utf-8 -*-

#a############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  #########
#a############################################################################

from gi.repository import Gtk, Pango
import asm_customs, asm_araby
from asm_contacts import TarajimDB
import re

# class نافذة الرواة---------------------------------------------------------    

class Tarjama(Gtk.HPaned):
    rawa_anhe = {u'خ':u'البخاري في صحيحه، ', 
                u'خت':u'البخاري في صحيحه معلقا، ', 
                u'بخ':u'البخاري في الادب المفرد، ', 
                u'عخ':u'البخاري في خلق أفعال العباد، ', 
                u'ز':u'البخاري في جزء القراءة خلق الامام، ', 
                u'ي':u'البخاري في رفع اليدين، ', 
                u'م':u'مسلم في صحيحه، ', 
                u'مق':u'مسلم في المقدمة، ', 
                u'د':u'أبو داود في سننه، ', 
                u'مد':u'أبو داود في المراسيل، ', 
                u'صد':u'أبو داود في فضائل الانصار، ', 
                u'خد':u'أبو داود في الناسخ، ', 
                u'قد':u'أبو داود في القدر، ', 
                u'ف':u'أبو داود في التفرد، ', 
                u'ل':u'أبو داود في المسائل، ', 
                u'كد':u'أبو داود في مسند مالك، ', 
                u'ت':u'الترمذي في سننه، ', 
                u'تم':u'الترمذي في الشمائل، ', 
                u'س':u'النسائي في سننه، ', 
                u'عس':u'النسائي في مسند علي، ', 
                u'سي':u'النسائي في عمل اليوم والليلة، ', 
                u'كن':u'النسائي في مسند مالك، ', 
                u'ص':u'النسائي في خصائص الامام علي، ', 
                u'ق':u'ابن ماجة في سننه، ',
                u'فق':u'ابن ماجة في التفسير، ',}
    tags = [ "الاسم :  ","المولد :  ","الوفاة :  ","الطبقة :  "
                ,"الرواة عنه :  ","الرتبة عند الحافظ :  ","الرتبة عند الذهبي :  "]
        
    def search_cb(self, *a):
        text = self.search_rawi.get_text().decode('utf8')
        rawis = self.db.tardjma(text)
        self.store_tarjama.clear()
        for a in rawis:
            self.store_tarjama.append(None, a)
    
    def show_tarjama(self, *a):
        model, i = self.sel_tarjama.get_selected()
        if i:
            id_rawi = model.get_value(i,0)
            rawi = self.db.show_rawi(id_rawi)
            rawa_anhe_txt = u''
            for t in rawi[3].split(' '):
                if t in self.rawa_anhe.keys():
                    rawa_anhe_txt += re.sub(t, self.rawa_anhe[t], t)
            text = u'''الاسم :  {}
المولد :  {}
الوفاة :  {}
الطبقة :  {}
الرواة عنه :  {} : {}
الرتبة عند الحافظ :  {}
الرتبة عند الذهبي :  {}'''.format(rawi[1], rawi[6], rawi[7], 
                                  rawi[2], rawi[3], rawa_anhe_txt, rawi[4], rawi[5])  
            
            text = re.sub("F", u'صحابي رضي الله عنه', text)
            text = re.sub("G", u'الثانية ، كبار التابعين', text)
            text = re.sub("H", u'الثالثة ، الوسطى من التابعين', text)
            text = re.sub("I", u'الرابعة ، تلي الوسطى من التابعين', text)
            text = re.sub("J", u'الخامسة ، صغار التابعين', text)
            text = re.sub("K", u'السادسة ، الذين عاصروا صغار التابعين', text)
            text = re.sub("L", u'السابعة ، كبار أتباع التابعين', text)
            text = re.sub("M", u'الثامنة ، الوسطى من أتباع التابعين', text)
            text = re.sub("N", u'التاسعة ، صغار أتباع التابعين', text)
            text = re.sub("O", u'العاشرة ، كبار الآخذين عن تبع الأتباع', text)
            text = re.sub("P", u'الحادية عشرة ، الوسطى من الآخذين عن تبع الأتباع', text)
            text = re.sub("Q", u'الثانية عشرة ، صغار الآخذين عن تبع الأتباع', text)
            text = re.sub("&lt;", u'<', text)
            text = re.sub("&gt;", u'>', text)
            text = re.sub("&quot;", u'"', text)
            text = re.sub("W", u'صلى الله عليه وسلم', text)
            text = re.sub(u"1 :", u'الأولى ،', text)
            self.view_tarjama_bfr.set_text(text)
            asm_customs.with_tag(self.view_tarjama_bfr, self.view_tarjama_tag, self.tags)
                
    def near_page(self, v):
        self.size_font += v
        self.view_tarjama.override_font(Pango.FontDescription("{}".format(self.size_font,))) 
    
    def change_font(self, *a):
        self.view_tarjama_tag.set_property('foreground', self.parent.theme.color_tit)
        self.view_tarjama_tag.set_property('font', self.parent.theme.font_tit)
    
    def __init__(self, parent):
        self.parent = parent
        self.db = TarajimDB()
        self.size_font = int(self.parent.theme.font_nass[-2:])
        self.all_term = []
        Gtk.HPaned.__init__(self)
        self.set_border_width(3)
        vbox = Gtk.VBox(False, 3)
        try: self.search_rawi = Gtk.SearchEntry()
        except: self.search_rawi = Gtk.Entry()
        self.search_rawi.set_placeholder_text('بحث عن راوِ')
        self.search_rawi.connect('activate', self.search_cb)
        vbox.pack_start(self.search_rawi, False, False, 0)
        
        self.tree_tarjama = asm_customs.TreeIndex()
        self.sel_tarjama = self.tree_tarjama.get_selection()
        cell = Gtk.CellRendererText()
        kal = Gtk.TreeViewColumn('الرواة', cell, text=1)
        self.tree_tarjama.append_column(kal)
        self.store_tarjama = Gtk.TreeStore(int, str)
        self.tree_tarjama.set_model(self.store_tarjama)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_tarjama)
        self.tree_tarjama.connect("cursor-changed", self.show_tarjama)
        vbox.pack_start(scroll, True, True, 0)
        self.pack1(vbox, True, True)
        
        self.view_tarjama = asm_customs.ViewClass()
        self.view_tarjama_bfr = self.view_tarjama.get_buffer()
        self.view_tarjama_tag = self.view_tarjama_bfr.create_tag("tarjama")
        self.change_font()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.view_tarjama)
        self.pack2(scroll, True, True)
        self.set_position(200)
        
        self.show_all()