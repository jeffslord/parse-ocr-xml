import xml.etree.ElementTree as ET
import re
import json
import numpy as np
from ocr_parse_objects import Word
from ocr_parse_objects import Line
import ocr_ops


def main():
    tree = ET.fromstring(getTxt())
    lines = parseTree(tree)
    horizontalMergeLines = mergeHorizontal(lines)
    verticalMergeLines = mergeVertical(horizontalMergeLines)

    arr = []
    for i in verticalMergeLines:
        print(i)


def parseTree(tree):
    # separate all words into
    lines = []
    line = None
    word = None
    # go through all elements in the hOCR text
    # make all words and lines into my custom class
    for node in tree.iter():
        if('class' in node.attrib):
            cl = ocr_ops.getClass(node)
            if(cl == "ocr_line"):
                if(line != None and len(line.words) > 0):
                    lines.append(line)
                    line = None
                line = Line()
            if(cl == "ocrx_word"):
                text = ocr_ops.getText(node)
                bbox = ocr_ops.getBoundingBox(node)
                word = Word(text, bbox[0], bbox[1], bbox[2], bbox[3])
                line.addWord(word)
    if(line != None and len(line.words) > 0):
        lines.append(line)
    return lines


def mergeVertical(lines):
    mergedLines = []
    mergeSource = {}

    mergedIndexes = []
    # loop through all lines, except the last line
    for i in range(len(lines)-1):
        mergeLine = Line()
        # loop through all words in first line
        for j in range(len(lines[i].words)):
            word1 = lines[i].words[j]
            # if word1 is already merged, set word1 as the merged word
            if((i, j) in mergedIndexes):
                word1 = mergeSource.get((i, j))
                # print(word1)
            # loop through all words in second line
            for k in range(len(lines[i+1].words)):
                word2 = lines[i+1].words[k]
                # if word in line1 can merge with line2, do the merge and break out of loop (only 1 merge per word)
                if(Word.tryMergeVertical(word1, word2)):
                    # print("MERGE")
                    # print(word1)
                    # print(word2)
                    newWord = Word.mergeWords(word1, word2)
                    if((i, j) in mergeSource.keys()):
                        # print("TRUE", mergeSource[i, j])
                        replaceWord(mergedLines, mergeSource[(i, j)], newWord)
                        # print("NEED TO REPLACE WORD")
                        mergeSource[(i, j)] = newWord
                        # mergeLine.addWord(newWord)
                        # print("NEW", mergeSource[i, j])
                    else:
                        mergeLine.addWord(newWord)
                        mergedIndexes.append((i, j))
                        mergeSource[(i, j)] = newWord
                    mergedIndexes.append((i+1, k))
                    mergeSource[(i+1, k)] = newWord
                    # print("I+1", mergeSource[(i+1, k)])
                    # break
            # if word has no word to match with, just add the word by itself
            if((i, j) not in mergedIndexes):
                mergeLine.addWord(word1)
        if(len(mergeLine.words) > 0):
            mergedLines.append(mergeLine)
    # for k, v in mergeSource.items():
    #     print(k, "=>", v)
    # for i in mergedLines:
    #     print(i)
    return mergedLines


def replaceWord(lines, oldWord, newWord):
    for i in range(len(lines)):
        for j in range(len(lines[i].words)):
            if(lines[i].words[j] == oldWord):
                # print("WORD FOUND")
                lines[i].words[j] = newWord


