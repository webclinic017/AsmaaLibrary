# -*- coding: utf-8 -*-

#a############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  #########
#a############################################################################

from gi.repository import Gtk, Pango
import asm_araby, asm_customs, asm_stemming
from asm_contacts import DictDB

# class نافذة المعجم---------------------------------------------------------    

class Explanatory(Gtk.VBox):
    
    def show_charh(self, *a):
        model, i = self.sel_dict.get_selected()
        if i:
            p = model.get_path(i)
            if model.iter_has_child(i) :
                if self.tree_dict.row_expanded(p):
                    self.tree_dict.collapse_row(p)
                else: self.tree_dict.expand_row(p, False) 
            else:
                term = model.get_value(i,0).decode('utf-8')
                charh = self.mydict.show_charh(term)
                self.view_dict_bfr.set_text(charh[0][0]) 
    
    def search_in_page(self, *a):
        text = self.entry_search.get_text().decode('utf8')
        self.show_charh()
        search_tokens = []
        nasse = self.view_dict_bfr.get_text(self.view_dict_bfr.get_start_iter(), 
                                            self.view_dict_bfr.get_end_iter(),True).split()
        if text == u'': 
            for a in self.all_term:
                txt = asm_araby.fuzzy(a)
                for term in nasse: 
                    if txt in asm_araby.fuzzy(term.decode('utf8')):
                        search_tokens.append(term)
        else:
            txt = asm_araby.fuzzy(text)
            for term in nasse: 
                if txt in asm_araby.fuzzy(term.decode('utf8')):
                    search_tokens.append(term)
        asm_customs.with_tag(self.view_dict_bfr, self.search_tag, search_tokens)
    
    def search(self, *a):
        text = self.entry_search.get_text().decode('utf8')
        if text == u'': return
        elif len(text) < 3: 
            asm_customs.erro(self.parent, 'أدخل كلمة بها أكثر من حرفين للبحث عنها')
            return
        all_root, all_term = asm_stemming.get_root(u''+text)
        self.tree_dict.collapse_all()
        self.store_dict.clear()
        self.view_dict_bfr.set_text('')
        if len(all_root) == 0: asm_customs.erro(self.parent, 'لا يوجد نتيجة'); return
        for text in all_root: 
            self.store_dict.append(None, [text])
        self.all_term = all_term
                
    def near_page(self, v):
        self.size_font += v
        self.view_dict.override_font(Pango.FontDescription("{}".format(self.size_font,))) 
    
    def move_in_page(self, v):
        model, i = self.sel_dict.get_selected()
        if i:
            p = model.get_path(i).get_indices()[0]
            if p+v == -1 or p+v == len(model): return
            i1 = model.get_iter((p+v,))
            self.tree_dict.get_selection().select_iter(i1)
            self.tree_dict.scroll_to_cell((p+v,))
        elif len(self.tree_dict.get_model()) == 0: return
        else:
            i2 = model.get_iter((0,))
            self.tree_dict.get_selection().select_iter(i2)
            self.tree_dict.scroll_to_cell((0,))
        self.show_charh()
    
    def show_index(self, f_letter):
        self.tree_dict.collapse_all()
        self.store_dict.clear()
        self.view_dict_bfr.set_text('')
        all_index = self.mydict.all_index(f_letter)
        if len(all_index) > 0:
            for a in all_index:
                self.store_dict.append(None, [a[0]])
    
    def select_letter(self, *a):
        letter = asm_customs.value_active(self.btn_letters, 1).decode('utf-8')
        f_letter = letter[0]
        self.show_index(f_letter)
    
    def change_font(self, *a):
        self.search_tag.set_property('background', self.parent.theme.color_fnd) 
    
    def __init__(self, parent):
        self.parent = parent
        self.mydict = DictDB()
        self.size_font = int(self.parent.theme.font_nass[-2:])
        self.all_term = []
        Gtk.VBox.__init__(self, False, 7)
        self.set_border_width(3)
        self.hb = Gtk.HBox(False, 7)
        self.tree_dict = asm_customs.TreeIndex()
        self.sel_dict = self.tree_dict.get_selection()
        cell = Gtk.CellRendererText()
        kal = Gtk.TreeViewColumn('الجذور', cell, text=0)
        self.tree_dict.append_column(kal)
        self.store_dict = Gtk.TreeStore(str)
        self.tree_dict.set_model(self.store_dict)
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(150,  -1)
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.tree_dict)
        self.tree_dict.connect("cursor-changed", lambda *a: self.search_in_page(u""))
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.hb.pack_start(scroll, False, False, 0)
        
        hbox = Gtk.Box(spacing=10,orientation=Gtk.Orientation.HORIZONTAL)
        letters = [ 
            [1, u"ألف"], 
            [2, u"باء"], 
            [3, u'تاء' ], 
            [4, u'ثاء' ],
            [5, u'جيم' ], 
            [6, u'حاء' ], 
            [7, u'خاء' ], 
            [8, u'دال' ], 
            [9, u'ذال' ],
            [10, u'راء' ], 
            [11, u'زاي' ], 
            [12, u'سين' ], 
            [13, u'شين' ], 
            [14, u'صاد' ],
            [15, u'ضاد' ], 
            [16, u'طاء' ], 
            [17, u'ظاء' ], 
            [18, u'عين' ], 
            [19, u'غين' ],
            [20, u'فاء' ], 
            [21, u'قاف' ], 
            [22, u'كاف' ], 
            [23, u'لام' ], 
            [24, u'ميم' ],
            [25, u'نون' ], 
            [26, u'هاء' ], 
            [27, u'واو' ], 
            [28, u'ياء' ],
            ]
        hb, self.btn_letters = asm_customs.combo(letters, u'تصفح بالحروف', 4)
        self.btn_letters.connect('changed', self.select_letter)
        hbox.pack_start(hb, False, False, 0)
        self.btn_search = Gtk.ToolButton(stock_id=Gtk.STOCK_FIND)
        try: self.entry_search = Gtk.SearchEntry()
        except: self.entry_search = Gtk.Entry()
        self.entry_search.set_placeholder_text('أدخل نصا للبحث عنه')
        self.entry_search.connect("activate", self.search) 
        self.entry_search.connect("changed", self.search_in_page) 
        self.btn_search.connect('clicked', self.search)
        hbox.pack_end(self.entry_search, False, False, 0)
        hbox.pack_end(self.btn_search, False, False, 0)
        self.pack_start(hbox, False, False, 0)
        
        self.view_dict = asm_customs.ViewClass()
        self.view_dict_bfr = self.view_dict.get_buffer()
        self.search_tag = self.view_dict_bfr.create_tag("search")
        self.change_font()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.view_dict)
        self.hb.pack_start(scroll, True, True, 0)
        self.pack_start(self.hb, True, True, 0)
        
        self.show_all()
        




