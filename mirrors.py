# !/usr/bin/python
import re
import time

import requests

# find a list of mirrors
url = 'https://dumps.wikimedia.org/mirrors.html'
r = requests.get(url)

html = r.content.decode('utf-8')
mirrors = re.findall("href=\"(http:.*)\"", html)
mirrorDownloadTime = []

# Add main site
mirrors.append("https://dumps.wikimedia.org/")

# find the requisite wiki dump
wiki = "enwiki/"
dump = "20200101/"

firstfile = "enwiki-20200101-pages-meta-history2.xml-p40221p40268.7z"

for index, mirror in enumerate(mirrors):
    url = mirror + wiki + dump + firstfile
    
    tick = time.time()
    r = requests.get(url)
    
    # if 404 or similar
    if (r.content[0] == 60):
        # try other url scheme
        mirrors[index] = mirror + "dumps/"
        url = mirrors[index] + wiki + dump + firstfile
        
        tick = time.time()
        r = requests.get(url)
        
        if (r.content[0] == 60):
            mirrorDownloadTime.append(1000)
        else:
            mirrorDownloadTime.append(time.time() - tick)
    # add the time to download
    else:
        mirrorDownloadTime.append(time.time() - tick)

    # print(url)


# return fastest mirror
val, index = min((val, index) for (index, val) in enumerate(mirrorDownloadTime))

# print(mirrorDownloadTime)
# print("Fastest mirror is " + mirrors[index])

print(mirrors[index])
