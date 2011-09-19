#!/usr/bin/python
# -*- coding: utf-8 -*-

# 花園明朝フォント（実験版）を生成する。

import fontforge                                 #Load the module
import psMat
import os, re

base=fontforge.open("./basefont.ttf.ivs")
base.os2_width=1024
base.fontname="HanaMinA"
base.fullname="Hanazono Mincho A"
base.hasvmetrics=True
base.vhea_linegap=102

mat1 = psMat.scale(1.05,1.05)
mat2 = psMat.translate(-25,-25)

def import_glyph (code, file, name):
    glyph=base.createChar(code, name)
    glyph.importOutlines(file, "removeoverlap")
    glyph.simplify()
    glyph.transform(mat1)
    glyph.transform(mat2)
    glyph.width=1024
    glyph.vwidth=1024
    glyph.round()
    glyph.autoInstr()
    return glyph

def file_name (file):
    #ファイルから名前を生成する。
    if re.search("work/(.+)\\.svg",file):
        return re.group(1)
    else:
        error ("Something Wrong!")

tmp_code=0xf0000
def import_tmp_glyph (file,name):
    global tmp_code
    glyph=import_glyph(tmp_code, file,name)
    tmp_code=tmp_code+1
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
            code = int(m.group(2),16)
            import_glyph(code,"./work/"+file,name)

## IVS
def make_ivs (reg):
    reobj = re.compile(reg)
    for file in os.listdir('./work/'):
        m=reobj.match(file)
        if (m):
            name  = m.group(1)
            code  = int(m.group(2),16)
            vs    = int(m.group(3),16)
            glyph = import_tmp_glyph("./work/"+file,name)
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
            glyph = import_tmp_glyph("./work/"+file,name)
            if region == "g":
                base[nameX].addPosSub("zhcn1",name)
            elif region == "t":
                base[nameX].addPosSub("zhtw1",name)
            elif region == "j":
                base[nameX].addPosSub("jajp1",name)
            elif region == "k":
                base[nameX].addPosSub("kokr1",name)
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
            glyph = import_tmp_glyph("./work/"+file,name)
            base[nameX].addPosSub("vert1",name)

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
            glyph = import_tmp_glyph("./work/"+file,name)
            base[nameX].addPosSub("ss"+style+"1",name)

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
            glyph  = import_tmp_glyph("./work/"+file,name)
            try:
                dict[nameX][variant]=name
            except KeyError:
                dict[nameX] = {variant: name}
                
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
            glyph  = import_tmp_glyph("./work/"+file,name)
            try:
                dict[nameX][variant]=name
            except KeyError:
                dict[nameX] = {variant: name}
    
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
            nameX  = m.group(2)
            ids    = tuple(name.split("-"))
            print ("liga",ids)
            base[nameX].addPosSub("liga1",ids)

def make_font_debug ():
    make_base("^(u([23][0f][0-9a-f]{2}))\\.svg$") # debug
    make_ivs ( "^(u([3][0f][0-9a-f]{2})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk( "^((u[3][0f][0-9a-f]{2})-([gtkj]))\\.svg$")
    make_vert( "^((u[3][0f][0-9a-f]{2})-vert)\\.svg$")
    make_ssXX( "^((u[3][0f][0-9a-f]{2})-([01][0-9]))\\.svg$")
    make_salt( "^((u[3][0f][0-9a-f]{2})-var-([0-9]{3}))\\.svg$")
    make_aalt( "^((u[3][0f][0-9a-f]{2})-itaiji-([0-9]{3}))\\.svg$")

def make_font_a ():
    make_base("^(u([2-9f][0-9a-f]{3}))\\.svg$")
    make_ivs ("^(u([2-9f][0-9a-f]{3})-u(e01[01][0-9a-f]))\\.svg$")
    make_gtjk("^((u[2-9f][0-9a-f]{3})-([gtkj]))\\.svg$")
    make_vert("^((u[2-9f][0-9a-f]{3})-vert)\\.svg$")
    make_ssXX("^((u[2-9f][0-9a-f]{3})-([01][0-9]))\\.svg$")
    make_salt("^((u[2-9f][0-9a-f]{3})-var-([0-9]{3}))\\.svg$")
    make_aalt("^((u[2-9f][0-9a-f]{3})-itaiji-([0-9]{3}))\\.svg$")
    make_liga("^((u2ff[0-b])(-u[0-9a-f]{4})+)\\.svg$")

# make_font_a()
make_font_debug()
print("Generate .ttf file.")
base.generate("HanaMinA.ttf",flags=("opentype","no-hints","round"))

# TODO:
# 横書き漢文句読点重ねあわせ機能
# 縦書き漢文句読点重ねあわせ機能
