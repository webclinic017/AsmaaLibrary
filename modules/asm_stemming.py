#!/usr/bin/python
# -*- coding: utf-8 -*-

#a############################################################################
#a########  "قُلۡ بِفَضلِ ٱللَّهِ وَبِرَحمَتِهِۦ فَبِذَٰلِكَ فَليَفرَحُواْ هُوَ خَيرُُ مِّمَّا يَجمَعُونَ"  #########
#a############################################################################

#a============================================================================
#a                       المشروع : وحدة استخراج الجذور والجذوع للكلمات العربية                                                      
#a                                 <asmaaarab@gmail.com>   المطور  : أحمد رغدي                               
#a  http://www.ojuba.org/wiki/doku.php/waqf/license  الرخصة  : رخصة وقف العامة
#a============================================================================

#a============================================================================
#a                                  ـ الكلمة العربية المفردة لا تتجوز سبعة أحرف
#a        ـ الكلمة العربية لا تقل عن ثلاثة أحرف باستثناء الأدوات أو ماحذف منه حرف
#a                                  ـ الكلمة العربية المجردة لا تتجوز خمسة أحرف
#a                                              ـ أكثر الجذور في العربية ثلاثية
#a                                      ـ الحالات النادرة لا تعتبر في هذه الوحدة
#a============================================================================
#a      الجذع هو الكلمة المفردة أي غير المتصل بها كلمات لا في أولها ولا في آخرها
#a                            الجذوع هي الكلمات الناتجةعن حذف السوابق واللواحق
#a                                  مثال : بالاستخراج = استخراج ، يضربهن = يضرب
#a~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#a                              السوابق وهي الكلمات المتصلة بأول الكلمة الأصلية
#a                                          مثال الباء وال التعريف في : بالقلم
#a      استـ في كلمة استخرج ليست سابقة لأنها جزء من الكلمة وليست كلمة متصلة بها
#a                       ـ ما كان أوله ألفا ولاما ليس بعدها تاء فلا يكون إلا اسما
#a                                                ـ لا تدخل السين على غير الفعل
#a                                             ـ لا تدخل حروف الجر على غير الاسم 
#a                           ـ تاء القسم لا تدخل على غير لفظ الجلالة واسم الرحمن
#a~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#a                              اللواحق وهي الكلمات المتصلة بآخر الكلمة الأصلية
#a                                                مثال الهاء والميم في : قلمهم
#a     الألف والتاء في مسلمات ليست لاحقة لأنها جزء من الكلمة وليست كلمة متصلة بها
#a                                     الياء دون نون الوقاية لا تلحق غير الأسماء
#a============================================================================
#a                                      الجذر هو أصل الكلمة بدون الحروف المزيدة
#a    الحروف المزيدة هي حروف سألتمونيها مثل الألف في : قاعد ، والتاء في : فاطمة
#a                                                  مثال الجذر : استخراج = خرج
#a~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#a           ـ ما يزاد من الحروف أولا : ا،م،ه،ت،ن،ي،أ،إ،است،مست،تست،نست،يست،أست
#a                     مت،تت،نت،يت،أت،من،تن،نن،ين،أن
#a                                    ـ ما يزاد من الحروف حشوا : ا،م،ي،ت،و،ء،ن
#a                   ـ ما يزاد من الحروف أخيرا : ا،م،ت،و،ن،ى،ه،ة،ء،ات،ون،وا،ين
#a                          انة،نة،ان،اء،اءات،اوات
#a                         ـ اللام تزاد أخيرا في بضع كلمات والهاء في مادة أهراق
#a============================================================================

import re, sqlite3
import asm_path
import asm_araby

duality_term = ['يد', 'دم', 'فم', 'أب', 'أخ', 'حم', 'هن']

#a حذف السوابق المحتملة-------------------------------------------------------

