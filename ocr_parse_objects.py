class Word:
    def __init__(self, text, pos0, pos1, pos2, pos3, line=None):
        self.text = text
        self.setPosition(pos0, pos1, pos2, pos3)
        self.line = line

    def __repr__(self):
        return self.text + ' [' + 'Left:' + self.posLeft + ' Top:' + self.posTop + ' Right:' + self.posRight + ' Bottom:' + self.posBottom + ']'

    def setPosition(self, pos0, pos1, pos2, pos3):
        self.posLeft = pos0
        self.posTop = pos1
        self.posRight = pos2
        self.posBottom = pos3

    def setText(self, newText):
        self.text = newText

    def deleteSelf(self):
        if(self.line != None):
            self.line.removeWord(self)
        del(self)

    def setLine(self, newLine):
        if(self.line != None):
            self.line.removeWord(self)
        self.line = newLine

    @staticmethod
    def tryMergeHorizontal(wordLeft, wordRight, maxDist=4):
        if(abs(wordLeft.posRight - wordRight.posLeft) < maxDist):
            return True
        else:
            return False

    @staticmethod
    def mergeWords(word1, word2):
        posLeft = min(word1.posLeft, word2.posLeft)
        posTop = min(word1.posTop, word2.posTop)
        posRight = max(word1.posRight, word2.posRight)
        posBottom = max(word1.posBottom, word2.posBottom)
        text = word1.text + ' ' + word2.text
        newWord = Word(text, posLeft, posTop, posRight, posBottom)
        return newWord

    @staticmethod
    def tryMergeVertical(wordTop, wordBottom, maxDist=4):
        topWordMidPoint = wordTop.posLeft + \
            ((wordTop.posRight - wordTop.posLeft)/2)
        bottomWordMidPoint = wordBottom.posLeft + \
            ((wordBottom.posRight - wordBottom.posLeft)/2)
        if(wordBottom.posLeft <= topWordMidPoint <= wordBottom.posRight):
            return Word.checkVerticalDistane(wordTop, wordBottom, maxDist)
        elif(wordTop.posLeft <= bottomWordMidPoint <= wordTop.posRight):
            return Word.checkVerticalDistane(wordTop, wordBottom, maxDist)
        else:
            return False

    def checkVerticalDistane(self, wordTop, wordBottom, maxDist=4):
        if(abs(wordTop.posBottom - wordBottom.posTop) < maxDist):
            return True
        else:
            return False


class Line:
    def __init__(self):
        self.words = []

    def __repr__(self):
        words = ''
        for i in self.words:
            words += '\t' + str(i) + '\n'
        return 'Line -----\n' + words

    def addWord(self, word):
        if(word not in self.words):
            self.words.append(word)

    def removeWord(self, word):
        if(word in self.words):
            self.words.remove(word)
