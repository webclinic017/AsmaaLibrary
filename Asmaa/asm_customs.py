# -*- coding: utf-8 -*-

##############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  ########
##############################################################################

from os.path import join, dirname, realpath, exists, expanduser
from gi.repository import Gtk, Gdk, Pango
import asm_config, asm_araby
from os import mkdir
import re, sqlite3

Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL)

#a------------------------------------------
version = '2.0.7'
#a--------------------------------------------------
APP_DIR      = dirname(dirname(realpath(__file__))).decode('utf8')
HOME_DIR     = expanduser(u'~/.asmaa')
if exists(join(APP_DIR, u'asmaa-data', u'icons', u'tab.png')):
    DATA_DIR = join(APP_DIR, u'asmaa-data')
elif exists(u'/usr/share/asmaa/asmaa-data/icons/tab.png'):
    DATA_DIR = u'/usr/share/asmaa/asmaa-data'
elif exists(u'/usr/local/share/asmaa/asmaa-data/icons/tab.png'):
    DATA_DIR = u'/usr/local/share/asmaa/asmaa-data'

ICON_DIR     = join(DATA_DIR, u'icons')
MY_DATA      = join(DATA_DIR, u'data')

# a ------------------------------------------------

schema = {
        'main': "bk TEXT, shortname TEXT, cat INTEGER, betaka TEXT, inf TEXT, authno INTEGER DEFAULT 0, \
            auth_death INTEGER DEFAULT 0, islamshort INTEGER DEFAULT 0, is_tafseer INTEGER DEFAULT 0, \
            is_sharh INTEGER DEFAULT 0, version INTEGER DEFAULT 0.1", 
        'shorts': "ramz TEXT, nass TEXT", 
        'shrooh': "matnid INTEGER, sharhid INTEGER, matnpg INTEGER, sharhpg INTEGER", 
        'pages': "id INTEGER PRIMARY KEY, nass TEXT, part INTEGER DEFAULT 1, page INTEGER DEFAULT 1, hno INTEGER DEFAULT 0, \
            sora INTEGER DEFAULT 0, aya INTEGER DEFAULT 0, na INTEGER DEFAULT 0", 
        'titles': "id INTEGER, tit TEXT, lvl INTEGER DEFAULT 1, sub INTEGER DEFAULT 0", 
        'com': "pgid INTEGER PRIMARY KEY, nass TEXT"
}

#a------------------------------------------
def info(parent, msg):
    dlg = Gtk.MessageDialog(parent, Gtk.DialogFlags.MODAL,
                            Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, msg)
    dlg.run()
    dlg.destroy()

#a------------------------------------------
def erro(parent, msg):
    dlg = Gtk.MessageDialog(parent, Gtk.DialogFlags.MODAL,
                            Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, msg)
    dlg.run()
    dlg.destroy()

#a------------------------------------------
def sure(parent, msg):
    dlg = Gtk.MessageDialog(parent, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING,
                             Gtk.ButtonsType.YES_NO)
    dlg.set_markup(msg)                         
    r = dlg.run()
    dlg.destroy()
    return r

#a------------------------------------------
def sure_start():
    dlg = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING,
                             Gtk.ButtonsType.YES_NO)
    dlg.set_markup('''
    لم يتمكن البرنامج من الاتصال بقاعدة البيانات،
    إذا كنت قد نزلتها بالفعل فربما لم تربطها بالبرنامج، 
    أو قد يكون القرص الموجود عليه القاعدة غير مضموم،
    هل تريد تحديد مسار قاعدة البيانات ؟''')
    db_void = Gtk.LinkButton.new_with_label("http://sourceforge.net/projects/asmaalibrary/files/AsmaaLibrary.tar.gz/download",
                                                'تنزيل قاعدة بيانات للتجربة')
    new_lib = Gtk.Button('إنشاء مكتبة مفرغة')
    dlg.add_action_widget(new_lib, 3)
    area = dlg.get_content_area()
    area.set_spacing(7)
    hbox = Gtk.HBox(False, 7)
    hbox.pack_end(db_void, False, False, 0)
    area.pack_start(hbox, False, False, 0)
    area.show_all()
    r = dlg.run()
    dlg.destroy()
    return r