def mergeHorizontal(lines):
    # will this work? who knows, let's find out
    # go through all lines
    mergedLines = []
    mergeCount = 0
    for i in lines:
        # print(i)
        mergeLine = Line()
        mergedIndexes = []
        # only try to merge if line has more than 1 word
        if(len(i.words) > 1):
            # go through all words in line, do no process last word because it has no word next to it
            for j in range(len(i.words) - 1):
                word1 = None
                word2 = None
                # check if word is already merged.
                # if it is, make current word the last merged word
                if(j in mergedIndexes):
                    word1 = mergeLine.words[-1]
                    word2 = i.words[j+1]
                # if it isn't merged, check if mergeLine is empty, if it is not, set current word to last added, and new word to next in line
                else:
                    if(len(mergeLine.words) > 0):
                        word1 = mergeLine.words[-1]
                        word2 = i.words[j+1]
                    else:
                        word1 = i.words[j]
                        word2 = i.words[j+1]
                # try to see if words will merge
                # if they will, merge them, add merged word to mergeLine, and add the indexes to mergedIndexes
                if(Word.tryMergeHorizontal(word1, word2)):
                    mergeCount += 1
                    newWord = Word.mergeWords(word1, word2)
                    if(word1 in mergeLine.words):
                        mergeLine.words[-1] = newWord
                    else:
                        mergeLine.addWord(newWord)
                    mergedIndexes.append(j)
                    mergedIndexes.append(j+1)
                # if they will not merge, add both words separately
                else:
                    mergeLine.addWord(word1)
                    mergeLine.addWord(word2)
            mergedLines.append(mergeLine)
        # if there is only 1 word
        else:
            if(len(i.words) == 1):
                mergeLine = Line()
                mergeLine.addWord(i.words[0])
                mergedLines.append(mergeLine)
    return mergedLines


