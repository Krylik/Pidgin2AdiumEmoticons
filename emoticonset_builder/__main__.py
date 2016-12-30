__author__ = 'Krylik'
import argparse
import re
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from shutil import copytree, ignore_patterns

argparser = argparse.ArgumentParser()
argparser.add_argument('indir',
                       metavar='input',
                       type=str,
                       help="The directory containing the pidgin emotes")
argparser.add_argument('outdir',
                       metavar='output',
                       type=str,
                       help="The output directory name, this will have .AdiumEmoticonSet appended to the name")
args = argparser.parse_args()

outdir = "%s%s" % (args.outdir, '.AdiumEmoticonSet')
copytree(args.indir, outdir, ignore=ignore_patterns('theme', '.git*', '*.gz'))
# store list of filenames for case insensitive matching later
outfiles = os.listdir(outdir)

emoticons = []
with open('%s/theme' % args.indir) as themefile:
    for themeline in themefile:
        if themeline.startswith('! '):
            parts = re.split('\s*', themeline.strip('! ').strip('\n'))
            img = parts[0]
            triggers = parts[1:]
            emoticons.append((img, triggers))

# Build plist file from template
tree = ET.parse('emoticonset_builder/template.plist')
plist = tree.getroot()
plist_root_dict = plist.find('dict')
emote_dict = ET.SubElement(plist_root_dict, 'dict')
for emote in emoticons:
    img, triggers = emote
    # verify image name, replace with correct case if necessary
    for filename in outfiles:
        if filename.lower() == img.lower():
            img = filename
    # key for image name
    img_key = ET.SubElement(emote_dict, 'key')
    img_key.text = img
    # dict to hold triggers for this emote
    triggers_dict = ET.SubElement(emote_dict, 'dict')
    equiv_key = ET.SubElement(triggers_dict, 'key')
    equiv_key.text = 'Equivalents'
    triggers_array = ET.SubElement(triggers_dict, 'array')
    for trigger in triggers:
        trigger_item = ET.SubElement(triggers_array, 'string')
        trigger_item.text = trigger
    name_key = ET.SubElement(triggers_dict, 'key')
    name_key.text = 'Name'
    name_value = ET.SubElement(triggers_dict, 'string')
    name_value.text = img

# Write xml output to the outfile specified
reparsed_xml = minidom.parseString(ET.tostring(plist))
with open('%s/Emoticons.plist' % outdir, 'w+') as outplist:
    outplist.write(reparsed_xml.toprettyxml(indent="\t"))