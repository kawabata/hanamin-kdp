#!/usr/bin/python
# -*- coding: utf-8 -*-

# 花園明朝フォント（実験版）を生成する。

import fontforge                                 #Load the module
import psMat
import os, re

base=fontforge.open("./basefont.ttf.ivs")
mat1 = psMat.scale(1.05,1.05)
mat2 = psMat.translate(-25,-25)
aalt = {} # add_aalt で異体字を入れる。文字溢れがおきないよう、数は抑制する。

def make_font (name,style):
    global base, aalt
    base.close()
    base=fontforge.open("./basefont.ttf.ivs")
    base.os2_width=1024
    aalt = {}
    fullname_en="Hanazono Mincho "+style
    fullname_jp="花園明朝 "+style
    base.sfnt_names = ((0x409, 0,"Copyright &#169; 2007-2011 GlyphWiki / Kanji Database Project"),
                       (0x409, 1,fullname_en),
                       (0x409, 2,"Regular"),
                       (0x409, 3,"1.001-KDP-beta;"+name),
                       (0x409, 4,fullname_en+" Regular"),
                       (0x409, 5,"Version 001.001 (KDP) beta"),
                       (0x409, 6,name+"-Regular"),
                       (0x409, 9,"Kamichi Koichi and various contributors"),
                       (0x409,11,"http://glyphwiki.org"),
                       (0x409,14,"http://glyphwiki.org/wiki/GlyphWiki:%E3%83%87%E3%83%BC%E3%82%BF%E3%83%BB%E8%A8%98%E4%BA%8B%E3%81%AE%E3%83%A9%E3%82%A4%E3%82%BB%E3%83%B3%E3%82%B9"),
                       (0x409,16,"Hanazono Mincho"),
                       (0x409,17,style),
                       (0x411, 1,fullname_en),
                       (0x411, 2,"Regular"),
                       (0x411,16,"花園明朝"),
                       (0x411,17,style))
    #base.horizontalBaseline = (("icfb", "icft", "ideo", "romn"),
    #                           (("DFLT", "icfb", (-120,),()),
    #                            ("DFLT", "icft", (-856,),()),
    #                            ("DFLT", "ideo", (-144,),()),
    #                            ("DFLT", "romn", (-0,),())))
    #base.verticalBaseline = (("icfb", "icft", "ideo", "romn"),
    #                           (("DFLT", "icfb", (24,),()),
    #                            ("DFLT", "icft", (1000,),()),
    #                            ("DFLT", "ideo", (0,),()),
    #                            ("DFLT", "romn", (144,),())))
    base.hasvmetrics=True
    base.vhea_linegap=102

def add_aalt (glyphX, glyph):
    # 名前のグリフにvarsを入れる。varsは単独でもリストでもOK.
    nameX = glyphX.glyphname
    name = glyph.glyphname
    if nameX != name:
        if aalt.has_key(nameX):
            aalt[nameX].append(name)
        else:
            aalt[nameX] = [name]

def resolve_name (name):
    # 名前をシンボリックリンクを解決する。存在しない場合はNoneを返す。
    file = "./work/"+name+".svg"
    if not os.path.isfile(file):
        print ("Warning! not exist-"+file)
        return None
    name = os.path.basename(os.path.realpath(file))[0:-4]
    return name

def import_glyph (code, name):
    # 指定された文字コード、名前で文字をSVGから読み込む。
    global dict
    glyph=base.createChar(code, name)
    glyph.importOutlines("./work/"+name+".svg", ("removeOverlap"))
    glyph.simplify()
    glyph.transform(mat1)
    glyph.transform(mat2)
    glyph.width=1024
    glyph.vwidth=1024
    glyph.round()
    glyph.autoInstr()
    return glyph

dict = {}
tmp_code=0xf0000
def get_glyph (name):
    # 名前のグリフを取得する。
    # (1) 名前がすでに記録済みならば、それを返す。
    # (2) 名前がuXXXX ならば、符号XXXX・名前uXXXXへimport_glyphする。
    # (3) 参照先名が記録済みならばそれを返す。
    # (4) 参照先名がuYYYYならば、符号YYYY・名前uYYYYへimport_glyphする。
    # (5) それ以外ならば、符号tmp_codeを参照先名へimport_glyphする。
    global tmp_code, dict
    if dict.has_key(name):
        return dict[name]
    reobj=re.match("^u([0-9a-f]+)$",name)
    if reobj != None:
        code=int(reobj.group(1),16)
        glyph=import_glyph(code,name)
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
        # print("get_glyph/tmp",code,name,rname)
    glyph=import_glyph(code,rname)
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
def make_base (reg):
    reobj = re.compile(reg)
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name = m.group(1)
            get_glyph(name)

