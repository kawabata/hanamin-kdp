#!/usr/bin/python
# -*- coding: utf-8 -*-

# 花園明朝フォント（実験版）を生成する。
# 注意！ UCS4オプションでコンパイルしたPythonを使うこと！
# 確認方法： ord(u'𠀀’) がちゃんと#x20000 になるかどうか。

import fontforge                                 #Load the module
import psMat
import sys, os, re, fnmatch, codecs

mat1 = psMat.scale(1.05,1.05)
mat2 = psMat.translate(-25,-25)
aalt = {} # add_aalt で異体字を入れる。溢れないよう、数は抑制する。
vari_dir = '/home/kawabata/Dropbox/cvs/kanji-database/variants/'

def make_font (name,style,version):
    global aalt
    font=fontforge.open("./basefont.ttf")
    font.os2_width=1024
    aalt = {}
    # バージョン番号。
    # 上一桁＝（年号-2010）。
    # 下４桁＝ もとデータ（dump.tar.gz）の取得日。下２桁＝フォント生成差分日。
    font.sfntRevision = float(version)
    fullname_en="Hanazono Mincho "+style
    fullname_ja="花園明朝 "+style
    print ("now generating "+fullname_en+" ("+fullname_ja+")")
    # 注意。
    # pid=1,eid=0,lid=0x0   の、id=4 は、自由文字列 (Hanazono-Mincho B) でいいが、
    # pid=3,eid=1,lid=0x409 の、id=4 は、pid=3,eid=1,lid=0x409 の、id=6と同じでなければいけない。
    # fontforgeでは、両方は同じである必要があるので、これは変更できない。
    font.sfnt_names = ((0x409, 0,"Copyright © 2007-2011 GlyphWiki / Kanji Database Project"),
                       (0x409, 1,fullname_en),
                       (0x409, 2,"Regular"),
                       (0x409, 3,version+"-KDP-experimental;"+name),
                       (0x409, 4,name+"-Regular"),
                       #(0x409, 4,fullname_en+" Regular"),
                       (0x409, 5,"Version "+version+" (KDP experimental)"),
                       (0x409, 6,name+"-Regular"),
                       (0x409, 9,"KAMICHI Koichi, KAWABATA Taichi and various contributors"),
                       (0x409,11,"http://glyphwiki.org"),
                       (0x409,14,"http://en.glyphwiki.org/wiki/GlyphWiki:License"),
                       (0x409,16,"Hanazono Mincho"),
                       (0x409,17,style),
                       (0x411, 1,fullname_ja),
                       (0x411, 2,"Regular"),
                       # (0x411, 4,name+"-Regular"), # もしHanaMinBが認識されなくなったらこれをコメントアウトしてみる。
                       (0x411, 5,"Version "+version+" （KDP 実験版）"),
                       (0x409, 9,"上地宏一・川幡太一・その他、GlyphWikiにグリフを投稿して頂いた方々。"),
                       (0x411,14,"http://glyphwiki.org/wiki/GlyphWiki:%E3%83%87%E3%83%BC%E3%82%BF%E3%83%BB%E8%A8%98%E4%BA%8B%E3%81%AE%E3%83%A9%E3%82%A4%E3%82%BB%E3%83%B3%E3%82%B9"),
                       (0x411,16,"花園明朝"),
                       (0x411,17,style))
    font.hasvmetrics=True
    font.vhea_linegap=102
    font.hhea_linegap=102
    # font.cvt=(0,0)
    return font

def add_aalt (glyphB, glyph):
    # glyphBのaaltにglyphを入れる。
    base = glyphB.glyphname
    name = glyph.glyphname
    if (glyphB.unicode > 0x30000):
        print ("add_aalt error!")
        exit()
    if base != name:
        if aalt.has_key(base):
            aalt[base].append(name)
        else:
            aalt[base] = [name]

def resolve_name (name):
    # 名前をシンボリックリンクを解決する。存在しない場合はNoneを返す。
    file = "./work/"+name+".svg"
    if not os.path.isfile(file):
        print ("Warning! not exist-"+file)
        return None
    name = os.path.basename(os.path.realpath(file))[0:-4]
    return name

