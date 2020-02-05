import xml.etree.ElementTree as ET
print('getting ready')
tree = ET.parse('enwiki-20200101-pages-meta-history1.xml-p10p1036')
root = tree.getroot
print('done')
print(root)