## IVS
def make_ivs (reg):
    reobj = re.compile(reg)
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name  = m.group(1)
            #code  = int(m.group(2),16)
            nameX = "u"+m.group(2)
            vs    = int(m.group(3),16)
            glyph = get_glyph(name)
            glyphX= get_glyph(nameX)
            #altuni= base[code].altuni
            altuni= glyphX.altuni
            if (glyphX.unicode > 0x2d000):
                print ("Warning! irregular IVS!", glyphX.glyphname)
            if altuni == None:
                glyphX.altuni = ((glyph.unicode,vs,0),)
            else:
                glyphX.altuni = altuni+((glyph.unicode,vs,0),)
            add_aalt(glyphX,glyph)

## gtk
def make_gtjk (reg):
    reobj = re.compile(reg)
    base.addLookup("zhcn","gsub_single",(),(("zhcn",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
                                            # ("locl",(("hani",("ZHS ")),))))
    base.addLookup("zhtw","gsub_single",(),(("zhtw",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
                                            # ("locl",(("hani",("ZHT ")),))))
    base.addLookup("jajp","gsub_single",(),(("jajp",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
                                            # ("locl",(("hani",("JAN ")),))))
    base.addLookup("kokr","gsub_single",(),(("kokr",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
                                            # ("locl",(("hani",("KOR ")),))))
    base.addLookupSubtable("zhcn","zhcn1")
    base.addLookupSubtable("zhtw","zhtw1")
    base.addLookupSubtable("jajp","jajp1")
    base.addLookupSubtable("kokr","kokr1")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name  = m.group(1)
            nameX = m.group(2)
            region= m.group(3)
            glyph = get_glyph(name)
            glyphX= get_glyph(nameX)
            if region == "g":
                glyphX.addPosSub("zhcn1",glyph.glyphname)
            elif region == "t":
                glyphX.addPosSub("zhtw1",glyph.glyphname)
            elif region == "j":
                glyphX.addPosSub("jajp1",glyph.glyphname)
            elif region == "k":
                glyphX.addPosSub("kokr1",glyph.glyphname)
            else:
                print ("region not found")
            # add_aalt(glyphX,glyph)

## vert
def make_vert (reg):
    reobj = re.compile(reg)
    base.addLookup("vert","gsub_single",(),(("vert",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
    base.addLookupSubtable("vert","vert1")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name  = m.group(1)
            nameX = m.group(2)
            glyph = get_glyph(name)
            glyphX= get_glyph(nameX)
            base[nameX].addPosSub("vert1",glyph.glyphname)
            # add_aalt(glyphX,glyph)

def make_ssXX (reg):
    reobj=re.compile(reg)
    print("ss01-ss20")
    for x in range(15):
        base.addLookup("ss%02d" % (x+1,),
                       "gsub_single",(),
                       (("ss%02d" % (x+1,),(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
    for x in range(15):
        base.addLookupSubtable("ss%02d" % (x+1,), "ss%02d1" % (x+1,))
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name  = m.group(1)
            nameX = m.group(2)
            style = m.group(3)
            glyph = get_glyph(name)
            glyphX= get_glyph(nameX)
            glyphX.addPosSub("ss"+style+"1",glyph.glyphname)
            # add_aalt(glyphX,glyph)

## salt
def make_salt (reg):
    reobj=re.compile(reg)
    print("salt")
    base.addLookup("salt","gsub_alternate",(),(("salt",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
    base.addLookupSubtable("salt","salt1")
    dict={}
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name   = m.group(1)
            nameX  = m.group(2)
            variant= int(m.group(3))
            glyph  = get_glyph(name)
            glyphX = get_glyph(nameX)
            try:
                dict[glyphX.glyphname][variant]=glyph.glyphname
            except KeyError:
                dict[glyphX.glyphname] = {variant: glyph.glyphname}
                
    for key in dict.keys():
        vals = dict[key].values()
        vals.sort()
        print ("variants:",vals)
        base[key].addPosSub("salt1",tuple(vals))
        #for val in vals:
            # add_aalt(base[key],base[val])

## trad
def make_trad (reg):
    reobj=re.compile(reg)
    print("trad")
    base.addLookup("trad","gsub_alternate",(),(("trad",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
    base.addLookupSubtable("trad","trad1")
    dict={}
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name   = m.group(1)
            nameX  = m.group(2)
            variant= int(m.group(3))
            glyph  = get_glyph(name)
            glyphX = get_glyph(nameX)
            try:
                dict[glyphX.glyphname][variant]=glyph.glyphname
            except KeyError:
                dict[glyphX.glyphname] = {variant: glyph.glyphname}
    
    for key in dict.keys():
        vals = dict[key].values()
        vals.sort()
        print ("itaiji2:",vals)
        base[key].addPosSub("trad1",tuple(vals))
        #for val in vals:
            # add_aalt(base[key],base[val])

def make_aalt():
    print("aalt")
    base.addLookup("aalt","gsub_alternate",(),(("aalt",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
    base.addLookupSubtable("aalt","aalt1")
    for key in aalt.keys():
        vals=aalt[key]
        vals.sort()
        print ("aalt",vals)
        base[key].addPosSub("aalt1",tuple(vals))

## liga
def make_liga (reg):
    print("liga")
    reobj = re.compile(reg)
    base.addLookup("liga","gsub_ligature",(),(("liga",(("DFLT",("dflt")),("hani",("dflt")),("kana",("dflt")))),))
    base.addLookupSubtable("liga","liga1")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name   = m.group(1)
            glyph  = get_glyph(name)
            ids    = tuple(map ((lambda x: get_glyph(x).glyphname), name.split("-")))
            print ("liga",ids)
            glyph.addPosSub("liga1",ids)

def finish_font (file_name):
    font.generate(file_name), flags=("opentype","no-hints","round"))
    font.close
    dict={}

def make_font_test ():
    font=make_font("HanaMinTest", "Test")
    make_base(font,"^(u([235][0f][0-9a-f]{2}))\\.svg$") # debug
    make_ivs (font, "^(u([35][0f][0-9a-f]{2})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk(font, "^((u[35][0f][0-9a-f]{2})-([gtkj]))\\.svg$")
    make_vert(font, "^((u[35][0f][0-9a-f]{2})-vert)\\.svg$")
    make_ssXX(font, "^((u[35][0f][0-9a-f]{2})-([01][0-9]))\\.svg$")
    make_salt(font, "^((u[35][0f][0-9a-f]{2})-var-([0-9]{3}))\\.svg$")
    make_trad(font, "^((u[35][0f][0-9a-f]{2})-itaiji-([0-9]{3}))\\.svg$")
    make_liga(font,"^((u2ff[0-b])(-u[0-9a-f]{4,5})+)\\.svg$")
    make_aalt(font)
    print("Generate HanaMinTest.ttf.")
    font=finish_font("HanaMinTest.ttf")
    base.generate("HanaMinTest.ttf",flags=("opentype","no-hints","round"))
    base.close()
    dict = {}

def make_font_a ():
    make_font("HanaMinA", "A")
    make_base("^(u([2-9f][0-9a-f]{3}))\\.svg$")
    make_ivs ("^(u([2-9f][0-9a-f]{3})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk("^((u[2-9f][0-9a-f]{3})-([gtkj]))\\.svg$")
    make_vert("^((u[2-9f][0-9a-f]{3})-vert)\\.svg$")
    make_ssXX("^((u[2-9f][0-9a-f]{3})-([01][0-9]))\\.svg$")
    make_salt("^((u[2-9f][0-9a-f]{3})-var-([0-9]{3}))\\.svg$")
    make_trad("^((u[2-9f][0-9a-f]{3})-itaiji-([0-9]{3}))\\.svg$")
    make_liga("^((u2ff0)(-u[0-9a-f]{4,5})+)\\.svg$")
    make_aalt()
    print("Generate HanaMinA.ttf file.")
    base.generate("HanaMinA.ttf",flags=("opentype","no-hints","round"))
    base.close()
    dict = {}

def make_font_b ():
    make_font("HanaMinB", "B")
    make_base("^(u([12][0-9a-f]{4}))\\.svg$")
    make_ivs ("^(u([12][0-9a-f]{4})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk("^((u[12][0-9a-f]{4})-([gtkj]))\\.svg$")
    make_vert("^((u[12][0-9a-f]{4})-vert)\\.svg$")
    make_ssXX("^((u[12][0-9a-f]{4})-([01][0-9]))\\.svg$")
    make_salt("^((u[12][0-9a-f]{4})-var-([0-9]{3}))\\.svg$")
    make_trad("^((u[12][0-9a-f]{4})-itaiji-([0-9]{3}))\\.svg$")
    make_liga("^((u2ff[1-b])(-u[0-9a-f]{4,5})+)\\.svg$")
    make_aalt()
    print("Generate HanaMinB.ttf file.")
    base.generate("HanaMinB.ttf",flags=("opentype","no-hints","round"))
    base.close()
    dict = {}

make_font_test()
#make_font_a()
#make_font_b()
# TODO:
# 横書き漢文句読点重ねあわせ機能
# 縦書き漢文句読点重ねあわせ機能