glyph_count= 0
def import_glyph (font, code, name):
    # 指定されたcode、nameで文字をSVGから読み込む。
    global glyph_count
    glyph=font.createChar(code, name)
    file ="./work/"+name+".svg"
    if os.path.exists(file):
        glyph.importOutlines(file, ("toobigwarn", "removeoverlap"))
        glyph.removeOverlap()
        glyph.simplify(1,("ignoreslopes","ignoreextrema","smoothcurves",
                          "choosehv","nearlyhvlines","mergelines", "forcelines",
                          "setstarttoextremum","removesingletonpoints"))
        glyph.round()
        # glyph.autoHint()
        glyph.autoInstr()
    else:
        print ("Warning! "+file+" does not exist!")
    glyph_count+=1
    glyph.transform(mat1)
    glyph.transform(mat2)
    glyph.width=1024
    glyph.vwidth=1024
    return glyph

dict = {} # 文字名→glyph の辞書データ。エイリアスもあり。
tmp_code=0xf0000
def get_glyph (font, name):
    # 名前のグリフを取得する。
    # (1) 名前がすでに記録済みならば、それを返す。
    # (2) 名前がuXXXX ならば、符号XXXX・名前uXXXXへimport_glyphする。
    # (3) 参照先名が記録済みならばそれを返す。
    # (4) 参照先名がuYYYYならば、符号YYYY・名前uYYYYへimport_glyphする。
    # (5) それ以外ならば、符号tmp_codeを参照先名へimport_glyphする。
    global tmp_code, dict, glyph_count
    if dict.has_key(name):
        return dict[name]
    reobj=re.match("^u([0-9a-f]+)$",name)
    if reobj != None:
        code=int(reobj.group(1),16)
        glyph=import_glyph(font, code,name)
        dict[name]=glyph
        return glyph
    rname = resolve_name (name)
    if dict.has_key(rname):
        return dict[rname]
    reobj=re.match("^u([0-9a-f]+)$",rname)
    if reobj != None:
        code=int(reobj.group(1),16)
    else:
        code=tmp_code
        tmp_code=tmp_code+1
    glyph=import_glyph(font, code,rname)
    dict[rname]=glyph
    return glyph

# main function

# 優先度
# uXXXX
# uXXXX-ue0XXX
# uXXXX-{gtk}
# uXXXX-u3099 (ligature)
# uXXXX-u309a (ligature)
# uXXXX-XX (ssXX)
# [XXXX]-vert
# [XXXX]-itaiji-00X
# [XXXX]-var-00X
# u2ff[0-b]-uxxxxx-uxxxxx- IDS

# u[3-9f]xxx のグリフのフォント生成
def make_base (font, reg):
    print ("base characters")
    reobj = re.compile(reg)
    count = 0
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count += 1
            base = m.group(1)
            get_glyph(font, base)
    print ("base: total=%d" % (count,))

def add_lookup(font, feat, type):
    font.addLookup(feat, type, (), ((feat, (("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")),
                                            ("DFLT",("JAN ")),("hani",("JAN ")),("kana",("JAN ")),
                                            ("DFLT",("ZHS ")),("hani",("ZHS ")),("kana",("ZHS ")),
                                            ("DFLT",("ZHT ")),("hani",("ZHT ")),("kana",("ZHT ")),
                                            ("DFLT",("KOR ")),("hani",("KOR ")),("kana",("KOR ")))),))
                                 #(("zhcn",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
    font.addLookupSubtable(feat,feat+"1")
    
    print (feat+"1 subtable created.")

def add_posSub(glyph, feat, val):
    print (glyph.glyphname, feat, val)
    glyph.addPosSub(feat, val)

def make_cdp (font):
    # CDPすべての文字をPUAにインポートする。
    # cdpの文字名は維持したまま、外字に変換する。
    reobj = re.compile("(cdp-([0-9a-f]{2})([0-9a-f]{2}))\\.svg$")
    count = 0
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count += 1
            name   = m.group(1)
            big5_h = int(m.group(2),16)
            big5_l = int(m.group(3),16)
            uni    = 0xeeb8 + (big5_h - 0x81) * 157 + ((big5_l - 0x40) if (big5_l < 0x80) else (big5_l - 0x62))
            glyph  = import_glyph (font, uni, name)
            dict["u%04x" % (uni,)] = glyph
            dict[name]=glyph # alias
    print ("cdp: total=%d" % (count,))

