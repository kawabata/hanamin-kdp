#/bin/bash -x
version=1.`date "+%m%d"`1
echo "creating version "$version
cd /home/kawabata/Resources/GlyphWiki/dump/

echo "Removing various data...."
/bin/rm -rf ./work
/bin/rm -rf ./ttx
/bin/rm dump.tar.gz
/bin/rm log.*
rm HanaMin*.ttf
rm *.sfd *.afm
mkdir ./work/
mkdir ./ttx/

echo "Downloading data..."
wget http://glyphwiki.org/dump.tar.gz
tar xvfz dump.tar.gz

echo "Creating data.."
# java -jar /usr/share/java/rhino.jar makesvg.js dump_newest_only.txt > log.j.txt
rhino makesvg.js dump_newest_only.txt > log.j.txt
emacs --script glyphwiki-symlink.el

echo "Creating fonts.."
python makefont.py A $version > log.A.txt
python makefont.py B $version > log.B.txt

echo "Decomposing fonts..."
ttx -si -t hhea -t cmap -d ttx HanaMinA.ttf
ttx -si -t hhea -t cmap -d ttx HanaMinB.ttf

echo "re-Building fonts...."
mv ttx/HanaMinA._c_m_a_p.ttx ttx/HanaMinA._c_m_a_p.ttx.bak
mv ttx/HanaMinA._h_h_e_a.ttx ttx/HanaMinA._h_h_e_a.ttx.bak
mv ttx/HanaMinB._c_m_a_p.ttx ttx/HanaMinB._c_m_a_p.ttx.bak
mv ttx/HanaMinB._h_h_e_a.ttx ttx/HanaMinB._h_h_e_a.ttx.bak

grep -v -e "Plane 15 Private Use" ttx/HanaMinA._c_m_a_p.ttx.bak > ttx/HanaMinA._c_m_a_p.ttx
grep -v -e "Plane 15 Private Use" ttx/HanaMinB._c_m_a_p.ttx.bak > ttx/HanaMinB._c_m_a_p.ttx
sed -e 's/<ascent .*\/>/<ascent value="880"\/>/' -e 's/<descent .*\/>/<descent value="-144"\/>/' ttx/HanaMinA._h_h_e_a.ttx.bak > ttx/HanaMinA._h_h_e_a.ttx
sed -e 's/<ascent .*\/>/<ascent value="880"\/>/' -e 's/<descent .*\/>/<descent value="-144"\/>/' ttx/HanaMinB._h_h_e_a.ttx.bak > ttx/HanaMinB._h_h_e_a.ttx

ttx -m HanaMinA.ttf ttx/HanaMinA.ttx
ttx -m HanaMinB.ttf ttx/HanaMinB.ttx
