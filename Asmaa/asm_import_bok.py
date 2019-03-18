# -*- coding: utf-8 -*-

import sqlite3
from os.path import join, exists
import re, os, sys
import asm_customs
from subprocess import Popen, PIPE


schema_fix_del=re.compile('\(\d+\)')
schema_fix_text=re.compile('Memo/Hyperlink', re.I)
schema_fix_int=re.compile('(Boolean|Byte|double|Numeric|Replication ID|(\w+ )?Integer)', re.I)
        
class DB_from_MDB(object):
    
    def get_cols(self):
        s = re.compile(r'.*\(')
        e = re.compile(r'\);.*')
        new_cmd = re.sub(s, '', self.new_cmd)
        new_cmd = re.sub(e, '', new_cmd)
        new_cmd = re.sub('\s+', ' ', new_cmd)
        new_cmd = re.sub(' ,', ',', new_cmd)
        new_cmd = new_cmd.strip()
        list_cmd = new_cmd.split(',')
        for a in list_cmd:
            a = a.strip()
            col = re.sub('(text|integer)$', '', a)
            col = col.strip()
            self.cols.append(col)
    
    def __init__(self, ifile, tables, db):
        self.cols = []
        self.table_list = []
        self.contents = ''
        self.list_contents = []
        self.ifile = ifile
        self.my_tables = tables
        if exists(db): os.unlink(db)
        self.con = sqlite3.connect(db, isolation_level=None)
        self.cur = self.con.cursor() 
        self.creat_newDB()
        
    def get_tables(self):
        table_names = Popen(["mdb-tables", "-1", self.ifile], stdout=PIPE).communicate()[0]
        self.table_list = table_names.splitlines()
        sys.stdout.flush()
   
    def creat_newDB(self):
        self.get_tables()     
        self.cur.execute("BEGIN;")
        for table in self.table_list:
            if table in self.my_tables or self.my_tables == []:
                new_table = re.sub('^(\d)', 'a', re.sub(' ', '_', table)).lower()
                pipe = Popen(['mdb-schema', '-T', table, self.ifile], 0, stdout=PIPE, env={'MDB_JET3_CHARSET':'cp1256'})
                r = pipe.communicate()[0].decode('utf8')
                cmd = schema_fix_text.sub('TEXT', schema_fix_int.sub('INETEGER', schema_fix_del.sub('', r))).lower()
                cmd = cmd.replace('drop table ', 'drop table if exists ')
                cmd = cmd.replace('\n', ' ')
                cmd = cmd.replace('tb.', '')
                s = re.compile(r'.*create table')
                e = re.compile(r'\);.*')
                self.new_cmd = re.sub(s, 'create table', cmd)
                self.new_cmd = re.sub(u'create table '+table.lower(), u'create table '+new_table, self.new_cmd)
                self.new_cmd = re.sub(e, ');', self.new_cmd)
                self.get_cols()
                for col in self.cols:
                    new_col = re.sub(r'/', '', col)
                    new_col = re.sub('\s+', '_', new_col)
                    self.new_cmd = re.sub(col, new_col, self.new_cmd) 
                self.cur.execute(self.new_cmd)
                #-------------------------------------------------------------------------------
                self.contents = Popen(['mdb-export', '-d', 'new_col', '-R', '\nnew_row', self.ifile, table], 
                           0, stdout=PIPE, env={'MDB_JET3_CHARSET':'cp1256'}).communicate()[0].decode('utf8')
                self.contents = re.sub(r'"', '', self.contents)
                self.list_contents = self.contents.split('new_row')
                for a in range(len(self.list_contents)):
                    if a == 0: 
                        motif = '\n'.join(self.list_contents[0].split('\n')[1:]).split('new_col')
                    else:
                        motif = self.list_contents[a].split('new_col')
                    try:
                        self.cur.execute('INSERT INTO {} VALUES (?{})'.format(new_table,', ?'*(len(motif)-1)), motif)
                    except: continue
        self.con.commit()
        
    def destroy_db(self):
        self.cur.close()
        self.con.close()
        self.contents = None
        self.list_contents = None
        self.cur = None
        self.con = None
        del self.contents
        del self.list_contents
        del self.cur
        del self.con