def make_ivs (font, reg):
    print("ivs/cv17-cv99")
    for x in range(00,99):
        add_lookup(font, "cv%02d" % (x+1,),"gsub_single")
    reobj = re.compile(reg)
    count = 0
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count+= 1
            name  = m.group(1)
            base  = m.group(2)
            vs    = int(m.group(3),16)
            glyph = get_glyph(font, name)
            glyphB= get_glyph(font, base)
            #altuni= glyphB.altuni
            altuni= glyph.altuni
            if (glyphB.unicode > 0x2d000):
                print ("Error! irregular IVS!", glyphB.glyphname)
                exit()
            if altuni == None:
                #glyphB.altuni = ((glyph.unicode,vs,0),)
                glyph.altuni = ((glyphB.unicode,vs,0),)
            else:
                #glyphB.altuni = altuni+((glyph.unicode,vs,0),)
                glyph.altuni = altuni+((glyphB.unicode,vs,0),)
            add_posSub(glyphB, ("cv%02d1" % (vs-0xe0100+17,)), glyph.glyphname)
            add_aalt(glyphB,glyph)
    print ("ivs/cvXX: total=%d" % (count,))

def make_gtjk (font,reg):
    print ("gtjk")
    reobj = re.compile(reg)
    count_g = 0
    count_t = 0
    count_j = 0
    count_k = 0
    #font.addLookup("zhtw","gsub_single",(),(("zhtw",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
    #                                        # ("locl",(("hani",("ZHT ")),))))
    font.addLookup("zhcn","gsub_single",(),(("zhcn",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")),
                                                     ("DFLT",("JAN ")),("hani",("JAN ")),("kana",("JAN ")),
                                                     ("DFLT",("ZHS ")),("hani",("ZHS ")),("kana",("ZHS ")),
                                                     ("DFLT",("ZHT ")),("hani",("ZHT ")),("kana",("ZHT ")),
                                                     ("DFLT",("KOR ")),("hani",("KOR ")),("kana",("KOR ")))),
                                            ("locl",(("DFLT",("ZHS ")),("hani",("ZHS ")),("kana",("ZHS "))))))
    font.addLookup("zhtw","gsub_single",(),(("zhtw",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")),
                                                     ("DFLT",("JAN ")),("hani",("JAN ")),("kana",("JAN ")),
                                                     ("DFLT",("ZHS ")),("hani",("ZHS ")),("kana",("ZHS ")),
                                                     ("DFLT",("ZHT ")),("hani",("ZHT ")),("kana",("ZHT ")),
                                                     ("DFLT",("KOR ")),("hani",("KOR ")),("kana",("KOR ")))),
                                            ("locl",(("DFLT",("ZHT ")),("hani",("ZHT ")),("kana",("ZHT "))))))
    font.addLookup("jajp","gsub_single",(),(("jajp",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")),
                                                     ("DFLT",("JAN ")),("hani",("JAN ")),("kana",("JAN ")),
                                                     ("DFLT",("ZHS ")),("hani",("ZHS ")),("kana",("ZHS ")),
                                                     ("DFLT",("ZHT ")),("hani",("ZHT ")),("kana",("ZHT ")),
                                                     ("DFLT",("KOR ")),("hani",("KOR ")),("kana",("KOR ")))),
                                            ("locl",(("DFLT",("JAN ")),("hani",("JAN ")),("kana",("JAN "))))))
    font.addLookup("kokr","gsub_single",(),(("kokr",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")),
                                                     ("DFLT",("JAN ")),("hani",("JAN ")),("kana",("JAN ")),
                                                     ("DFLT",("ZHS ")),("hani",("ZHS ")),("kana",("ZHS ")),
                                                     ("DFLT",("ZHT ")),("hani",("ZHT ")),("kana",("ZHT ")),
                                                     ("DFLT",("KOR ")),("hani",("KOR ")),("kana",("KOR ")))),
                                            ("locl",(("DFLT",("KOR ")),("hani",("KOR ")),("kana",("KOR "))))))
    font.addLookupSubtable("zhcn","zhcn1")
    font.addLookupSubtable("zhtw","zhtw1")
    font.addLookupSubtable("jajp","jajp1")
    font.addLookupSubtable("kokr","kokr1")

    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name  = m.group(1)
            base  = m.group(2)
            region= m.group(3)
            glyph = get_glyph(font, name)
            glyphB= get_glyph(font, base)
            if region == "g":
                count_g += 1
                add_posSub(glyphB,"zhcn1",glyph.glyphname)
            elif region == "t":
                count_t += 1
                add_posSub(glyphB,"zhtw1",glyph.glyphname)
            elif region == "j":
                count_j += 1
                add_posSub(glyphB,"jajp1",glyph.glyphname)
            elif region == "k":
                count_k += 1
                add_posSub(glyphB,"kokr1",glyph.glyphname)
            else:
                print ("region not found")
                exit()
            add_aalt(glyphB,glyph)
    print ("uXXXX-g: total=%d" % (count_g,))
    print ("uXXXX-t: total=%d" % (count_t,))
    print ("uXXXX-j: total=%d" % (count_j,))
    print ("uXXXX-k: total=%d" % (count_k,))