def getTxt():
    txt1 = '''
        <html:html xmlns:html=\"http://www.w3.org/1999/xhtml\" lang=\"en\" xml:lang=\"en\">\n <html:head>\n  <html:title />\n<html:meta content=\"text/html;charset=utf-8\" http-equiv=\"Content-Type\" />\n  <html:meta content=\"tesseract 4.0.0-beta.4-50-g07acc\" name=\"ocr-system\" />\n  <html:meta content=\"ocr_page ocr_carea ocr_par ocr_line ocrx_word\" name=\"ocr-capabilities\" />\n</html:head>\n<html:body>\n  <html:div class=\"ocr_page\" id=\"page_1\" rotation=\"0\" title=\"image &quot;/home/vcap/tmp/27470e00-88ea-4fa6-a5ac-035921e362860/L3pdfexample-8-8.pdf1.png&quot;; bbox 0 0 3300 2550; ppageno 0\">\n   <html:div class=\"ocr_carea\" id=\"block_1_1\" title=\"bbox 1536 120 1775 140\">\n    <html:p class=\"ocr_par\" id=\"par_1_1\" lang=\"eng_best\" title=\"bbox 1536 120 1775 140\">\n     <html:span class=\"ocr_line\" id=\"line_1_1\" title=\"bbox 1536 120 1775 140; baseline 0 0; x_size 27.333334; x_descenders 6.8333335; x_ascenders 6.8333335\">\n      <html:span class=\"ocrx_word\" id=\"word_1_1\" title=\"bbox 1536 120 1775 140; x_wconf 95\"><html:strong><html:em>UNCLASSIFIED</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n   </html:div>\n   <html:div class=\"ocr_carea\" id=\"block_1_2\" title=\"bbox 1276 195 3132 372\">\n    <html:p class=\"ocr_par\" id=\"par_1_2\" lang=\"eng_best\" title=\"bbox 1276 195 3132 372\">\n     <html:span class=\"ocr_line\" id=\"line_1_2\" title=\"bbox 1436 195 1855 223; baseline 0.002 -7; x_size 29; x_descenders 7; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_2\" title=\"bbox 1436 196 1634 223; x_wconf 95\"><html:strong><html:em>Department</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_3\" title=\"bbox 1657 195 1695 217; x_wconf 96\"><html:strong><html:em>of</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_4\" title=\"bbox 1716 195 1855 217; x_wconf 95\"><html:strong><html:em>Defense</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_3\" title=\"bbox 1396 231 1914 260; baseline 0 -7; x_size 28; x_descenders 6; x_ascenders 7\">\n      <html:span class=\"ocrx_word\" id=\"word_1_5\" title=\"bbox 1396 233 1436 253; x_wconf 96\"><html:strong><html:em>FY</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_6\" title=\"bbox 1458 231 1534 253; x_wconf 95\"><html:strong><html:em>2019</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_7\" title=\"bbox 1556 232 1774 254; x_wconf 94\"><html:strong><html:em>President's</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_8\" title=\"bbox 1796 232 1914 260; x_wconf 96\"><html:strong><html:em>Budget</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_4\" title=\"bbox 1276 269 2034 298; baseline 0 -7; x_size 29; x_descenders 7; x_ascenders 7\">\n      <html:span class=\"ocrx_word\" id=\"word_1_9\" title=\"bbox 1276 270 1414 291; x_wconf 93\"><html:strong><html:em>Exhibit</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_10\" title=\"bbox 1436 270 1493 291; x_wconf 77\"><html:strong><html:em>R-1</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_11\" title=\"bbox 1516 271 1556 291; x_wconf 96\"><html:strong><html:em>FY</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_12\" title=\"bbox 1578 269 1654 291; x_wconf 96\"><html:strong><html:em>2019</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_13\" title=\"bbox 1676 270 1894 292; x_wconf 90\"><html:strong><html:em>President's</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_14\" title=\"bbox 1916 270 2034 298; x_wconf 96\"><html:strong><html:em>Budget</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_5\" title=\"bbox 1377 308 3132 336; baseline 0.001 -7; x_size 28; x_descenders 7; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_15\" title=\"bbox 1377 308 1474 330; x_wconf 92\"><html:strong><html:em>Total</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_16\" title=\"bbox 1497 308 1734 336; x_wconf 91\"><html:strong><html:em>Obligational</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_17\" title=\"bbox 1755 308 1936 336; x_wconf 96\"><html:strong><html:em>Authority</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_18\" title=\"bbox 2977 310 3034 331; x_wconf 96\"><html:strong><html:em>Feb</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_19\" title=\"bbox 3059 309 3132 330; x_wconf 96\"><html:strong><html:em>2018</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_6\" title=\"bbox 1445 346 1868 372; baseline 0.002 -5; x_size 26; x_descenders 4; x_ascenders 7\">\n      <html:span class=\"ocrx_word\" id=\"word_1_20\" title=\"bbox 1445 346 1594 372; x_wconf 95\"><html:strong><html:em>(Dollars</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_21\" title=\"bbox 1618 346 1655 367; x_wconf 95\"><html:strong><html:em>in</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_22\" title=\"bbox 1677 346 1868 372; x_wconf 96\"><html:strong><html:em>Thousands)</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n   </html:div>\n   <html:div class=\"ocr_carea\" id=\"block_1_3\" title=\"bbox 95 609 2013 1128\">\n    <html:p class=\"ocr_par\" id=\"par_1_3\" lang=\"eng_best\" title=\"bbox 1276 609 1974 631\">\n     <html:span class=\"ocr_line\" id=\"line_1_7\" title=\"bbox 1276 609 1974 631; baseline 0 0; x_size 28.666666; x_descenders 6.5; x_ascenders 6.6666665\">\n      <html:span class=\"ocrx_word\" id=\"word_1_23\" title=\"bbox 1276 611 1316 631; x_wconf 95\"><html:strong><html:em>FY</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_24\" title=\"bbox 1338 609 1414 631; x_wconf 95\"><html:strong><html:em>2019</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_25\" title=\"bbox 1556 611 1596 631; x_wconf 95\"><html:strong><html:em>FY</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_26\" title=\"bbox 1618 609 1694 631; x_wconf 95\"><html:strong><html:em>2019</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_27\" title=\"bbox 1836 611 1876 631; x_wconf 96\"><html:strong><html:em>FY</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_28\" title=\"bbox 1898 609 1974 631; x_wconf 96\"><html:strong><html:em>2019</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n\n    <html:p class=\"ocr_par\" id=\"par_1_4\" lang=\"eng_best\" title=\"bbox 95 647 2013 1128\">\n     <html:span class=\"ocr_line\" id=\"line_1_8\" title=\"bbox 95 647 1956 679; baseline 0.001 -11; x_size 28.290321; x_descenders 6.2903223; x_ascenders 7\">\n      <html:span class=\"ocrx_word\" id=\"word_1_29\" title=\"bbox 95 647 355 678; x_wconf 95\"><html:strong><html:em>Appropriation</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_30\" title=\"bbox 1316 649 1396 679; x_wconf 96\"><html:strong><html:em>Base</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_31\" title=\"bbox 1596 649 1656 679; x_wconf 81\"><html:strong><html:em>oco</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_32\" title=\"bbox 1856 648 1956 679; x_wconf 95\"><html:strong><html:em>Total</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_9\" title=\"bbox 97 724 2013 750; baseline 0.001 -6; x_size 26; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_33\" title=\"bbox 97 724 267 748; x_wconf 96\"><html:strong><html:em>Research,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_34\" title=\"bbox 297 724 527 750; x_wconf 95\"><html:strong><html:em>Development,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_35\" title=\"bbox 558 725 633 745; x_wconf 93\"><html:strong><html:em>Test</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_36\" title=\"bbox 659 727 672 745; x_wconf 92\"><html:strong><html:em>&amp;</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_37\" title=\"bbox 696 724 787 749; x_wconf 95\"><html:strong><html:em>Eval,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_38\" title=\"bbox 816 725 894 750; x_wconf 94\"><html:strong><html:em>Army</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_39\" title=\"bbox 1259 724 1453 749; x_wconf 95\"><html:strong><html:em>10,159,379</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_40\" title=\"bbox 1598 724 1732 750; x_wconf 96\"><html:strong><html:em>325,104</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_41\" title=\"bbox 1819 724 2013 750; x_wconf 96\"><html:strong><html:em>10,484,483</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_10\" title=\"bbox 97 800 2012 826; baseline 0.001 -6; x_size 26; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_42\" title=\"bbox 97 800 267 824; x_wconf 95\"><html:strong><html:em>Research,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_43\" title=\"bbox 297 800 526 826; x_wconf 95\"><html:strong><html:em>Development,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_44\" title=\"bbox 557 801 632 821; x_wconf 93\"><html:strong><html:em>Test</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_45\" title=\"bbox 659 803 671 821; x_wconf 92\"><html:strong><html:em>&amp;</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_46\" title=\"bbox 696 800 786 825; x_wconf 95\"><html:strong><html:em>Eval,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_47\" title=\"bbox 816 801 894 826; x_wconf 95\"><html:strong><html:em>Navy</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_48\" title=\"bbox 1259 800 1453 826; x_wconf 95\"><html:strong><html:em>18,481,666</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_49\" title=\"bbox 1599 800 1732 826; x_wconf 96\"><html:strong><html:em>167,812</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_50\" title=\"bbox 1819 800 2012 826; x_wconf 95\"><html:strong><html:em>18,649,478</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_11\" title=\"bbox 97 875 2011 901; baseline 0.001 -6; x_size 26; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_51\" title=\"bbox 97 875 266 900; x_wconf 96\"><html:strong><html:em>Research,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_52\" title=\"bbox 296 875 526 901; x_wconf 94\"><html:strong><html:em>Development,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_53\" title=\"bbox 557 876 632 896; x_wconf 93\"><html:strong><html:em>Test</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_54\" title=\"bbox 659 878 671 896; x_wconf 92\"><html:strong><html:em>&amp;</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_55\" title=\"bbox 696 875 786 900; x_wconf 95\"><html:strong><html:em>Eval,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_56\" title=\"bbox 815 876 853 895; x_wconf 95\"><html:strong><html:em>AF</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_57\" title=\"bbox 1259 875 1452 901; x_wconf 96\"><html:strong><html:em>40,178,343</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_58\" title=\"bbox 1598 875 1731 901; x_wconf 94\"><html:strong><html:em>314,271</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_59\" title=\"bbox 1819 875 2011 901; x_wconf 95\"><html:strong><html:em>40,492,614</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_12\" title=\"bbox 97 951 2011 977; baseline 0.001 -6; x_size 26; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_60\" title=\"bbox 97 951 266 976; x_wconf 95\"><html:strong><html:em>Research,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_61\" title=\"bbox 296 951 526 977; x_wconf 95\"><html:strong><html:em>Development,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_62\" title=\"bbox 557 952 632 972; x_wconf 93\"><html:strong><html:em>Test</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_63\" title=\"bbox 659 954 671 972; x_wconf 92\"><html:strong><html:em>&amp;</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_64\" title=\"bbox 696 951 786 976; x_wconf 96\"><html:strong><html:em>Eval,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_65\" title=\"bbox 816 952 855 971; x_wconf 95\"><html:strong><html:em>DW</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_66\" title=\"bbox 1258 951 1452 977; x_wconf 95\"><html:strong><html:em>22,016,553</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_67\" title=\"bbox 1598 951 1731 977; x_wconf 95\"><html:strong><html:em>500,544</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_68\" title=\"bbox 1818 951 2011 977; x_wconf 96\"><html:strong><html:em>22,517,097</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_13\" title=\"bbox 97 1025 2012 1052; baseline 0.001 -6; x_size 26; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_69\" title=\"bbox 97 1025 312 1052; x_wconf 96\"><html:strong><html:em>Operational</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_70\" title=\"bbox 337 1027 412 1047; x_wconf 93\"><html:strong><html:em>Test</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_71\" title=\"bbox 439 1029 451 1047; x_wconf 93\"><html:strong><html:em>&amp;</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_72\" title=\"bbox 476 1026 566 1051; x_wconf 91\"><html:strong><html:em>Eval,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_73\" title=\"bbox 596 1026 733 1047; x_wconf 95\"><html:strong><html:em>Defense</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_74\" title=\"bbox 1318 1026 1452 1052; x_wconf 93\"><html:strong><html:em>221,009</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_75\" title=\"bbox 1878 1026 2012 1052; x_wconf 71\"><html:strong><html:em>221,009</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_14\" title=\"bbox 136 1100 2012 1128; baseline 0.001 -7; x_size 27; x_descenders 5; x_ascenders 7\">\n      <html:span class=\"ocrx_word\" id=\"word_1_76\" title=\"bbox 136 1100 233 1122; x_wconf 95\"><html:strong><html:em>Total</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_77\" title=\"bbox 255 1100 427 1126; x_wconf 96\"><html:strong><html:em>Research,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_78\" title=\"bbox 455 1100 687 1128; x_wconf 96\"><html:strong><html:em>Development,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_79\" title=\"bbox 716 1101 793 1122; x_wconf 93\"><html:strong><html:em>Test</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_80\" title=\"bbox 818 1102 832 1121; x_wconf 93\"><html:strong><html:em>&amp;</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_81\" title=\"bbox 855 1100 1054 1122; x_wconf 96\"><html:strong><html:em>Evaluation</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_82\" title=\"bbox 1259 1100 1387 1127; x_wconf 91\"><html:strong><html:em>91,056,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_83\" title=\"bbox 1399 1100 1452 1122; x_wconf 94\"><html:strong><html:em>950</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_84\" title=\"bbox 1558 1101 1732 1127; x_wconf 96\"><html:strong><html:em>1,307,731</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_85\" title=\"bbox 1819 1100 2012 1127; x_wconf 93\"><html:strong><html:em>92,364,681</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n   </html:div>\n   <html:div class=\"ocr_carea\" id=\"block_1_4\" title=\"bbox 96 1213 2054 1242\">\n    <html:p class=\"ocr_par\" id=\"par_1_5\" lang=\"eng_best\" title=\"bbox 96 1213 2054 1242\">\n     <html:span class=\"ocr_line\" id=\"line_1_15\" title=\"bbox 96 1213 2054 1242; baseline 0.001 -8; x_size 28; x_descenders 7; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_86\" title=\"bbox 96 1213 194 1235; x_wconf 96\"><html:strong><html:em>Other</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_87\" title=\"bbox 215 1214 314 1234; x_wconf 95\"><html:strong><html:em>RDT&amp;E</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_88\" title=\"bbox 335 1213 453 1241; x_wconf 96\"><html:strong><html:em>Budget</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_89\" title=\"bbox 474 1213 673 1235; x_wconf 96\"><html:strong><html:em>Activities</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_90\" title=\"bbox 695 1214 753 1235; x_wconf 95\"><html:strong><html:em>Not</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_91\" title=\"bbox 778 1213 936 1235; x_wconf 96\"><html:strong><html:em>Included</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_92\" title=\"bbox 957 1213 994 1234; x_wconf 95\"><html:strong><html:em>in</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_93\" title=\"bbox 1016 1213 1074 1235; x_wconf 96\"><html:strong><html:em>the</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_94\" title=\"bbox 1095 1214 1267 1240; x_wconf 96\"><html:strong><html:em>Research,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_95\" title=\"bbox 1295 1214 1527 1242; x_wconf 95\"><html:strong><html:em>Development,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_96\" title=\"bbox 1556 1215 1633 1236; x_wconf 96\"><html:strong><html:em>Test</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_97\" title=\"bbox 1656 1214 1716 1236; x_wconf 96\"><html:strong><html:em>and</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_98\" title=\"bbox 1735 1214 1934 1236; x_wconf 96\"><html:strong><html:em>Evaluation</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_99\" title=\"bbox 1956 1214 2054 1236; x_wconf 95\"><html:strong><html:em>Title</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n   </html:div>\n   <html:div class=\"ocr_carea\" id=\"block_1_5\" title=\"bbox 96 1290 2011 1468\">\n    <html:p class=\"ocr_par\" id=\"par_1_6\" lang=\"eng_best\" title=\"bbox 96 1290 2011 1468\">\n     <html:span class=\"ocr_line\" id=\"line_1_16\" title=\"bbox 97 1290 2011 1317; baseline 0.001 -6; x_size 27; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_100\" title=\"bbox 97 1290 213 1312; x_wconf 96\"><html:strong><html:em>Office</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_101\" title=\"bbox 237 1291 273 1312; x_wconf 95\"><html:strong><html:em>of</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_102\" title=\"bbox 296 1291 353 1312; x_wconf 96\"><html:strong><html:em>the</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_103\" title=\"bbox 379 1292 553 1317; x_wconf 95\"><html:strong><html:em>Inspector</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_104\" title=\"bbox 577 1291 712 1312; x_wconf 95\"><html:strong><html:em>General</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_105\" title=\"bbox 1359 1291 1451 1317; x_wconf 95\"><html:strong><html:em>1,602</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_106\" title=\"bbox 1919 1291 2011 1317; x_wconf 95\"><html:strong><html:em>1,602</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_17\" title=\"bbox 96 1365 2011 1392; baseline 0.001 -6; x_size 26; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_107\" title=\"bbox 96 1365 233 1387; x_wconf 95\"><html:strong><html:em>Defense</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_108\" title=\"bbox 257 1366 374 1387; x_wconf 95\"><html:strong><html:em>Health</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_109\" title=\"bbox 396 1367 535 1392; x_wconf 96\"><html:strong><html:em>Program</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_110\" title=\"bbox 1319 1366 1386 1392; x_wconf 95\"><html:strong><html:em>710,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_111\" title=\"bbox 1400 1366 1451 1387; x_wconf 96\"><html:strong><html:em>637</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_112\" title=\"bbox 1879 1366 2011 1392; x_wconf 95\"><html:strong><html:em>710,637</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_18\" title=\"bbox 97 1441 2011 1468; baseline 0.001 -6; x_size 27; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_113\" title=\"bbox 97 1441 175 1463; x_wconf 96\"><html:strong><html:em>Chem</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_114\" title=\"bbox 195 1442 312 1468; x_wconf 91\"><html:strong><html:em>Agents</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_115\" title=\"bbox 339 1445 351 1463; x_wconf 93\"><html:strong><html:em>&amp;</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_116\" title=\"bbox 375 1441 552 1463; x_wconf 96\"><html:strong><html:em>Munitions</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_117\" title=\"bbox 576 1441 793 1463; x_wconf 96\"><html:strong><html:em>Destruction</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_118\" title=\"bbox 1319 1442 1451 1468; x_wconf 94\"><html:strong><html:em>886,728</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_119\" title=\"bbox 1879 1442 2011 1468; x_wconf 95\"><html:strong><html:em>886,728</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n   </html:div>\n   <html:div class=\"ocr_carea\" id=\"block_1_6\" title=\"bbox 96 1515 675 1538\">\n    <html:p class=\"ocr_par\" id=\"par_1_7\" lang=\"eng_best\" title=\"bbox 96 1515 675 1538\">\n     <html:span class=\"ocr_line\" id=\"line_1_19\" title=\"bbox 96 1515 675 1538; baseline 0.002 -1; x_size 27.32258; x_descenders 5.3225803; x_ascenders 7\">\n      <html:span class=\"ocrx_word\" id=\"word_1_120\" title=\"bbox 96 1515 252 1538; x_wconf 96\"><html:strong><html:em>National</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_121\" title=\"bbox 276 1517 413 1538; x_wconf 95\"><html:strong><html:em>Defense</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_122\" title=\"bbox 438 1516 572 1538; x_wconf 94\"><html:strong><html:em>Sealift</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_123\" title=\"bbox 596 1517 675 1538; x_wconf 94\"><html:strong><html:em>Fund</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n   </html:div>\n   <html:div class=\"ocr_carea\" id=\"block_1_7\" title=\"bbox 136 1591 2012 1619\">\n    <html:p class=\"ocr_par\" id=\"par_1_8\" lang=\"eng_best\" title=\"bbox 136 1591 2012 1619\">\n     <html:span class=\"ocr_line\" id=\"line_1_20\" title=\"bbox 136 1591 2012 1619; baseline 0.001 -7; x_size 27; x_descenders 5; x_ascenders 6\">\n      <html:span class=\"ocrx_word\" id=\"word_1_124\" title=\"bbox 136 1591 233 1613; x_wconf 96\"><html:strong><html:em>Total</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_125\" title=\"bbox 255 1592 313 1613; x_wconf 96\"><html:strong><html:em>Not</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_126\" title=\"bbox 337 1591 374 1612; x_wconf 96\"><html:strong><html:em>in</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_127\" title=\"bbox 395 1591 567 1617; x_wconf 94\"><html:strong><html:em>Research,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_128\" title=\"bbox 595 1591 827 1619; x_wconf 95\"><html:strong><html:em>Development,</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_129\" title=\"bbox 856 1592 933 1613; x_wconf 93\"><html:strong><html:em>Test</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_130\" title=\"bbox 958 1593 972 1612; x_wconf 92\"><html:strong><html:em>&amp;</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_131\" title=\"bbox 995 1591 1194 1613; x_wconf 96\"><html:strong><html:em>Evaluation</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_132\" title=\"bbox 1278 1591 1452 1618; x_wconf 83\"><html:strong><html:em>1,598,967</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_133\" title=\"bbox 1838 1591 2012 1618; x_wconf 94\"><html:strong><html:em>1,598,967</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n   </html:div>\n   <html:div class=\"ocr_carea\" id=\"block_1_8\" title=\"bbox 1534 2389 3132 2443\">\n    <html:p class=\"ocr_par\" id=\"par_1_9\" lang=\"eng_best\" title=\"bbox 1534 2389 3132 2443\">\n     <html:span class=\"ocr_line\" id=\"line_1_21\" title=\"bbox 2975 2389 3132 2414; baseline 0.006 -6; x_size 37.25; x_descenders 6.5; x_ascenders 10.25\">\n      <html:span class=\"ocrx_word\" id=\"word_1_134\" title=\"bbox 2975 2389 3052 2414; x_wconf 96\"><html:strong><html:em>Page</html:em></html:strong></html:span>\n      <html:span class=\"ocrx_word\" id=\"word_1_135\" title=\"bbox 3078 2389 3132 2409; x_wconf 95\"><html:strong><html:em>IIB</html:em></html:strong></html:span>\n     </html:span>\n     <html:span class=\"ocr_line\" id=\"line_1_22\" title=\"bbox 1534 2423 1773 2443; baseline 0 0; x_size 37.25; x_descenders 6.5; x_ascenders 10.25\">\n      <html:span class=\"ocrx_word\" id=\"word_1_136\" title=\"bbox 1534 2423 1773 2443; x_wconf 93\"><html:strong><html:em>UNCLASSIFIED</html:em></html:strong></html:span>\n     </html:span>\n    </html:p>\n   </html:div>\n  </html:div>\n </html:body>\n</html:html>
        '''
    return txt1


if __name__ == '__main__':
    main()
