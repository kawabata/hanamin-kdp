load("./engine/2d.js");
load("./engine/buhin.js");
load("./engine/curve.js");
load("./engine/kage.js");
load("./engine/kagecd.js");
load("./engine/kagedf.js");
load("./engine/polygon.js");
load("./engine/polygons.js");

file = new java.io.File("./work");
if(!file.exists()){
  file.mkdir();
}

target = "dump_all_versions.txt"
fis = new java.io.FileInputStream("./" + target);
isr = new java.io.InputStreamReader(fis);
br = new java.io.BufferedReader(isr);

kage = new Kage();
array = new Array();

while((line = br.readLine()) != null){
    if (line.match(/^ ([-0-9a-z_]+)(@[0-9]+) +\| [-0-9a-z]+ +\| (.+)$/)) {
        glyph    = RegExp.$1;
        revision = RegExp.$2;
        glyph_id = glyph+revision;
        data     = RegExp.$3;
        kage.kBuhin.push(glyph_id, data);
        kage.kBuhin.push(glyph, data);
        //if (glyph_id.match(/^cdp-/)) {//
        if (glyph_id.match(/^u[0-9f]/) || glyph_id.match(/^cdp-/) || glyph_id.match(/^kumimoji-u2ff/)) {
            array[glyph]=glyph_id;
        }
    }
}

br.close();
isr.close();
fis.close();

print ("Output phase\n")

for(key in array) {
    gid = array[key]
    print (gid)
    try {
        var polygons = new Polygons();
        kage.makeGlyph(polygons,gid);
        fos = new java.io.FileOutputStream("./work/" + key + ".svg");
        osw = new java.io.OutputStreamWriter(fos);
        bw = new java.io.BufferedWriter(osw);
        bw.write(polygons.generateSVG(false));
        bw.close();
        osw.close();
        fos.close();
    } catch (e) {
        print ("error:"+gid)
    }
}