def make_vert (font, reg):
    reobj = re.compile(reg)
    count = 0
    add_lookup(font, "vert","gsub_single")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count+= 1
            name  = m.group(1)
            base  = m.group(2)
            glyph = get_glyph(font, name)
            glyphB= get_glyph(font, base)
            add_posSub(glyphB,"vert1",glyph.glyphname)
            add_aalt(glyphB,glyph)
    print ("vert: total=%d" % (count,))

def make_ssXX (font, reg):
    reobj = re.compile(reg)
    count = 0
    print("ss01-ss20")
    for x in range(15):
        add_lookup(font, "ss%02d" % (x+1,), "gsub_single")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count+= 1
            name  = m.group(1)
            base  = m.group(2)
            style = m.group(3)
            glyph = get_glyph(font, name)
            glyphB= get_glyph(font, base)
            add_posSub(glyphB,"ss"+style+"1",glyph.glyphname)
            add_aalt(glyphB,glyph)
    print ("ssXX: total=%d" % (count,))

def make_salt (font, reg):
    reobj = re.compile(reg)
    count = 0
    print("salt")
    add_lookup(font, "salt","gsub_alternate")
    vars={}
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count+= 1
            name  = m.group(1)
            base  = m.group(2)
            vari  = int(m.group(3))
            glyph = get_glyph(font, name)
            glyphB= get_glyph(font, base)
            if vars.has_key(glyphB.glyphname):
                vars[glyphB.glyphname][vari]=glyph.glyphname
            else:
                vars[glyphB.glyphname] = {vari: glyph.glyphname}
    for key in vars.keys():
        vals = vars[key].values()
        vals.sort()
        if dict.has_key(key):
            if (dict[key].glyphname != key):
                print ("Warning! dict[key]="+dict[key].glyphname+",key="+key)
            add_posSub(dict[key],"salt1",tuple(vals))
        else:
            print "salt error.  no such key="+key
        for val in vals:
            add_aalt(dict[key],dict[val])
    print ("salt: total=%d" % (count,))

def make_trad (font, reg):
    reobj = re.compile(reg)
    count = 0
    print("trad")
    add_lookup(font, "trad","gsub_alternate")
    vars={}
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count+= 1
            name  = m.group(1)
            base  = m.group(2)
            vari  = int(m.group(3))
            glyph = get_glyph(font, name)
            glyphB= get_glyph(font, base)
            if vars.has_key(glyphB.glyphname):
                vars[glyphB.glyphname][vari]=glyph.glyphname
            else:
                vars[glyphB.glyphname] = {vari: glyph.glyphname}
    for key in vars.keys():
        vals = vars[key].values()
        vals.sort()
        #add_posSub(font[key],"trad1",tuple(vals))
        #for val in vals:
        #    add_aalt(font[key],font[val])
        add_posSub(dict[key],"trad1",tuple(vals))
        for val in vals:
            add_aalt(dict[key],dict[val])
    print ("trad: total=%d" % (count,))

