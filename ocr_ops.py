import xml.etree.ElementTree as ET
import re
import json
import numpy as np


def main():
    return


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
