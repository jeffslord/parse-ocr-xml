class Word:
    def __init__(self, text, pos0: int, pos1: int, pos2: int, pos3: int, line=None):
        self.text = text
        self.setPosition(pos0, pos1, pos2, pos3)
        self.line = line

    def __repr__(self):
        return self.text + ' [' + 'Left:' + str(self.posLeft) + ' Top:' + str(self.posTop) + ' Right:' + str(self.posRight) + ' Bottom:' + str(self.posBottom) + ']'

    def setPosition(self, pos0, pos1, pos2, pos3):
        self.posLeft = int(pos0)
        self.posTop = int(pos1)
        self.posRight = int(pos2)
        self.posBottom = int(pos3)

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
    def tryMergeHorizontal(wordLeft, wordRight, maxDist=50):
        if(Word.checkSameLine(wordLeft, wordRight)):
            return Word.checkHorizontalDistance(wordLeft, wordRight, maxDist)
        else:
            return False

    @staticmethod
    def checkSameLine(wordLeft, wordRight):
        leftWordMidPoint = int(wordLeft.posTop) + \
            ((int(wordLeft.posBottom) - int(wordLeft.posTop))/2)
        rightWordMidPoint = int(wordRight.posTop) + \
            ((int(wordRight.posBottom) - int(wordRight.posTop))/2)
        if(int(wordRight.posTop) <= leftWordMidPoint <= int(wordRight.posBottom)):
            return True
        elif(int(wordLeft.posTop) <= rightWordMidPoint <= int(wordLeft.posBottom)):
            return True
        else:
            return False

    @staticmethod
    def checkHorizontalDistance(wordLeft, wordRight, maxDist):
        distance = abs(int(wordLeft.posRight) - int(wordRight.posLeft))
        if(distance <= maxDist):
            return True

    @staticmethod
    def mergeWords(word1, word2):
        posLeft = min(int(word1.posLeft), int(word2.posLeft))
        posTop = min(int(word1.posTop), int(word2.posTop))
        posRight = max(int(word1.posRight), int(word2.posRight))
        posBottom = max(int(word1.posBottom), int(word2.posBottom))
        text = word1.text + ' ' + word2.text
        newWord = Word(text, posLeft, posTop, posRight, posBottom)
        return newWord

    @staticmethod
    def tryMergeVertical(wordTop, wordBottom, maxDist=20):
        if(Word.checkSameColumn(wordTop, wordBottom)):
            return Word.checkVerticalDistance(wordTop, wordBottom, maxDist)
        else:
            return False

    @staticmethod
    def checkSameColumn(wordTop, wordBottom):
        topWordMidPoint = int(wordTop.posLeft) + \
            ((int(wordTop.posRight) - int(wordTop.posLeft))/2)
        bottomWordMidPoint = int(wordBottom.posLeft) + \
            ((int(wordBottom.posRight) - int(wordBottom.posLeft))/2)
        if(int(wordBottom.posLeft) <= topWordMidPoint <= int(wordBottom.posRight)):
            return True
        elif(int(wordTop.posLeft) <= bottomWordMidPoint <= int(wordTop.posRight)):
            return True
        else:
            return False

    @staticmethod
    def checkVerticalDistance(wordTop, wordBottom, maxDist):
        distance = abs(int(wordTop.posBottom) - int(wordBottom.posTop))
        if(distance < maxDist):
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
