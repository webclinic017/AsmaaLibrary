# -*- coding: utf-8 -*-

#a############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  #########
#a############################################################################

from gi.repository import Gtk, Pango
import asm_customs
from asm_contacts import TarajimDB
import re

# class نافذة الرواة---------------------------------------------------------    

class Tarjama(Gtk.HPaned):
    rawa_anhe = {u'خ':u'البخاري في صحيحه، ', 
                'خت':u'البخاري في صحيحه معلقا، ', 
                'بخ':u'البخاري في الادب المفرد، ', 
                'عخ':u'البخاري في خلق أفعال العباد، ', 
                'ز':u'البخاري في جزء القراءة خلق الامام، ', 
                'ي':u'البخاري في رفع اليدين، ', 
                'م':u'مسلم في صحيحه، ', 
                'مق':u'مسلم في المقدمة، ', 
                'د':u'أبو داود في سننه، ', 
                'مد':u'أبو داود في المراسيل، ', 
                'صد':u'أبو داود في فضائل الانصار، ', 
                'خد':u'أبو داود في الناسخ، ', 
                'قد':u'أبو داود في القدر، ', 
                'ف':u'أبو داود في التفرد، ', 
                'ل':u'أبو داود في المسائل، ', 
                'كد':u'أبو داود في مسند مالك، ', 
                'ت':u'الترمذي في سننه، ', 
                'تم':u'الترمذي في الشمائل، ', 
                'س':u'النسائي في سننه، ', 
                'عس':u'النسائي في مسند علي، ', 
                'سي':u'النسائي في عمل اليوم والليلة، ', 
                'كن':u'النسائي في مسند مالك، ', 
                'ص':u'النسائي في خصائص الامام علي، ', 
                'ق':u'ابن ماجة في سننه، ',
                'فق':u'ابن ماجة في التفسير، ',}
    tags = [ "الاسم :  ","المولد :  ","الوفاة :  ","الطبقة :  "
                ,"الرواة عنه :  ","الرتبة عند الحافظ :  ","الرتبة عند الذهبي :  "]
        
    def search_on_page(self, text):
        return
        
    def search_on_active(self, text):
        rawis = self.db.tardjma(text)
        self.store_tarjama.clear()
        for a in rawis:
            self.store_tarjama.append(None, a)
    
    def show_tarjama(self, *a):
        model, i = self.sel_tarjama.get_selected()
        if i:
            id_rawi = model.get_value(i,0)
            rawi = self.db.show_rawi(id_rawi)
            rawa_anhe_txt = ''
            for t in rawi[3].split(' '):
                if t in self.rawa_anhe.keys():
                    rawa_anhe_txt += re.sub(t, self.rawa_anhe[t], t)
            text = '''الاسم :  {}
المولد :  {}
الوفاة :  {}
الطبقة :  {}
الرواة عنه :  {} : {}
الرتبة عند الحافظ :  {}
الرتبة عند الذهبي :  {}'''.format(rawi[1], rawi[6], rawi[7], 
                                  rawi[2], rawi[3], rawa_anhe_txt, rawi[4], rawi[5])  
            
            text = re.sub("F", 'صحابي رضي الله عنه', text)
            text = re.sub("G", 'الثانية ، كبار التابعين', text)
            text = re.sub("H", 'الثالثة ، الوسطى من التابعين', text)
            text = re.sub("I", 'الرابعة ، تلي الوسطى من التابعين', text)
            text = re.sub("J", 'الخامسة ، صغار التابعين', text)
            text = re.sub("K", 'السادسة ، الذين عاصروا صغار التابعين', text)
            text = re.sub("L", 'السابعة ، كبار أتباع التابعين', text)
            text = re.sub("M", 'الثامنة ، الوسطى من أتباع التابعين', text)
            text = re.sub("N", 'التاسعة ، صغار أتباع التابعين', text)
            text = re.sub("O", 'العاشرة ، كبار الآخذين عن تبع الأتباع', text)
            text = re.sub("P", 'الحادية عشرة ، الوسطى من الآخذين عن تبع الأتباع', text)
            text = re.sub("Q", 'الثانية عشرة ، صغار الآخذين عن تبع الأتباع', text)
            text = re.sub("&lt;", '<', text)
            text = re.sub("&gt;", '>', text)
            text = re.sub("&quot;", '"', text)
            text = re.sub("W", 'صلى الله عليه وسلم', text)
            text = re.sub(u"1 :", 'الأولى ،', text)
            self.view_tarjama_bfr.set_text(text)
            asm_customs.with_tag(self.view_tarjama_bfr, self.view_tarjama_tag, self.tags)
                
    def near_page(self, v):
        self.size_font += v
        self.view_tarjama.override_font(Pango.FontDescription("{}".format(self.size_font,))) 
    
    def __init__(self, parent):
        self.parent = parent
        self.db = TarajimDB()
        self.size_font = asm_customs.split_font(self.parent.theme.font_nasse_books)[0]
        self.all_term = []
        Gtk.HPaned.__init__(self)
        self.set_border_width(3)
        
        self.tree_tarjama = Gtk.TreeView()
        self.tree_tarjama.set_name('Tree')
        self.sel_tarjama = self.tree_tarjama.get_selection()
        cell = Gtk.CellRendererText()
        cell.set_property("ellipsize", Pango.EllipsizeMode.END)
        kal = Gtk.TreeViewColumn('الرواة', cell, text=1)
        self.tree_tarjama.append_column(kal)
        self.store_tarjama = Gtk.TreeStore(int, str)
        self.tree_tarjama.set_model(self.store_tarjama)
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_tarjama)
        self.tree_tarjama.connect("cursor-changed", self.show_tarjama)
        self.pack1(scroll, True, True)
        
        self.view_tarjama = asm_customs.ViewClass()
        self.view_tarjama.set_name('View')
        self.view_tarjama_bfr = self.view_tarjama.get_buffer()
        self.view_tarjama_tag = self.view_tarjama_bfr.create_tag("tarjama")
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.view_tarjama)
        self.pack2(scroll, True, True)
        self.set_position(250)
        
        self.show_all()