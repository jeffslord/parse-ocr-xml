import xml.etree.ElementTree as ET
import re
import json
import numpy as np


def main():
    return


def getUniqueValues(allTextObjects, boxIndex):
    justified = {}
    for i in allTextObjects:
        if i['bbox'][boxIndex] not in justified:
            justified[i['bbox'][int(boxIndex)]] = [i]
        else:
            justified[i['bbox'][boxIndex]].append(i)
    for key, value in justified.items():
        a = np.array(value)
        justified[key] = a.ravel()
    return justified


def getBoundingBox(node):
    return re.findall(r'\d+', getTitle(node))


def getText(node):
    if('class' in getAttrib(node)):
        if(getClass(node) == 'ocrx_word'):
            for child in node.iter():
                if(child.tag.endswith("em")):
                    # print(child.text)
                    return child.text


def getClass(node):
    return getAttrib(node)['class']


def getTitle(node):
    return getAttrib(node)['title']


def getAttrib(node):
    return node.attrib


if __name__ == "__main__":
    main()
