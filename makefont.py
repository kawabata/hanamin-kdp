#!/usr/bin/python
# -*- coding: utf-8 -*-

# 花園明朝フォント（実験版）を生成する。

import fontforge                                 #Load the module
import psMat
import os, re

base=fontforge.open("./basefont.ttf.ivs")
mat1 = psMat.scale(1.05,1.05)
mat2 = psMat.translate(-25,-25)

def make_font (name,fullname):
    base=fontforge.open("./basefont.ttf.ivs")
    base.os2_width=1024
    base.fontname=name
    base.fullname=fullname
    base.hasvmetrics=True
    base.vhea_linegap=102

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
    glyph.importOutlines("./work/"+name+".svg", ("removeoverlap"))
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
    # (5) それ以外ならば、符号tmp_codez名前を参照先名へimport_glyphする。
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
        print("get_glyph/tmp",code,name,rname)
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
            code  = int(m.group(2),16)
            vs    = int(m.group(3),16)
            glyph = get_glyph(name)
            altuni= base[code].altuni
            if altuni == None:
                base[code].altuni = ((glyph.unicode,vs,0),)
            else:
                base[code].altuni = altuni+((glyph.unicode,vs,0),)

## gtk
def make_gtjk (reg):
    reobj = re.compile(reg)
    base.addLookup("zhcn","gsub_single",(),(("locl",(("hani",("ZHS ")),)),("zhcn",(("hani",("dflt")),))))
    base.addLookup("zhtw","gsub_single",(),(("locl",(("hani",("ZHT ")),)),("zhtw",(("hani",("dflt")),))))
    base.addLookup("jajp","gsub_single",(),(("locl",(("hani",("JAN ")),)),("jajp",(("hani",("dflt")),))))
    base.addLookup("kokr","gsub_single",(),(("locl",(("hani",("KOR ")),)),("kokr",(("hani",("dflt")),))))
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

## vert
def make_vert (reg):
    reobj = re.compile(reg)
    base.addLookup("vert","gsub_single",(),(("vert",(("hani",("dflt")),("kana",("dflt")))),))
    base.addLookupSubtable("vert","vert1")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name  = m.group(1)
            nameX = m.group(2)
            glyph = get_glyph(name)
            glyphX= get_glyph(nameX)
            base[nameX].addPosSub("vert1",glyph.glyphname)

def make_ssXX (reg):
    reobj=re.compile(reg)
    print("ss01-ss20")
    for x in range(15):
        base.addLookup("ss%02d" % (x+1,),
                       "gsub_single",(),
                       (("ss%02d" % (x+1,),(("hani",("dflt")),("kana",("dflt")))),))
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

## salt
def make_salt (reg):
    reobj=re.compile(reg)
    print("salt")
    base.addLookup("salt","gsub_alternate",(),(("salt",(("hani",("dflt")),("kana",("dflt")))),))
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
        print ("variants:",dict[key].values())
        base[key].addPosSub("salt1",tuple(dict[key].values()))

## aalt
def make_aalt (reg):
    reobj=re.compile(reg)
    print("aalt")
    base.addLookup("aalt","gsub_alternate",(),(("aalt",(("hani",("dflt")),("kana",("dflt")))),))
    base.addLookupSubtable("aalt","aalt1")
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
        print ("itaiji:",dict[key].values())
        base[key].addPosSub("aalt1",tuple(dict[key].values()))
    
## liga
def make_liga (reg):
    print("liga")
    reobj = re.compile(reg)
    base.addLookup("liga","gsub_alternate",(),(("liga",(("hani",("dflt")),("kana",("dflt")))),))
    base.addLookupSubtable("liga","liga1")
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name   = m.group(1)
            glyph  = get_glyph(name)
            ids    = tuple(map ((lambda x: get_glyph(x).glyphname), name.split("-")))
            print ("liga",ids)
            glyph.addPosSub("liga1",ids)

def make_font_debug ():
    make_font("HanaMinTest", "Hanazono Mincho Test")
    make_base("^(u([235][0f][0-9a-f]{2}))\\.svg$") # debug
    make_ivs ( "^(u([35][0f][0-9a-f]{2})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk( "^((u[35][0f][0-9a-f]{2})-([gtkj]))\\.svg$")
    make_vert( "^((u[35][0f][0-9a-f]{2})-vert)\\.svg$")
    make_ssXX( "^((u[35][0f][0-9a-f]{2})-([01][0-9]))\\.svg$")
    make_salt( "^((u[35][0f][0-9a-f]{2})-var-([0-9]{3}))\\.svg$")
    make_aalt( "^((u[35][0f][0-9a-f]{2})-itaiji-([0-9]{3}))\\.svg$")
    make_liga("^((u2ff[0-b])(-u[0-9a-f]{4,5})+)\\.svg$")
    print("Generate HanaMinDebug.ttf.")
    base.generate("HanaMinDebug.ttf",flags=("opentype","no-hints","round"))

def make_font_a ():
    make_font("HanaMinA", "Hanazono Mincho A")
    make_base("^(u([2-9f][0-9a-f]{3}))\\.svg$")
    make_ivs ("^(u([2-9f][0-9a-f]{3})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk("^((u[2-9f][0-9a-f]{3})-([gtkj]))\\.svg$")
    make_vert("^((u[2-9f][0-9a-f]{3})-vert)\\.svg$")
    make_ssXX("^((u[2-9f][0-9a-f]{3})-([01][0-9]))\\.svg$")
    make_salt("^((u[2-9f][0-9a-f]{3})-var-([0-9]{3}))\\.svg$")
    make_aalt("^((u[2-9f][0-9a-f]{3})-itaiji-([0-9]{3}))\\.svg$")
    make_liga("^((u2ff[0-b])(-u[0-9a-f]{4,5})+)\\.svg$")
    print("Generate HanaMinA.ttf file.")
    base.generate("HanaMinA.ttf",flags=("opentype","no-hints","round"))

def make_font_b ():
    make_font("HanaMinB", "Hanazono Mincho B")
    make_base("^(u([12][0-9a-f]{4}))\\.svg$")
    make_ivs ("^(u([12][0-9a-f]{4})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk("^((u[12][0-9a-f]{4})-([gtkj]))\\.svg$")
    make_vert("^((u[12][0-9a-f]{4})-vert)\\.svg$")
    make_ssXX("^((u[12][0-9a-f]{4})-([01][0-9]))\\.svg$")
    make_salt("^((u[12][0-9a-f]{4})-var-([0-9]{3}))\\.svg$")
    make_aalt("^((u[12][0-9a-f]{4})-itaiji-([0-9]{3}))\\.svg$")
    print("Generate HanaMinB.ttf file.")
    base.generate("HanaMinB.ttf",flags=("opentype","no-hints","round"))

#make_font_debug()
#make_font_a()
make_font_b()
# TODO:
# 横書き漢文句読点重ねあわせ機能
# 縦書き漢文句読点重ねあわせ機能
