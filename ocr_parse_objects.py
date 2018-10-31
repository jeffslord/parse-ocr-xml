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
    def tryMergeHorizontal(wordLeft, wordRight, maxDist=50):
        distance = abs(int(wordLeft.posRight) - int(wordRight.posLeft))
        if(distance <= maxDist):
            return True
        else:
            return False

    @staticmethod
    def mergeWords(word1, word2):
        posLeft = min(int(word1.posLeft), int(word2.posLeft))
        posTop = min(int(word1.posTop), int(word2.posTop))
        posRight = max(int(word1.posRight), int(word2.posRight))
        posBottom = max(int(word1.posBottom), int(word2.posBottom))
        text = word1.text + ' ' + word2.text
        newWord = Word(text, str(posLeft), str(posTop),
                       str(posRight), str(posBottom))
        return newWord

    @staticmethod
    def tryMergeVertical(wordTop, wordBottom, maxDist=20):
        topWordMidPoint = int(wordTop.posLeft) + \
            ((int(wordTop.posRight) - int(wordTop.posLeft))/2)
        bottomWordMidPoint = int(wordBottom.posLeft) + \
            ((int(wordBottom.posRight) - int(wordBottom.posLeft))/2)
        if(int(wordBottom.posLeft) <= topWordMidPoint <= int(wordBottom.posRight)):
            return Word.checkVerticalDistance(wordTop, wordBottom, maxDist)
        elif(int(wordTop.posLeft) <= bottomWordMidPoint <= int(wordTop.posRight)):
            return Word.checkVerticalDistance(wordTop, wordBottom, maxDist)
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