def _del_prefix(text):
    without_prefix = []
    if text[:2] == 'ال' and text[2] != 'ت':
        if len(text[2:]) >= 3:
            text = text[2:]
            term = 'ismno'
            if text[1] == asm_araby.SHADDA:
                text = text[0]+text[1:]
            without_prefix.append([text, term])
        return without_prefix
    term = 'all'
    without_prefix.append([text, term])
    if text[0] in ['أ', 'ء']:
        if len(text[1:]) >= 3:
            term = 'all'
            without_prefix.append([text[1:], term])
            text = text[1:]
        else: return without_prefix
    if text[0] in ['ف', 'و']:
        if len(text[1:]) >= 3:
            term = 'all'
            without_prefix.append([text[1:], term])
            text = text[1:]
        else: return without_prefix
    if text[:2] in ['سأ', 'سن', 'ست', 'سي']:
        if len(text[1:]) >= 3:
            term = 'fi3l'
            without_prefix.append([text[1:], term])
        return without_prefix
    if text[:2] == 'لل':
        if len(text[2:]) >= 3:
            term = 'ismno'
            without_prefix.append([text[2:], term])
        return without_prefix
    if text[0] in ['ب', 'ك', 'و']:
        if len(text[1:]) >= 3:
            term = 'ism'
            without_prefix.append([text[1:], term])
            text = text[1:]
    elif text[0] == 'ل':
        if len(text) >= 4:
            term = 'all'
            without_prefix.append([text[1:], term])
        return without_prefix
    if text[:2] == 'ال' and text[2] != 'ت':
        if len(text[2:]) >= 3:
            text = text[2:]
            term = 'ismno'
            if text[1] == asm_araby.SHADDA:
                text = text[0]+text[1:]
            without_prefix.append([text, term])
        return without_prefix
    if text in [ 'تالله' ,'تاللّه' , 'تالرحمن']: 
        text = text[1:]
        term = 'ismno'
        without_prefix.append([text, term])
    return without_prefix

#a حذف اللواحق المحتملة-------------------------------------------------------

def _del_suffix(ls):
    without_suffix = []
    text = ls[0]
    term = ls[1]
    without_suffix.append(text)
    if term == 'ismno': 
        if text[-1:] == 'ي':
            if len(text[:-1]) >= 3:
                without_suffix.append(text[:-1])
        elif text[-2:] == 'يّ':
            if len(text[:-2]) >= 3:
                without_suffix.append(text[:-2])
        return without_suffix
    for a in ['ه', 'ها', 'هما', 'هم', 'هنّ', 'هن', 'ك', 'كما', 'كم', 'كنّ', 'كن']:
        if text[-1*len(a):] == a:
            if len(text[:-1*len(a)]) >= 3:
                without_suffix.append(text[:-1*len(a)])
                text = text[:-1*len(a)]
                if term == 'ism': return without_suffix
            else: return without_suffix
    for a in ['ني', 'نا', 'هو', 'ها', 'هما', 'همو', 
              'هنّ','هن', 'ك', 'كما', 'كمو', 'كنّ', 'كن']:
        if text[-1*len(a):] == a:
            if len(text[:-1*len(a)]) >= 3:
                without_suffix.append(text[:-1*len(a)])
                text = text[:-1*len(a)]
            else: return without_suffix
    if text[-1:] == 'ي':
        if term != 'fi3l': 
            if len(text[:-1]) >= 3:
                without_suffix.append(text[:-1])
            return without_suffix
    if text[-2:] == 'يّ':
        if len(text[:-2]) >= 3:
            without_suffix.append(text[:-2])
        return without_suffix
    for a in ['ن', 'نّ', 'تما', 'تم', 'تمو', 'تنّ', 'تن', 'ا', 'ما']:
        if text[-1*len(a):] == a:
            if len(text[:-1*len(a)]) >= 3:
                if term != 'ism':
                    without_suffix.append(text[:-1*len(a)])
            else: return without_suffix
    if text[-1] == 'ت' and text[-2] != 'ا':
        if len(text) > 3:
            without_suffix.append(text[:-1])
    return without_suffix

#a حذف الأحرف الزوائد المحتملة------------------------------------------------