def add_to_booksDB(con, nm_book, nm_group, is_tafsir):
    cur = con.cursor()
    cur.execute('SELECT id_group FROM groups WHERE tit=?', (nm_group, ))
    id_part = cur.fetchone()[0]
    cur.execute('SELECT id_book FROM books ORDER BY id_book')
    books = cur.fetchall()
    if len(books) == 0: id_book = 1
    else: id_book = books[-1][0]+1
    cur.execute('INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                     (id_book, nm_book, id_part, 0, 0, 0, is_tafsir, 0))
    con.commit()
    
def create_asmaa_bok(con_ls, cur_ls, new_path, inf_book, inf_group, shorts_book, shrooh_book, com_book, inf_page, inf_title, sharh, tafsir, is_tafsir, is_sharh, version):
    if not exists(join(new_path, 'books', inf_group[1])): 
        os.mkdir(join(new_path, 'books', inf_group[1]))
        cur_ls.execute('SELECT id_group FROM groups ORDER BY id_group')
        groups = cur_ls.fetchall()
        if len(groups) == 0: id_group = 1
        else: id_group = groups[-1][0]+1
        cur_ls.execute('INSERT INTO groups VALUES (?, ?, ?, ?)', 
                         (id_group, inf_group[1], 0, len(groups)))
        con_ls.commit()
    db = join(new_path, 'books', inf_group[1], inf_book[1]+'.asm')
    if exists(db): os.unlink(db)
    con = sqlite3.connect(db, isolation_level=None)
    cur = con.cursor() 
    for tb in asm_customs.schema.keys():
        cur.execute('CREATE TABLE IF NOT EXISTS {} ({})'.format(tb, asm_customs.schema[tb]))
    cur.execute("BEGIN;")
    # main table ----------------------------------------------------
    cur.execute('INSERT INTO main VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                (inf_book[1],'', inf_book[2], inf_book[3], inf_book[4], inf_book[5], 0,  inf_book[6], is_tafsir, is_sharh, version))
    # shorts table ----------------------------------------------------
    for stb in shorts_book:
        cur.execute('INSERT INTO shorts VALUES (?, ?)', (stb[0], stb[1]))
    # shrooh table ----------------------------------------------------
    for shb in shrooh_book:
        cur.execute('INSERT INTO shrooh VALUES (?, ?, ?, ?)', (shb[0], shb[1], shb[2], shb[3]))
    # com table ----------------------------------------------------
    for cm in com_book:
        cur.execute('INSERT INTO com VALUES (?, ?)', (cm[0], cm[1]))
    # pages table ----------------------------------------------------
    page_dict = {}
    for pg in range(len(inf_page)):
        if is_sharh == 1:
            msharh = sharh[pg][0]
        else:
            msharh = 0 
        if is_tafsir == 1:
            mtafsir = tafsir[pg]
        else: 
            mtafsir = [0, 0, 0]
        cur.execute('INSERT INTO pages VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (pg+1, inf_page[pg][1], inf_page[pg][2], 
                        inf_page[pg][3], msharh, mtafsir[0], mtafsir[1], mtafsir[2]))
        page_dict[inf_page[pg][0]] = pg+1
    # titles table ----------------------------------------------------
    for ti in range(len(inf_title)):
        try: cur.execute('INSERT INTO titles VALUES (?, ?, ?, ?)', (page_dict[inf_title[ti][0]], inf_title[ti][1], inf_title[ti][2], 
                        inf_title[ti][3]))
        except: continue
    con.commit()
    add_to_booksDB(con_ls, inf_book[1], inf_group[1], is_tafsir)

def export_bok(ifile, cat, con_ls, cur_ls, cur):
    cur.execute('SELECT bkid, bk, cat, betaka, inf, auth, islamshort ,tafseernam FROM main LIMIT 1')
    inf_book = cur.fetchone()
    inf_group = [0, cat]
    cur.execute('SELECT com, id FROM com')
    com_book = cur.fetchall()
    cur.execute('SELECT ramz, nass FROM shorts')
    shorts_book = cur.fetchall()
    cur.execute('SELECT matn, matnid, sharh, sharhid FROM shrooh')
    shrooh_book = cur.fetchall()
    cur.execute('SELECT id, nass, part, page FROM b{}'.format(inf_book[0],))
    inf_page = cur.fetchall()
    if len(shrooh_book) > 0: 
        is_sharh = 1
        sharh = cur.execute('SELECT hno FROM b{}'.format(inf_book[0],)).fetchall()
    else: 
        is_sharh = 0
        sharh = []
    if len(inf_book[7]) > 2:
        tafsir = cur.execute('SELECT sora, aya, na FROM b{}'.format(inf_book[0],)).fetchall()
        is_tafsir = 1
    else: 
        tafsir = []
        is_tafsir = 0
    cur.execute('SELECT id, tit, lvl , sub FROM t{}'.format(inf_book[0],))
    inf_title = cur.fetchall()
    version = 0.1
    create_asmaa_bok(con_ls, cur_ls, asm_customs.MY_DIR, inf_book, inf_group, shorts_book, 
                         shrooh_book, com_book, inf_page, inf_title, sharh, tafsir, is_tafsir, is_sharh, version)

def export_mdb(path, new_path, con_ls, cur_ls, cur_main, cur_sp, cur, bkid):
    cur_main.execute('SELECT bkid, bk, cat, betaka, inf, authno, islamshort ,tafseernam FROM abok WHERE bkid=?', 
                     (bkid, ))
    inf_book = cur_main.fetchone()
    cur_main.execute('SELECT id, name, catord, lvl FROM acat WHERE id=?', (inf_book[2], ))
    inf_group = cur_main.fetchone()
    cur_sp.execute('SELECT com, id FROM com WHERE bk=?', (inf_book[0],))
    com_book = cur_sp.fetchall()
    cur_sp.execute('SELECT ramz, nass FROM shorts WHERE bk=?', (inf_book[0], ))
    shorts_book = cur_sp.fetchall()
    cur_sp.execute('SELECT matn, matnid, sharh, sharhid FROM shrooh WHERE matnid=?', (inf_book[0], ))
    shrooh_book = cur_sp.fetchall()
    cur.execute('SELECT id, nass, part, page FROM book')
    inf_page = cur.fetchall()
    if len(shrooh_book) > 0: 
        is_sharh = 1
        sharh = cur.execute('SELECT hno FROM book').fetchall()
    else: 
        is_sharh = 0
        sharh = []
    if len(inf_book[7]) > 2:
        tafsir = cur.execute('SELECT sora, aya, na FROM book').fetchall()
        is_tafsir = 1
    else: 
        tafsir = []
        is_tafsir = 0
    cur.execute('SELECT id, tit, lvl , sub FROM title')
    inf_title = cur.fetchall()
    version = 0.1
    create_asmaa_bok(con_ls, cur_ls, new_path, inf_book, inf_group, shorts_book, shrooh_book, com_book, 
                     inf_page, inf_title, sharh, tafsir, is_tafsir, is_sharh, version) 