def make_ccmp (font, reg):
    print("ccmp")
    reobj = re.compile(reg)
    count = 0
    add_lookup(font, "ccmp", "gsub_ligature")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count += 1
            name   = m.group(1)
            ucs_seq= m.group(2)
            glyph  = get_glyph(font, name)
            ids    = tuple(map ((lambda x: get_glyph(font, x).glyphname), ucs_seq.split("-")))
            add_posSub(glyph, "ccmp1",ids)
    print ("ccmp: total=%d" % (count,))

def make_liga (font, reg):
    print("liga")
    reobj = re.compile(reg)
    count = 0
    add_lookup(font, "liga", "gsub_ligature")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            count += 1
            name   = m.group(1)
            glyph  = get_glyph(font, name)
            ids    = tuple(map ((lambda x: get_glyph(font, x).glyphname), name.split("-")))
            add_posSub(glyph, "liga1",ids)
    print ("liga: total=%d" % (count,))

# 異体字データベースから異体字情報を取り込む。
def make_variants(font,regex1,regex2,regex3):
    global vari_dir
    reobj1 = re.compile(u"^("+regex1+u"),"+regex3+u",("+regex2+u")", re.UNICODE)
    reobj2 = re.compile(u"^("+regex2+u"),"+regex3+u",("+regex1+u")", re.UNICODE)
    for file in os.listdir(vari_dir):
        file = vari_dir+file
        if not (fnmatch.fnmatch(file,"*.txt")):
            continue
        print("reading "+file)
        f = codecs.open(file,"r",'utf-8')
        lines = f.readlines()
        for line in lines:
            #line = line.rstrip().decode('utf-8')
            #line = unicode(line.rstrip(),'utf-8')
            m1 = reobj1.match(line)
            m2 = reobj2.match(line)
            if (m1):
                code1 = ord(m1.group(1))
                code2 = ord(m1.group(2))
            elif (m2):
                code1 = ord(m2.group(1))
                code2 = ord(m2.group(2))
            else:
                continue
            glyph1 = get_glyph(font, "u%x" % (code1,))
            glyph2 = get_glyph(font, "u%x" % (code2,))
            print "%s,%s" % (glyph1.glyphname, glyph2.glyphname)
            add_aalt(glyph1, glyph2)
            add_aalt(glyph2, glyph1)
            line = f.readline()
        f.close()

def make_aalt(font):
    print("aalt")
    count = 0
    add_lookup(font, "aalt", "gsub_alternate")
    for key in aalt.keys():
        vals=aalt[key]
        vals=list(set(vals))
        vals.sort()
        count += len(vals)
        if dict.has_key(key):
            if (dict[key].glyphname != key):
                print ("Warning! dict[key]="+dict[key].glyphname+",key="+key)
            add_posSub(dict[key],"aalt1",tuple(vals))
        else:
            print "aalt error.  no such key="+key
    print ("aalt: total=%d" % (count,))

def fini_font (font,file_name):
    print("total import glyph=%d" % (glyph_count,))
    print("Generating "+file_name+"....")
    font.ascent=880
    font.descent=144
    font.generate(file_name, flags=("opentype","no-hints","round"))
    print("...finished.")
    print("Generating "+file_name+".sfd ....")
    font.generate(file_name+".sfd")
    font.close