def _del_augment(text):
    text = re.sub('آ', 'أا', text)
    without_augment = [text]
    if len(text) < 3: return without_augment
    if text[:3] in ['تست', 'نست', 'يست', 'أست', 'مست', 'است']:
        if len(text) >= 5:
            without_augment.append(text[3:])
    elif text[:3] in ['متت', 'اتت']:
        if len(text) >= 5:
            without_augment.append('و'+text[3:])
    elif text[0] in ['م', 'ا', 'أ', 'ي', 'ن', 'ت'] and text[2] == 'ت':
        if len(text) >= 5:
            without_augment.append(text[1]+text[3:])
    elif text[:2] in ['تن', 'نن', 'ين', 'أن']:
        if len(text) >= 4:
            without_augment.append(text[2:])
    elif text[:2] in ['من', 'ان', 'مت', 'أت', 'يت', 'نت'] and len(text) >= 5:
        without_augment.append(text[2:])
    if text[0] in ['ت', 'ن', 'ي', 'أ'] and len(text) >= 3:
        without_augment.append(text[1:])
    elif text[0] in ['ا', 'م', 'إ'] and len(text) >= 4:
        without_augment.append(text[1:])
    on_last = []
    for text in without_augment:
        if text[-2:] in ['وا','ون', 'ين', 'ان'] and len(text) > 4:
            on_last.append(text[:-2])
            if text[0] in ['ت', 'ي']:
                on_last.append('و'+text[1:-2])
        if text[-3:] in ['تان', 'تين'] and len(text) == 6:
            on_last.append(text[:-3])
        elif text[-2:] in ['وا','ون', 'ين'] and len(text) == 4:
            on_last.append(text[:-2]+'ا')
        elif text[-2:] == 'ات' and len(text) == 4:
            on_last.append('و'+text[:-2])
        elif text[-4:] in ['اوات', 'اءات'] and len(text) >= 7:
            on_last.append(text[:-4])
        elif text[-3:] in ['انة'] and len(text) >= 6:
            on_last.append(text[:-3])
        elif text[-2:] in ['نة','ات','اء'] and len(text) >= 5:
            on_last.append(text[:-2])
        elif text[-1:] in ['ت'] and len(text) == 3:
            on_last.append(text[:-1]+'ا')
            on_last.append(text[0]+'ا'+text[1])
        elif text[-1:] in ['ن'] and len(text) == 3:
            text = text[0]+'ا'+text[1]
            on_last.append(text)
        elif text[-1:] == 'ة' and len(text) == 3:
            on_last.append('و'+text[:-1])
        if text[-1:] in ['ا', 'ن', 'ت', 'ة', 
                           'ى', 'ه','و', 'ء'] and len(text) >= 4:
            on_last.append(text[:-1])
    without_augment.extend(on_last)
    on_padding = []
    on_padding2 = []
    for text in without_augment:
        if len(text) > 3:
            for a in range(len(text)):
                if text[a] == 'ا' :
                    on_padding.append(text[:a]+text[a+1:])
                elif text[a] in ['و', 'ي'] and a != 0:
                    on_padding2.append(text[:a]+text[a+1:])
    for text in on_padding:
        for a in range(len(text)):
            if len(text) > 3:
                if text[a] in ['و', 'ي'] and a != 0:
                    on_padding2.append(text[:a]+text[a+1:])
    for text in on_padding:
        if len(text) > 3:
            if text[1] == 'ن' :
                on_padding2.append(text[0]+text[2:])
    for text in without_augment:
        if text in ['تري', 'ترا', 'ترو', 'ترى', 'يرى', 'أرى']:
            on_padding.append('رأي')
    on_padding.extend(on_padding2)
    without_augment.extend(on_padding)      
    return without_augment
  
#a قائمة بالجذوع المحتملة----------------------------------------------------

def get_stem(text):
    'return list by all bearable stems'
    if len(text) < 3: return
    stems = []
    if asm_araby.stripTashkeel(text) == 'الله': 
        stems.append('الله')
        return stems
    text = asm_araby.stripHarakat(text)
    without_prefix = _del_prefix(text)
    for a in without_prefix:
        without_suffix = _del_suffix(a)
        for b in without_suffix:
            if len(b) <= 9:
                stems.append(b)
    return stems

#a قائمة بالجذور المحتملة----------------------------------------------------

def is_root(text):
    con = sqlite3.connect(asm_path.MOEJAM_DB)
    cur = con.cursor()
    cur.execute('SELECT term FROM dict WHERE term=?', (text,))
    result = cur.fetchall()
    if len(result) > 0: return True
    else: return False

def get_root(text):
    roots = []
    if len(text) < 3: return
    text = asm_araby.stripHarakat(text)
    stems = get_stem(text)
    all_term = get_stem(text)
    for a in stems:
        if a[-1] == text[-1] != "ي":
            text0 = a+"ي"
            without_augment1 = _del_augment(text0)
            for b in without_augment1:
                if len(b) <= 5 and b not in roots:
                    for c in asm_araby.i3lal(b):
                        all_term.append(c)
                        if is_root(c):
                            if c not in roots:
                                roots.append(c)
        text1, text2 = asm_araby.del_tense(a)
        without_augment1 = _del_augment(text1)
        for b in without_augment1:
            if len(b) <= 5 and b not in roots:
                for c in asm_araby.i3lal(b):
                    all_term.append(c)
                    if is_root(c):
                        if c not in roots:
                            roots.append(c)
                
        if text1 != text2:
            without_augment2 = _del_augment(text2)
            for b in without_augment2:
                if len(b) <= 5 and b not in roots:
                    for c in asm_araby.i3lal(b):
                        all_term.append(c)
                        if is_root(c):
                            if c not in roots:
                                roots.append(c)
    return roots, all_term

#f = 0
#if f == 0:
#    for a in get_stem('التربية'):
#        print (a)
#else:
#    for a in get_root('التربية'):
#        print (a[0])
