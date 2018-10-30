import xml.etree.ElementTree as ET
import re
import json
import numpy as np


def main():

    # text2_old = text2
    # tree = ET.fromstring(text2)

    try:
        open('export_text.txt', 'w').close()
    except:
        print('Not made yet')
    f = open('export_text.txt', 'w')

    allText = []
    allTextObjects = []
    allTextObjectsByLine = []
    currentText = ''
    lineNum = 0

    # Loop through all nodes in the xml tree
    for node in tree.iter():
        word = False
        line = False
        if('class' in node.attrib):
            cl = getClass(node)
            if(cl == 'ocr_line'):
                line = True
            if(cl == 'ocrx_word'):
                word = True
            if(line):
                print(
                    '---------------NEW LINE----------------------------------------------------------------')
                f.write(
                    '---------------NEW LINE----------------------------------------------------------------' + '\n')
                allText.append(currentText)
                lineNum += 1

                currentText = ''
            if(line or word):
                print('node: \t\t\t' + str(node))
                f.write('node: \t\t\t\t' + str(node) + '\n')
                print('attrib: \t\t' + str(getAttrib(node)))
                f.write('attrib: \t\t\t' + str(getAttrib(node)) + '\n')
                print('attrib[\'class\']: \t' + str(getClass(node)))
                f.write('attrib[\'class\']: \t' +
                        str(getClass(node)) + '\n')
                print('attrib[\'title\']: \t' + str(getTitle(node)))
                f.write('attrib[\'title\']: \t' +
                        str(getTitle(node)) + '\n')
                getBoundingBox(node)
            if(word):
                text = getText(node)
                # text = text_out.find("em", ns)
                print('text: \t\t\t' + str(text))
                f.write('text: \t\t\t\t' + str(text) + '\n')
                currentText += ' ' + text
                textObject = {"text": getText(node),
                              "bbox": getBoundingBox(node)}
                allTextObjects.append(textObject)
            print()
            f.write('\n')
    allText.append(currentText)

    for i in allText:
        print(i)
    print("Left, Top, Right, Bottom")
    for i in allTextObjects:
        print(i)

    # Get columns
    rightJustified = getUniqueValues(allTextObjects, 2)
    rightMatches = getSimilarValues(rightJustified, 3, 1)
    topJustified = getUniqueValues(allTextObjects, 1)
    topMatches = getSimilarValues(topJustified, 5, 0)

    for key, value in rightMatches.items():
        print(key)
        print(value)
        print()


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


def getSimilarValues(justified, distance, sortIndex):
    found = []
    match = {}
    for i in justified.keys():
        if i in found:
            continue
        else:
            match[i] = [justified[i]]
            for j in justified.keys():
                if(i == j) or (j in found):
                    continue
                else:
                    if(abs(int(i) - int(j)) < distance):
                        found.append(j)
                        match[i].append(justified[j])
    for key, value in match.items():
        match[key] = np.concatenate(value).ravel().tolist()
        # match[key] = match[key].sort(key=lambda x: x['bbox'][sortIndex])
    return match

# arrange all words by line
# check for overallap if... last word in line, or word to right of line is far (not part of same sentence)


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


def getDistance(bbox1, bbox2, direction):
    if(direction == 'TB'):
        return abs(int(bbox1[1]) - int(bbox2[3]))
    if(direction == 'BT'):
        return abs(int(bbox1[3]) - int(bbox2[1]))
    if(direction == 'LR'):
        return abs(int(bbox1[0]) - int(bbox2[2]))
    if(direction == 'RL'):
        return abs(int(bbox1[2]) - int(bbox2[0]))
    if(direction == 'LL'):
        return abs(int(bbox1[0]) - int(bbox2[0]))
    if(direction == 'RR'):
        return abs(int(bbox1[2]) - int(bbox2[2]))


if __name__ == "__main__":
    main()