def make_font_test (version):
    font=make_font("HanaMinTest", "Test", version)
    make_base(font, "^(u[234][0f][0-9a-f]{2})\\.svg$") # debug
    #make_cdp (font)
    make_ivs (font, "^((u[34][0f][0-9a-f]{2})-u(e01[01][0-9a-f]))\\.svg$")
    #make_gtjk(font, "^((u[3][0f][0-9a-f]{2})-([gtkj]))\\.svg$")
    #make_vert(font, "^((u[3][0f][0-9a-f]{2})-vert)\\.svg$")
    #make_ssXX(font, "^((u[3][0f][0-9a-f]{2})-([01][0-9]))\\.svg$")
    #make_salt(font, "^((u[3][0f][0-9a-f]{2})-var-([0-9]{3}))\\.svg$")
    #make_trad(font, "^((u[3][0f][0-9a-f]{2})-itaiji-([0-9]{3}))\\.svg$")
    #make_ccmp(font, "^((?:kumimoji-)?((u2ff[0-b])(-u[0-9a-f]{4,5})+))\\.svg$")
    #make_liga(font,"^(u[0-9a-f]{4,5}-(u20dd|(u309[9a])))\\.svg$")
    make_variants(font, u"[㐀-㔀]", u"[㐀-㔀]",u".*?simplified.*?")
    make_aalt(font)
    fini_font(font,"HanaMinTest.ttf")

def make_font_a (version):
    font=make_font("HanaMinA", "A", version)
    make_base(font,"^((u[0-9a-f][0-9a-f]{3}))\\.svg$")
    make_cdp (font)
    make_ivs (font,"^((u[2-9f][0-9a-f]{3})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk(font,"^((u[2-9f][0-9a-f]{3})-([gtk]))\\.svg$")
    make_vert(font,"^((u[2-9f][0-9a-f]{3})-vert)\\.svg$")
    make_ssXX(font,"^((u[2-9f][0-9a-f]{3})-([01][0-9]))\\.svg$")
    make_salt(font,"^((u[2-9f][0-9a-f]{3})-var-([0-9]{3}))\\.svg$")
    make_trad(font,"^((u[2-9f][0-9a-f]{3})-itaiji-([0-9]{3}))\\.svg$")
    make_ccmp(font,"^((?:kumimoji-)?((u2ff[0-b])(-u[0-9a-f]{4,5})+))\\.svg$")
    make_liga(font,"^(u[0-9a-f]{4,5}-(u20dd|(u309[9a])))\\.svg$")
    #make_variants(font, u"[一-﫿]", u"[一-﫿]",u".*?simplified.*?")
    make_variants(font, u"[一-﫿]", u"[一-﫿]",u".*?jisx.*?") # これだけならOK。
    #make_variants(font, u"[一-﫿]", u"[一-﫿]",u"[^,]+")
    #make_variants(font, u"[一-﫿]", u"[㐀-﫿𠀀-𯿽]",u"[^,]+")
    make_aalt(font)
    fini_font(font,"HanaMinA.ttf")

def make_font_b (version):
    font=make_font("HanaMinB", "B", version)
    # magic characters to be included
    get_glyph(font, "u4e00")
    get_glyph(font, "u3042")
    get_glyph(font, "u30a2") # This is by Ken Lunde.
    make_base(font,"^((u2[0-9a-f]{4}))\\.svg$")
    make_ivs (font,"^((u2[0-9a-f]{4})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk(font,"^((u2[0-9a-f]{4})-([gtkj]))\\.svg$")
    make_vert(font,"^((u2[0-9a-f]{4})-vert)\\.svg$")
    make_ssXX(font,"^((u2[0-9a-f]{4})-([01][0-9]))\\.svg$")
    make_salt(font,"^((u2[0-9a-f]{4})-var-([0-9]{3}))\\.svg$")
    make_trad(font,"^((u2[0-9a-f]{4})-itaiji-([0-9]{3}))\\.svg$")
    make_variants(font, u"[一-﫿]", u"[㐀-䷿𠀀-𯿽]",u".*?simplified.*?")
    make_variants(font, u"[一-﫿]", u"[㐀-䷿𠀀-𯿽]",u".*?jisx.*?")
    make_aalt(font)
    fini_font(font,"HanaMinB.ttf")

if (len(sys.argv) != 3):
    print ("Error! no proper argument!  TYPE and VERSION!")
elif (sys.argv[1] == "Test"):
    make_font_test(sys.argv[2])
elif (sys.argv[1] == "A"):
    make_font_a(sys.argv[2])
elif (sys.argv[1] == "B"):
    make_font_b(sys.argv[2])
else:
    print ("Error! not supported argument. "+sys.argv[1])
