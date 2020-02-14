import xml.etree.ElementTree as ET
import time

print('getting ready')
tick = time.time()
tree = ET.parse('enwiki-20200101-pages-meta-history1.xml-p10p1036')
print("--- %s seconds ---" % (time.time() - tick))
root = tree.getroot()
print('done')
print(root)
