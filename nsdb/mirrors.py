"""
This script finds the fastest mirror to download Wikipedia dumps from
"""
import re
import time

import requests
from tqdm import tqdm


def fastest(dump: str = "20200401/", wiki:str = "enwiki/") -> str:
    """Gets a list of the fastest mirrors, downloads a single file from each
    and returns the fastest one.

    Execution takes 5-10 seconds as a guideline

    Returns
    -------
    fastestMirror: str - the url of the fastest mirror
    """
    # find a list of mirrors
    url = "https://dumps.wikimedia.org/mirrors.html"
    mirrorPage = requests.get(url)

    html = mirrorPage.content.decode("utf-8")
    mirrors = re.findall('href="(http:.*)"', html)
    mirrorDownloadTime = []

    # Add main site
    mirrors.append("https://dumps.wikimedia.org/")

    firstfile = "enwiki-20200401-pages-meta-history5.xml-p564843p565313.7z"
    print("Finding fastest mirror")
    for index, mirror in enumerate(tqdm(mirrors, unit=" mirror")):
        url = mirror + wiki + dump + firstfile

        tick = time.time()
        file = requests.get(url)

        # if 404 or similar
        if file.content[0] == 60:
            # try other url scheme
            mirrors[index] = mirror + "dumps/"
            url = mirrors[index] + wiki + dump + firstfile

            tick = time.time()
            file = requests.get(url)

            if file.content[0] == 60:
                mirrorDownloadTime.append(1000)
            else:
                mirrorDownloadTime.append(time.time() - tick)
        # add the time to download
        else:
            mirrorDownloadTime.append(time.time() - tick)

        # print(url)

    # return fastest mirror
    _, index = min((val, index) for (index, val) in enumerate(mirrorDownloadTime))

    # print(mirrorDownloadTime)
    # print("Fastest mirror is " + mirrors[index])
    if all(time == 1000 for time in mirrorDownloadTime):
        raise RuntimeError("Dump " + dump + " is no longer hosted on any mirror")

    return mirrors[index]


if __name__ == "__main__":
    fastest()
