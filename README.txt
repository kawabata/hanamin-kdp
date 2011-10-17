
HanaMinKDP toolkit.

These files are to create HanaMin Experimental version
(http://kanji-database.sourceforge.net/fonts/hanazono.html).

Please download `kage engine' from M17n CVS repository
(:pserver:anonymous@cvs.m17n.org:/cvs/chise) and prepare it
in the same directory.

Variant database from `kanji-database' can be incorporated
into `aalt' feature, but Fontforge may produce imporper font
when `aalt' entries are too large (>15,000).



About Fontforge `vmtx' table problem.

To properly output `vmtx' (vertical matrix) table with fontforge,
please fix the following line at `ttfdumpmetrics' function of
fontforge/tottf.c.  (As of 2011 version of FontForge.)

     if ( sc->parent->hasvmetrics ) {
 	if ( sc->ttf_glyph<=gi->lastvwidth )
 	    putshort(gi->vmtx,vwidth);
-	putshort(gi->vmtx,/*sc->parent->vertical_origin-*/b->maxy);
+	putshort(gi->vmtx, sc->parent->ascent - b->maxy);
     }
     if ( sc->ttf_glyph==gi->lasthwidth )
 	gi->hfullcnt = sc->ttf_glyph+1;