#a------------------------------------------------
def change_path_db():
        open_dlg = Gtk.FileChooserDialog(u'تحديد مسار قاعدة البيانات',
                                         None, Gtk.FileChooserAction.OPEN,
                                        (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                         Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        
        Filter = Gtk.FileFilter()
        Filter.set_name(u"قاعدة البيانات")
        Filter.add_pattern("Listbooks.db")
        open_dlg.add_filter(Filter)
        
        res = open_dlg.run()
        if res == Gtk.ResponseType.OK:
            asm_config.setv('path', open_dlg.get_filenames()[0])          
            open_dlg.destroy()
        else:
            open_dlg.destroy()
            quit()

#a------------------------------------------
if not exists(asm_config.getv('path')): 
    res = sure_start()
    if res == Gtk.ResponseType.YES:
        change_path_db()
        PATH_DIR  = asm_config.getv('path')
        MY_DIR = dirname(dirname(PATH_DIR)).decode('utf8')
    elif res == Gtk.ResponseType.NO:
        my_return = 0
        quit()
    elif res == 3:
        save_dlg = Gtk.FileChooserDialog(u'مسار قاعدة البيانات الجديدة', None,
                                    Gtk.FileChooserAction.SELECT_FOLDER,
                                    (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        res = save_dlg.run()
        if res == Gtk.ResponseType.OK:
            new_dir = join(save_dlg.get_filename().decode('utf8'), u'مكتبة أسماء')
            if exists(join(new_dir, 'data', 'Listbooks.db')):
                erro(None, u'يوجد مكتبة في هذا الدليل بالفعل')
            else:
                if not exists(new_dir):
                    mkdir(new_dir)
                if not exists(join(new_dir, u'data')):
                    mkdir(join(new_dir, u'data'))
                if not exists(join(new_dir, u'books')):
                    mkdir(join(new_dir, u'books'))
                if not exists(join(new_dir, u'index')):
                    mkdir(join(new_dir, u'index'))
                con = sqlite3.connect(join(new_dir, 'data', 'Listbooks.db'))
                cur = con.cursor()
                cur.execute('CREATE TABLE groups (id_group integer primary key, tit varchar(255), sub INTEGER, cat INTEGER)') 
                cur.execute('CREATE TABLE books (id_book integer primary key, tit varchar(255), \
                parent INTEGER, fav  INTEGER DEFAULT 0, last  INTEGER DEFAULT 1, cat  INTEGER DEFAULT 0,\
                tafsir  INTEGER DEFAULT 0, indx INTEGER DEFAULT 0)')
                info(None, u'تم إضافة مكتبة مفرغة جديدة')
        save_dlg.destroy()
        asm_config.setv('path', join(new_dir, 'data', 'Listbooks.db'))
        PATH_DIR  = asm_config.getv('path')
        MY_DIR = dirname(dirname(PATH_DIR)).decode('utf8')
else:
    PATH_DIR = asm_config.getv('path')
    MY_DIR = dirname(dirname(PATH_DIR)).decode('utf8')
    
if not exists(join(MY_DIR, 'fields-search')):
    mkdir(join(MY_DIR, 'fields-search'))
    
if not exists(join(MY_DIR, 'waraka-search')):
    mkdir(join(MY_DIR, 'waraka-search'))
    
#a--------------------------------------------------
try: greet = Gtk.Window(Gtk.WindowType.POPUP)
except: 
    greet = Gtk.Window()
    greet.set_title("مرحبا !")
greet.set_border_width(15)
greet.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
greet.set_size_request(400,300)
vb = Gtk.VBox(False, 10)
img_greet = Gtk.Image()
img_greet.set_from_file(join(ICON_DIR,"greet.png"))
vb.pack_start(img_greet, False, False, 0)
vb.pack_start(Gtk.Label('الإصدار {}\nجاري تحميل برنامج مكتبة أسماء....'.format(version, ))
              , False, False, 0)
greet.add(vb)
greet.show_all()
while (Gtk.events_pending()): Gtk.main_iteration()

#a------------------------------------------
def rgba(value):
    value = value.lstrip('#')
    v = len(value)/3
    R = int(value[0:v], 16)/15.999**v
    G = int(value[v:2*v], 16)/15.999**v
    B = int(value[2*v:3*v], 16)/15.999**v
    A = 1.0
    return Gdk.RGBA(R, G, B, A)

#a-------------------------------------------
def rgb(value):
    value = value.lstrip('#')
    v = len(value)/3
    R = int(value[0:v], 16)/16**(v-2)
    G = int(value[v:2*v], 16)/16**(v-2)
    B = int(value[2*v:3*v], 16)/16**(v-2)
    return  'rgb({}, {}, {})'.format(R, G, B)

#a------------------------------------------
def tool_button(icon_file, tooltip, function, data=None):
        ''' Build custom toolbutton '''
        toolbtn = Gtk.ToolButton()
        widget = Gtk.Image.new_from_file(join(APP_DIR, icon_file))
        toolbtn.set_icon_widget(widget)
        toolbtn.set_tooltip_text(tooltip)
        toolbtn.connect('clicked', function, data)
        return toolbtn

#a------------------------------------------
def combo(ls, name, v):
    new_ls = []
    new_ls.extend(ls)
    hb = Gtk.HBox(False, 6) 
    store = Gtk.ListStore(int, str, int)
    cmt = Gtk.ComboBox.new_with_model(store)
    if v == 1:
        new_ls.insert(0, [0, u'الكل'])
    for a in new_ls:
        if len(a) == 2:
            store.append([a[0], a[1], 0])
        else:
            store.append([a[0], a[1], a[2]])
    renderer_text = Gtk.CellRendererText()
    renderer_text.set_property("ellipsize-set", True)
    renderer_text.set_property("ellipsize", Pango.EllipsizeMode.END)
    renderer_text.set_property("max-width-chars",14)
    renderer_text.set_property("weight", 14)
    cmt.pack_start(renderer_text, True)
    cmt.add_attribute(renderer_text, "text", 1)
    lab = Gtk.Label(name)
    lab.set_alignment(0,0.5)
    if v == 3:
        lab.set_size_request(200, 8)
        cmt.set_size_request(120, -1)
    elif v == 4:
        lab.set_size_request(40, -1)
        cmt.set_size_request(40, -1)
    else:
        lab.set_size_request(50, -1)
        cmt.set_size_request(140, -1)
    hb.pack_start(lab, False, False, 0)
    hb.pack_end(cmt, False, False, 0)
    if v == 1:
        cmt.set_active(0)
    return hb, cmt

#a------------------------------------------
def button_fontnm():
    list_font = [[u"Amiri", u"أميري"], [u"Simplified Naskh", u"نسخ مبسط"], [u'AlHor', u"الحور"], [u"KacstBook", u"KacstBook"],
             [u"KacstLetter", u"KacstLetter"], [u'KacstNaskh', u"KacstNaskh"], [u'KacstFarsi', u"KacstFarsi"], 
             [u"KacstOne", u"KacstOne"], [u"KacstQurn", u"KacstQurn"], [u'KacstTitle', u"KacstTitle"]]
    store = Gtk.ListStore(str, str)
    cmt = Gtk.ComboBox.new_with_model(store)
    for a in list_font:
        store.append([a[0], a[1]])
    renderer_text = Gtk.CellRendererText()
    renderer_text.set_property("ellipsize-set", True)
    renderer_text.set_property("weight", 14)
    renderer_text.set_property("ellipsize", Pango.EllipsizeMode.END)
    cmt.pack_start(renderer_text, True)
    cmt.add_attribute(renderer_text, "text", 1)
    cmt.set_size_request(40, -1)
    lab = Gtk.Label('الخط')
    hb = Gtk.HBox(False, 0) 
    hb.set_border_width(3)
    hb.pack_start(lab, False, False, 0)
    hb.pack_start(cmt, False, False, 0)
    return hb, cmt
 
#a------------------------------------------
def button_fontsz():
    list_font = [[u'1', u'1'], [u'2', u'2'], [u'3', u'3'], [u'4', u'4'], 
                [u'5', u'5'], [u'6', u'6'], [u'7', u'7']] 
    store = Gtk.ListStore(str, str)
    cmt = Gtk.ComboBox.new_with_model(store)
    for a in list_font:
        store.append([a[0], a[1]])
    renderer_text = Gtk.CellRendererText()
    renderer_text.set_property("ellipsize-set", True)
    renderer_text.set_property("weight", 14)
    renderer_text.set_property("ellipsize", Pango.EllipsizeMode.END)
    cmt.pack_start(renderer_text, True)
    cmt.add_attribute(renderer_text, "text", 0)
    cmt.set_size_request(40, -1)
    lab = Gtk.Label('حجم')
    hb = Gtk.HBox(False, 0) 
    hb.set_border_width(3)
    hb.pack_start(lab, False, False, 0)
    hb.pack_start(cmt, False, False, 0)
    return hb, cmt

#a------------------------------------------
def value_active(combo, n=0):
    if combo.get_active() == -1: return None
    v = combo.get_active_iter()
    model = combo.get_model()
    value = model.get_value(v, n)
    return value

#a------------------------------------------
def search_and_mark(text_buff, text_tag, text, start, tt, view):
    i_min = None
    end = text_buff.get_end_iter()
    match = start.forward_search(text, Gtk.TextSearchFlags.CASE_INSENSITIVE, end)
    if match != None:
        match_start, match_end = match
        text_buff.apply_tag(text_tag, match_start, match_end)
        if match_start and (not i_min or i_min.compare(match_start) > 0): 
                i_min = match_start
        if tt == 1:
            search_and_mark(text_buff, text_tag, text, match_end, 1, view)
        if i_min and view != None:
            view.scroll_to_iter(i_min, 0.0, False, 0.5, 0.5)
        
def with_tag(text_buff, text_tag, ls, tt=0, view=None):
    for text in ls:
        cursor_mark = text_buff.get_insert()
        start = text_buff.get_iter_at_mark(cursor_mark)
        if start.get_offset() == text_buff.get_char_count():
            start = text_buff.get_start_iter()
        search_and_mark(text_buff, text_tag, text, start, tt, view)

##a------------------------------------------           
#def tashkil(text):
#    if asm_config.getv('tashkil') == '0': return daw_araby.stripTashkeel(text)
#    else: return text
    
#a------------------------------------------
class ViewClass(Gtk.TextView):
    __gtype_name__ = 'View'
    def __init__(self, *a):
        Gtk.TextView.__init__(self)
        self.set_cursor_visible(False)
        self.set_editable(False)
        self.set_right_margin(10)
        self.set_left_margin(10)
        self.set_wrap_mode(Gtk.WrapMode.WORD)
#        self.get_width = self.get_size_request()[0]
        
#a------------------------------------------
class ViewBitaka(Gtk.TextView):
    __gtype_name__ = 'Viewbitaka'
    def __init__(self, *a):
        Gtk.TextView.__init__(self)
        self.set_cursor_visible(False)
        self.set_editable(False)
        self.set_right_margin(5)
        self.set_left_margin(5)
        self.set_wrap_mode(Gtk.WrapMode.WORD)
                
#a------------------------------------------
class ButtonClass(Gtk.Button):
    __gtype_name__ = 'button'
    def __init__(self, name):
        Gtk.Button.__init__(self, name)
        label = Gtk.Label()
        label.set_text(name)
        pangolayout = label.get_layout()
        d = pangolayout.get_pixel_size()
        w = ((d[0]/25)+2)*25
        self.set_size_request(w, 30)
    
#a------------------------------------------
class TreeIndex(Gtk.TreeView):
    __gtype_name__ = 'Treeindex'
    def __init__(self, *a):
        Gtk.TreeView.__init__(self)
        
#a------------------------------------------
class TreeClass(Gtk.TreeView):
    __gtype_name__ = 'Tree'
    def __init__(self, *a):
        Gtk.TreeView.__init__(self)

def first_term(text):
    text = re.sub('\n', ' ', text)
    text = re.sub(' +', ' ', text)
    text = text.strip()
    ls = text.split(' ')
    txt = asm_araby.stripTatweel(ls[0])
    return txt
        
#a------------------------------------------
class SpinnerClass(Gtk.Dialog):

    def __init__(self, parent, title):
        while (Gtk.events_pending()): Gtk.main_iteration()
        Gtk.Dialog.__init__(self, parent=parent)
        self.set_title(title)
        self.set_size_request(300, 160)
        area = self.get_content_area()
        area.set_spacing(6)
        lab = Gtk.Label('\nانتظر قليلاً من فضلك ...\n')
        self.spinner = Gtk.Spinner()
        self.spinner.start()
        vb = Gtk.VBox(False, 6)
        vb.pack_start(lab, False, False, 0)
        vb.pack_start(self.spinner,  True, True, 0)
        area.pack_start(vb, True, True, 0)
        self.show_all()

    def close(self, *a):
        self.destroy()
