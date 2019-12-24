import os
import sys
import random
import math
import time

class BadInputError(Exception):
    pass

class Player():

    def __init__(self, name):
        self.id = None
        self.name = name
        self.type = 'Human'
        self.hand = Hand()
        self.legalCards = []
        self.wildCards = []
        self.valueChangeCards = []
        self.zeroCards = []
        self.canSkip = False
        self.canReverse = False
        self.canDrawTwo = False
        self.canDrawFour = False
        self.canValueChange = False
        self.drew = False
        self.scrollMax = 0
        self.points = 0
        self.forceDraw = 0

    def addCard(self, card):
        self.drew = True
        if self.forceDraw > 0:
            self.forceDraw -= 1
            self.drew = False
        self.hand.addCard(card)

    def beginTurn(self):
        self.drew = False

    def didDraw(self):
        return self.drew

    def getLegalCards(self, color, value, zeroChange=False):
        self.canSkip = False
        self.canReverse = False
        self.canDrawTwo = False
        self.canDrawFour = False
        self.canValueChange = False
        self.canZeroChange = False
        self.legalCards = []
        self.wildCards = []
        self.valueChangeCards = []
        self.zeroCards = []
        plusFours = []
        for card in self.hand:
            if card.isWild():
                if card.getValue() == '+4':
                    plusFours.append(card)
                else:
                    self.wildCards.append(card)
            elif zeroChange and card.isZero():
                self.canZero = True
                self.zeroCards.append(card)
            elif card.getColor() == color or card.getValue() == value:
                if card.getColor() != color:
                    self.canValueChange = True
                    self.valueChangeCards.append(card)
                if card.getValue() == "+2":
                    self.canDrawTwo = True
                elif card.getValue() == 'R':
                    self.canReverse = True
                elif card.getValue() == 'X':
                    self.canSkip = True
                self.legalCards.append(card)
        if len(self.legalCards) == 0 and len(plusFours) > 0:
            self.canDrawFour = True
            self.wildCards += plusFours

    def getValidCards(self):
        return self.legalCards

    def getAllValidCards(self):
        return self.legalCards + self.wildCards + self.zeroCards

    def hasLegalCard(self):
        return len(self.legalCards) > 0

    def addPoints(self, amount):
        if (self.points + amount) <= 999999999999999999999:
            self.points += amount

    def removeCard(self, index):
        return self.hand.removeCard(index)

    def assignID(self, identity):
        self.id = identity

    def getName(self):
        return self.name

    def getID(self):
        return self.id

    def getPoints(self):
        return self.points

    def getType(self):
        return self.type

    def getCardNum(self):
        return len(self.hand)

    def getHand(self, scrollNum=0, hide=False):
        return self.hand.show(scrollNum, hide)

    def getForceDraws(self):
        return self.forceDraw

    def addForceDraw(self, num):
        self.forceDraw += num

    def decreaseForceDraw(self):
        self.forceDraw -= 1

    def removeForceDraw(self):
        self.forceDraw = 0

    def checkCard(self, index):
        return self.hand.getCard(int(index))

    def discardHand(self):
        self.hand.discard()

    def __str__(self):
        return self.name

    def __repr__(self):
        return '({},{})'.format(self.name, self.points)

class Hand():
    ''''deck' (Deck) : Card's Color (rgby)
       'numberOfCards' (int) : Card's Value (0-9, R, X, W, +2, +4)'''

    def __init__(self, deck=None,numberOfCards=0):
        self.hand = []
        if deck != None:
            self.draw(deck,numberOfCards)

    def __iter__(self):
        return iter(self.hand)

    def __len__(self):
        return len(self.hand)

    def __getitem__(self, item):
        try:
            return self.hand[item]
        except:
            return ''

    def addCard(self, card):
        self.hand.append(card)

    def removeCard(self, index):
        index = int(index)
        if (0 <= index < len(self)):
            return self.hand.pop(index)

    def discard(self):
        self.hand = []

    def show(self, scrollNum=0, hide=False):
        if scrollNum == -1:
            scrollNum = 0
        output = ''
        num = 0
        header, footer, upper, lower = '', '', '', ''
        header +=   ('\033[97m\u2666--\u2666\033[0m ')
        upper +=    ('\033[97m|<-|\033[0m ')
        lower +=    ('\033[97m|<-|\033[0m ')
        footer +=   ('\033[97m\u2666--\u2666\033[0m ')
        for i in range(10):
            indexNum = i+(10*scrollNum)
            if indexNum < len(self):
                header += (self[indexNum].getRow(0,hide)+' ')
                upper += (self[indexNum].getRow(1,hide)+' ')
                lower += (self[indexNum].getRow(2,hide)+' ')
                footer += (self[indexNum].getRow(3,hide)+' ')
                num += 1
        for j in range(10-num):
            j #unused
            header += ('     ')
            footer += ('     ')
            upper += ('     ')
            lower += ('     ')
        header +=   ('\033[97m\u2666--\u2666\033[0m ')
        upper +=    ('\033[97m|->|\033[0m ')
        lower +=    ('\033[97m|->|\033[0m ')
        footer +=   ('\033[97m\u2666--\u2666\033[0m ')
        output += ('  '+header+'\n  '+upper+'\n  '+lower+'\n  '+footer+'\n\033[97m|-(<)--')
        for k in range(num):
            output += '({})'.format(k)
            output += '--'
        for l in range(10-num):
            l #unused
            output += '-----'
        output += '(>)--|\033[0m\n'
        return output

    def getCard(self, index):
        return self.hand[index]

    def indexCard(self, card):
        return self.hand.index(card)

class GameSettings():

    playerIdentities = ('play1','play2','play3','play4')
    computerNames = ('Watson','SkyNet','Hal','Metal Gear')

    def __init__(self):
        self.playerStaging = []                  #    Where Player Objs Are Stored Before Game Starts
        self.players = {}                        #    ID : Player Obj
        self.numPlayers = 0
        self.useColor = True
        self.displayEffects = True
        self.hideComputerHands = True
        self.zeroChange = False
        self.computerSimulation = False
        self.mainMenuError = ''
        self.computerSpeed = 'normal'

    def canAddPlayer(self):
        return (self.numPlayers < 4)

    def canRemovePlayer(self):
        return (self.numPlayers > 0)

    def canBegin(self):
        return (self.numPlayers > 1)

    def addPlayer(self, player):
        self.playerStaging.append(player)
        self.numPlayers += 1

    def removePlayer(self, number):
        number -= 1
        del self.playerStaging[number]
        self.numPlayers -= 1

    def clearStaging(self):
        self.numPlayers = 0
        self.playerStaging = []

    def finalizePlayers(self):
        self.players.clear()
        identity = 0
        for player in self.playerStaging:
            playerID = self.playerIdentities[identity]
            player.assignID(playerID)
            self.players[playerID] = player
            identity += 1

    def getPlayerNum(self):
        return self.numPlayers

    def getComputerName(self):
        complete = False
        index = self.numPlayers
        while not complete:
            name = self.computerNames[index]
            complete = True
            for player in self.playerStaging:
                if player.getName() == name:
                    index += 1
                    if index >= len(self.computerNames):
                        index = 0
                        complete = False

        return self.computerNames[index]

    def getRandomIdentity(self):
        '''For Getting a Random Player for First Turn.'''
        return random.choice(self.players.keys())

    def compileMainMenuElements(self):
        def getBlankSpace(word, total):
            return " "*(total-len(word))

        def getPlayerBox(playerNum, rowNum):
            if rowNum == 1:
                name = self.playerStaging[playerNum-1].getName()
                return '{}{}'.format(name, getBlankSpace(name, 29))
            elif rowNum == 2:
                points = self.playerStaging[playerNum-1].getPoints()
                return 'Points: {}{}'.format(points, getBlankSpace(str(points), 21))

        self.mainMenuElements= {'play1row1':'No Player                    ','play1row2':'                             ',
                                'play2row1':'No Player                    ',
                                'play2row2':'                             ',
                                'play3row1':'No Player                    ','play3row2':'                             ',
                                'play4row1':'No Player                    ',
                                'play4row2':'                             ',
                                'play1box':'\033[90m','play2box':'\033[90m','play3box':'\033[90m','play4box':'\033[90m',
                                'beginBox':'\033[90m','addBox':'\033[97m','removeBox':'\033[90m'
                                }
        playerBoxKey = 'play{}box'
        playerRowKey = 'play{}row{}'
        i = 1
        for j in self.playerStaging:
            j
            colorCode = ['\033[91m','\033[94m','\033[92m','\033[93m']
            key = playerBoxKey.format(i)
            self.mainMenuElements[key] = colorCode[i-1]
            self.mainMenuElements[playerRowKey.format(i,1)] = getPlayerBox(i, 1)
            self.mainMenuElements[playerRowKey.format(i,2)] = getPlayerBox(i, 2)
            i+=1
        if self.canBegin():
            self.mainMenuElements['beginBox'] = '\033[95m'
        if not self.canAddPlayer():
            self.mainMenuElements['addBox'] = '\033[90m'
        if self.canRemovePlayer():
            self.mainMenuElements['removeBox'] = '\033[97m'

    def changeComputerSpeed(self):
        if self.computerSpeed == 'slow':
            self.computerSpeed = 'normal'
        elif self.computerSpeed == 'normal':
            self.computerSpeed = 'fast'
        elif self.computerSpeed == 'fast':
            self.computerSpeed = 'slow'

    def getMainMenuElements(self):
        return self.mainMenuElements

class Deck():
    ''''shuffle' (bool) : shuffle deck.'''

    colors =     ('red','yellow','green','blue')
    values =     ('0','1','2','3','4','5','6','7','8','9','X','R','+2')

    def __init__(self, populate):
        '''Initializes proper deck of 108 Uno Cards.'''
        self.deck = []
        if populate:
            self.populate(True)

    def __getitem__(self, index):
        return self.deck[index]

    def populate(self, shuffle=True):
        for color in self.colors:
            for value in self.values:
                self.deck.append(Card(color, value))
                if value != '0':
                    self.deck.append(Card(color, value))
        for i in range(4):
            i #unused
            self.deck.append(Card('wild', '+4'))
            self.deck.append(Card('wild', 'W'))
        if shuffle:
            self.shuffle()

    def __iter__(self):
        return iter(self.deck)

    def __len__(self):
        return len(self.deck)

    def draw(self):
        return self.deck.pop()

    def place(self, card):
        return self.deck.append(card)

    def insert(self, card):
        self.deck.insert(0, card)

    def shuffle(self):
        random.shuffle(self.deck)

class ComputerPlayer(Player):

    def __init__(self, name):
        super().__init__(name)
        self.type = 'Computer'
        self.begun = False
        self.colorsInHand = {'red':0, 'blue':0, 'green':0, 'yellow':0, 'wild':0}
        self.colorsOutHand = {}
        self.currentColor = ""

    def addCard(self, card):
        Player.addCard(self, card)
        color = card.getColor()
        self.colorsInHand[color] += 1

    def indexCard(self, cardColor, cardValue):
        for card in self.hand:
            if card.getValue() == cardValue:
                if cardValue in ('+4', 'W'):
                    return self.hand.indexCard(card)
                else:
                    if card.getColor() == cardColor:
                        return self.hand.indexCard(card)
        raise ValueError("Card Cannot Be Found")

    def think(self, match):
        card = None
        self.currentColor = match.currentColor
        currentValue = match.currentValue
        zeroChangeRule = match.zeroChange
        twoPlayers = False
        previousTurnID = match.getNextTurn(True)
        nextTurnID = match.getNextTurn(False)
        previousPlayer = match.getPlayer(previousTurnID)
        #nextPlayer = match.getPlayer(nextTurnID)
        if previousTurnID == nextTurnID:
            twoPlayers = True
            if self.canSkip == False and self.canReverse == True:
                self.canSkip = True
            self.canReverse = False

        self.getLegalCards(self.currentColor, currentValue, zeroChangeRule)

        ### DRAW CASE ###

        if len(self.legalCards) == 0 and len(self.wildCards) == 0:
            return "d"

        else:

            ### NO LEGAL CARD, USE WILD CARD ###

            if len(self.legalCards) == 0:

                if zeroChangeRule and self.canZeroChange:
                    bestZeroColor = self.getBestColor(self.zeroCards)
                    card = self.getCardByColor(self.zeroCards, bestZeroColor)

                else:

                    if self.canDrawFour:
                        card = self.getCardByValue(self.wildCards, "+4")
                        print(card)

                    else:
                        card = random.choice(self.wildCards)

            else:

                ### HAS LEGAL CARD ###

                if twoPlayers and self.canSkip: #Always play a skip card in a two player game
                    #print("Shed Skip Strategy")
                    card = self.getCardByValue(self.legalCards,"R", "X")

                if self.canReverse and previousPlayer.didDraw():
                    #print("Reverse Strategy")
                    reverseCards = self.getAllCardsByValue(self.legalCards, "R")
                    for reverseCard in reverseCards:
                        if reverseCard.getColor() == self.currentColor:
                            card = reverseCard

                if self.canValueChange:
                    # Computer Can Value Change, However, Should it?
                    # Computer Checks to See if Value Change Color is Better Than Current
                    currentColorNum = self.colorsInHand[self.currentColor]
                    bestValueChangeColor = self.getBestColor(self.valueChangeCards)
                    if self.colorsInHand[bestValueChangeColor] > currentColorNum or len(self.valueChangeCards) == len(self.legalCards):
                        card = self.getCardByColor(self.valueChangeCards, bestValueChangeColor)


                if card == None:
                    #print("Random Strategy")
                    card = random.choice(list(set(self.legalCards) - set(self.valueChangeCards)))

        color = card.getColor()
        self.colorsInHand[color] -= 1
        return str(self.indexCard(card.getColor(), card.getValue()))

    def getWildColor(self):
        maxKey = max(self.colorsInHand, key=self.colorsInHand.get)
        if maxKey == 'wild':
            return random.choice(('r','g','b','y'))
        else:
            return maxKey

    def getCardByValue(self, cardList, *values):
        for card in cardList:
            if card.getValue() in values:
                return card

    def getAllCardsByValue(self, cardList, *values):
        cards = []
        for card in cardList:
            if card.getValue() in values:
                cards.append(card)
        return cards

    def getCardByColor(self, cardList, *colors):
        for card in cardList:
            if card.getColor() in colors:
                return card

    def getBestColor(self, cardList):
        bestColor = None
        bestColorNum = 0
        for card in cardList:
            color = card.getColor()
            if self.colorsInHand[color] > bestColorNum:
                bestColor = color
                bestColorNum = self.colorsInHand[color]
        return bestColor

class Card():
    '''
    'suit' (string) : Card's Color (rgby)
    'rank' (string) : Card's Value (0-9, R, X, W, +2, +4)
    '''

    colors = {
        'red'       :   '\033[91m',
        'green'     :   '\033[92m',
        'yellow'    :   '\033[93m',
        'blue'      :   '\033[94m',
        'purple'    :   '\033[95m',
        'cyan'      :   '\033[96m',
        'white'     :   '\033[97m',
        'wild'      :   '',
        'dwild'     :   '',
        'dred'       :   '\033[31m',
        'dgreen'     :   '\033[32m',
        'dyellow'    :   '\033[33m',
        'dblue'      :   '\033[34m',
        'dpurple'    :   '\033[35m',
        'dcyan'      :   '\033[36m',
        'dwhite'     :   '\033[37m',
    }

    idMap = {
        'red':'R','blue':'B','green':'G','yellow':'Y','wild':'W',
        '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',
        '+2':'+','R':'R','W':'W','+4':'$','X':'X'
    }

    bigNums = {
        "0" : [" .d888b. ","d88P Y88b","888   888","888   888","888   888","888   888","d88P Y88b"," \"Y888P\" "],
        "1" : ["  d888   "," d8888   ","   888   ","   888   ","   888   ","   888   ","   888   "," 8888888 "],
        "2" : [".d8888b. ","d88P  Y88","d8    888","    .d88P",".od888P\" ","d88P\"    ","888\"     ","888888888"],
        "3" : [" .d8888b.","d88P  Y88","     .d88","   8888\" ","     \"Y8b","888    88","Y88b  d88"," \"Y8888P\""],
        "4" : ["    d88b ","   d8P88 ","  d8  88 "," d8   88 ","d8    88 ","888888888","      88 ","      88 "],
        "5" : ["888888888","888      ","888      ","8888888b ","   \"Y88b ","      888","Y88b d88P","\"Y8888P\" "],
        "6" : [" .d888b. ","d88P Y88b","888      ","888d888b ","888P \"Y8b","888   888","Y88b d88b"," \"Y888P\" "],
        "7" : ["888888888","      d8P","     d8P ","    d8P  "," 8888888 ","  d8P    "," d8P     ","d8P      "],
        "8" : [" .d888b. ","d8P   Y8b","Y8b.  d8P"," \"Y8888\" "," .dP\"Yb. ","888   888","Y88b d88P"," \"Y888P\" "],
        "9" : [" .d888b. ","d8P   Y8b","88     88","Y8b.  d88"," \"Y88P888","      888","Y88b d88P"," \"Y888P\" "],
        "X" : ["Y8b   d8P"," Y8b d8P ","  Y8o8P  ","   Y8P   ","   d8b   ","  d888b  "," d8P Y8b ","d8P   Y8b"],
        "W" : ["88     88","88     88","88  o  88","88 d8b 88","88d888b88","88P   Y88","8P     Y8","P       Y"],
        "+2" : ["  db     ","  88     ","C8888D   ","  88 8888","  VP    8","     8888","     8   ","     8888"],
        "+4" : ["  db     ","  88     ","C8888D   ","  88   d ","  VP  d8 ","     d 8 ","    d8888","       8 "],
        "R9" : ["    d88P ","   d88P  ","  d88P   "," d88P    "," Y88b    ","  Y88b   ","   Y88b  ","    Y88b "],
        "R8" : ["   d88P  ","  d88P   "," d88P    ","d88P     ","Y88b     "," Y88b    ","  Y88b   ","   Y88b  "],
        "R7" : ["  d88P  Y"," d88P    ","d88P     ","88P      ","88b      ","Y88b     "," Y88b    ","  Y88b  d"],
        "R6" : [" d88P  Y8","d88P    Y","88P      ","8P       ","8b       ","88b      ","Y88b    d"," Y88b  d8"],
        "R5" : ["d88P  Y88","88P    Y8","8P      Y","P        ","b        ","8b      d","88b    d8","Y88b  d88"],
        "R4" : ["88P  Y88b","8P    Y88","P      Y8","        Y","        d","b      d8","8b    d88","88b  d88P"],
        "R3" : ["8P  Y88b ","P    Y88b","      Y88","       Y8","       d8","      d88","b    d88P","8b  d88P "],
        "R2" : ["P  Y88b  ","    Y88b ","     Y88b","      Y88","      d88","     d88P","    d88P ","b  d88P  "],
        "R1" : ["  Y88b   ","   Y88b  ","    Y88b ","     Y88b","     d88P","    d88P ","   d88P  ","  d88P   "],
        "R0" : [" Y88b    ","  Y88b   ","   Y88b  ","    Y88b ","    d88P ","   d88P  ","  d88P   "," d88P    "],
    }


    def __init__(self, color, value):
        '''Initializes Uno Card w/ Color and Value.'''
        self.wild = False       #Is wild card?
        self.zero = False
        self.cardID = '{}{}'.format(self.idMap[color],self.idMap[value])
        self.setColor(color)
        self.setValue(value)
        self.setPoints(value)


    #############################################

    ### -\/-  Retrieve Card Information  -\/- ###

    def __repr__(self):
        return "{},{}".format(self.color, self.value)

    def getBigNum(self, reverse, reverseSeed=0):
        '''Returns list of strings to draw card's value on the pile.'''
        bigNums = []
        colorCode = self.colorCode
        colorCodeDark = self.colorCodeDark
        value = self.value
        if value == 'R':
            if not reverse:
                value += str(reverseSeed)
            else:
                value += str(9-reverseSeed)
        for mid in self.bigNums[value]:
            bigNums += ['{}| |{}'.format(colorCode,colorCodeDark)+mid+'{}| |\033[0m\t'.format(colorCode)]

        return bigNums

    def getColor(self):
        '''Returns card's color.'''
        return self.color

    def getColorCode(self):
        '''Returns card's color code.'''
        return self.colorCode

    def getValue(self):
        '''Returns card's value.'''
        return self.value

    def getPoints(self):
        '''Returns card's point value.'''
        return self.points

    def getRow(self,rowNum,hide=False):
        value = self.value
        displaySpace = self.displaySpace
        if hide:
            colorCode = '\033[97m'
            value = '?'
            displaySpace = ' '
        else:
            colorCode = self.colorCode
            if self.isWild():
                if rowNum == 0:
                    colorCode = '\033[91m'
                elif rowNum == 1:
                    colorCode = '\033[93m'
                elif rowNum == 2:
                    colorCode = '\033[92m'
                elif rowNum == 3:
                    colorCode = '\033[94m'

        if rowNum == 0:
            return      '{}\u2666--\u2666\033[0m'.format(colorCode)
        elif rowNum == 1:
            return      '{}|{}{}|\033[0m'.format(colorCode, displaySpace, value)
        elif rowNum == 2:
            if hide:
                return   '{}|? |\033[0m'.format(colorCode)
            else:
                return   '{}|  |\033[0m'.format(colorCode)
        elif rowNum == 3:
            return      '{}\u2666--\u2666\033[0m'.format(colorCode)

    #############################################

    ### -\/-  Set Card Information  -\/- ###

    def setColor(self, color):
        '''Sets Card's color and escape code.'''
        if color == 'blue':
            self.color = 'blue'
            self.colorCode = self.colors['blue']
            self.colorCodeDark = self.colors['dblue']
        elif color == 'red':
            self.color = 'red'
            self.colorCode = self.colors['red']
            self.colorCodeDark = self.colors['dred']
        elif color == 'yellow':
            self.color = 'yellow'
            self.colorCode = self.colors['yellow']
            self.colorCodeDark = self.colors['dyellow']
        elif color == 'green':
            self.color = 'green'
            self.colorCode = self.colors['green']
            self.colorCodeDark = self.colors['dgreen']
        elif color == 'wild':         #No color modification
            self.wild = True
            self.color = 'wild'
            self.colorCodeDark = self.colors['dwild']
            self.colorCode = self.colors['wild']

    def setValue(self, value):
        if value in ('0','1','2','3','4','5','6','7','8','9','X','R','+2','+4','W'):
            self.value = value
            self.displaySpace = ' '
            if len(value) == 2:
                self.displaySpace = ''
            if value == '0':
                self.zero = True

    def setPoints(self, value):
        if value in ('0','1','2','3','4','5','6','7','8','9'):
            self.points = int(value)
        elif value in ("W", "+4"):
            self.points = 50
        else:
            self.points = 20


    #############################################

    ### -\/-  Wild Card Methods  -\/- ###

    def changeColor(self, color):
        '''Changes Card's Color, Intended for Wild Cards.'''
        self.setColor(color)

    def isWild(self):
        '''Returns if card is a wild card.'''
        return self.wild

    def isZero(self):
        return self.zero

class Match():

    elementsInit = {
        ### Names (final) ###
        'P1Name':'           ', 'P2Name':'           ', 'P3Name':'           ', 'P4Name':'           ',
        ### Card Values ###
        'P1Cards':'           ', 'P2Cards':'           ', 'P3Cards':'           ', 'P4Cards':'           ',
        ### Turn Colors / Hand###
        'P1Turn':'', 'P2Turn':'', 'P3Turn':'', 'P4Turn':'',
        'HName':'\t\t', 'HVisual':'' ,'Hand':'',
        ### Deck ###
        'DNum':'', 'Deck':['','','','','','','','',''],
        'PostDNum':'',
        ### Pile ###
        'uHeader':'\t\t\t\t', 'uMiddle':'   ', 'uLower':'   ',
        'oHeader':'\t\t\t', 'oMiddle':['\t\t\t','\t\t\t','\t\t\t','\t\t\t','\t\t\t','\t\t\t','\t\t\t','\t\t\t'],
        ### Messages ###
        'Console':'', 'Error':''
        }

    speeds = {'slow':2,'normal':1,'fast':0}


    def __init__(self, gs):
        ### Decks ###
        self.deck = Deck(True)
        self.pile = Deck(False)

        ### Player Information ###
        self.players = gs.players
        self.turnList = []
        self.handTitles =  {'play1':'','play2':'','play3':'','play4':''}

        ### Carry Information ###
        self.displayEffects = gs.displayEffects
        self.hideComputerHands = gs.hideComputerHands
        self.zeroChange = gs.zeroChange
        self.computerSpeed = self.speeds[gs.computerSpeed]
        self.simulation = gs.computerSimulation

        ### Data ###
        self.handPosition = 0               # For hand displays
        self.drawAmount = 0                 # Used for force draws
        self.passes = 0                     # Keep track of consecutive passes for emergency color change
        self.passMax = 0                    # Max passes before color change
        self.turn = ''                      # Current turn
        self.event = ''                     # Wild, Reverse, Skip, etc
        self.wildColorChange = ''           # Specifies color to change wild card to
        self.currentColor = ''              # Current color
        self.currentValue = ''              # Current value
        self.winnerID = ''                  # ID of Player who Won
        self.reverse = False                # Is turn order reversed
        self.turnComplete = False           # Is turn complete
        self.matchComplete = False          # Is the Game over?
        self.matchAbort = False             # Did the match conclude without a winner?
        self.forcedWild = False             # Force change wild

        ### Initialize Names / Cards / Deck (Assuming New Game) ###
        self.elements = dict(self.elementsInit)

        keyStringName = 'P{}Name'
        keyStringCards = 'P{}Cards'

        for i in self.players:
            self.elements[keyStringName.format(i[-1])] = self.players[i].getName()+(' '*(11-len(self.players[i].getName())))
            self.elements[keyStringCards.format(i[-1])] = '  '+(' '*(3-len(str(self.players[i].getCardNum()))))+str(self.players[i].getCardNum())+' Cards'

        self.elements['DNum'] = len(self.deck)

        if len(str(len(self.deck))) < 2:
            self.elements['PostDNum'] = '\t'

        j = 8
        for i in range(int(math.ceil(len(self.deck)/12))):
            self.elements['Deck'][j] = '='
            j -= 1

        for key in GameSettings.playerIdentities:
            try:
                self.buildHandString(key)
                self.turnList += [key]
            except KeyError:
                pass

        self.passMax = len(self.turnList)

    def clearShell(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def begin(self):
        self.elements['Console'] = 'Beginning Game, Press Enter'
        print(self.drawScreen())
        self.enterBreak()
        self.eventDealCards()
        self.turn = random.choice(self.turnList)
        self.elements['Console'] = 'First turn will be {}. Press Enter.' .format(self.players[self.turn].getName())
        print(self.drawScreen(True))
        self.enterBreak()
        self.placeCard()
        self.elements['P{}Turn'.format(self.turn[-1])] = '\033[93m'
        if self.event == 'wild':
            self.eventWildCard()
        elif self.event == 'reverse':
            self.eventReverse()

    def end(self, gs):
        if not self.matchAbort:
            points = 0
            self.elements['P{}Turn'.format(self.turn[-1])] = ''
            self.elements['Console'] = '{} Wins! Press Enter to Begin Point Tally'.format(self.players[self.winnerID].getName())
            print(self.drawScreen())
            self.enterBreak()

            for identity in self.turnList:
                if identity != self.winnerID:
                    self.turn = identity
                    self.elements['HName'] = self.handTitles[self.turn]
                    self.elements['P{}Turn'.format(self.turn[-1])] = '\033[93m'
                    while self.players[identity].getCardNum() > 0:
                        card = self.players[identity].removeCard(0)
                        points += card.getPoints()
                        self.elements['Console'] = '{} Won {} Points!'.format(self.players[self.winnerID].getName(),points)

                        keyStringCards = 'P{}Cards'
                        self.elements[keyStringCards.format(identity[-1])] = '  '+(' '*(3-len(str(self.players[identity].getCardNum()))))+str(self.players[identity].getCardNum())+' Cards'
                        self.players[identity].maxScroll = math.ceil((self.players[identity].getCardNum() / 10)-1)
                        if self.handPosition > self.players[identity].maxScroll:
                            self.handPosition -= 1
                        self.buildHandVisual(identity)

                        if self.displayEffects and not self.simulation:
                            print(self.drawScreen())
                            time.sleep(.1)
                    self.elements['P{}Turn'.format(self.turn[-1])] = ''

            self.players[self.winnerID].addPoints(points)
            self.elements['Console'] = '{} Won {} Points! Press Enter'.format(self.players[self.winnerID].getName(),points)
            print(self.drawScreen())
            self.enterBreak()

        gs.clearStaging()
        for identity in self.turnList:
            self.players[identity].discardHand()
            gs.addPlayer(self.players[identity])
        return gs

    def adjustCardAmount(self, playerID):
        keyStringCards = 'P{}Cards'
        self.elements[keyStringCards.format(playerID[-1])] = '  '+(' '*(3-len(str(self.players[playerID].getCardNum()))))+str(self.players[playerID].getCardNum())+' Cards'
        self.players[playerID].maxScroll = math.ceil((self.players[player].getCardNum() / 10)-1)
        if self.handPosition > self.players[playerID].maxScroll:
            self.handPosition -= 1
        self.buildHandVisual(playerID)

    def buildHandString(self, playerID):
        playerName = self.players[playerID].getName()
        if len(playerName) < 9:
            self.handTitles[playerID] = "{}'s Hand\t".format(self.players[playerID].getName())
        else:
            self.handTitles[playerID] = "{}'s Hand".format(self.players[playerID].getName())

    def buildHandVisual(self, playerID):
        string ='['
        for i in range(self.players[playerID].maxScroll+1):
            if i == self.handPosition:
                string += '|'
            else:
                string += '-'
        string +=']'
        self.elements['HVisual'] = string

    def checkInput(self, playerInput):
        if playerInput == '':
            return {'valid':False,'entry':playerInput}
        if playerInput.isnumeric():
            if int(playerInput)+(10*self.handPosition) < self.players[self.turn].getCardNum():
                return {'valid':True,'entery':str(int(playerInput)+(10self.handPosition)),'type':'card'}
            else:
                self.elements['Error'] = '{} is not a card.'.format(playerInput)
                return {'valid': False,'entry':playerInput}
        else:
            playerInput = playerInput.lower()[0]
            if playerInput in ['<','>','u','d','p','q','s']:
                return {'valid':True, 'entry':playerInput}
            else:
                self.elements['Error'] = '{} is not a valid selection.'.format(playerInput)
                return {'valid':False,'entry':playerInput}

    def checkColorInput(self, playerInput):
        if playerInput = '':
            return {'valid':False,'entry':playerInput}
        playerInput = str(playerInput).lower()[0]
        if playerInput[0] == 'b':
            return {'valid':True,'entry':'blue'}
        elif playerInput[0] == 'r':
            return {'valid':True,'entry':'red'}
        elif playerInput[0] == 'g':
            return {'valid':True,'entry':'green'}
        elif playerInput[0] == 'y':
            return {'valid':True,'entry':'yellow'}
        return {'valid':False,'entry':playerInput}

    def eventDealCards(self):
        if self.displayEffects and not self.simulation:
            self.elements['Console'] = 'Dealing Cards...'
        for i in ('play1','play2','play3','play4'):
            if i in self.players:
                for j in range(7):
                    j #unused
                    self.dealCard(i)
                    if self.displayEffects and not self.simulation:
                        print(self.drawScreen(True))
                        time.sleep(.1)

    def eventReverse(self):
        if self.displayEffects and not self.simulation:
            hide = False
            if self.players[self.turn].getType() == "Computer":
                hide = self.hideComputerHands
            self.elements['Console'] = "Reverse Card Played! Reversing Turn Order.".format(self.players[self.turn].getName())
            print(self.drawScreen(hide))
            time.sleep(1)
            for i in range(10):
                cardBigNums = self.pile[0].getBigNum(self.reverse,i)
                self.elements['oMiddle'] = cardBigNums
                print(self.drawScreen(hide))
                if self.displayEffects and not self.simulation:
                    time.sleep(.1)
        cardBigNums = self.pile[0].getBigNum(self.reverse,9)
        self.elements['oMiddle'] = cardBigNums
        self.reverse = not self.reverse
        self.event = ''

    def eventSkip(self):
        if self.displayEffects and not self.simulation:
            hide = False
            if self.players[self.turn].getType() == "Computer":
                hide = self.hideComputerHands
            self.elements['Console'] = "Skip Card Placed! Skipping {}'s Turn.".format(self.players[self.turn].getName())
            print(self.drawScreen(hide))
            time.sleep(1)
            for i in range(2):
                i #unused
                self.elements['P{}Turn'.format(self.turn[-1])] = '\033[91m'
                print(self.drawScreen(hide))
                time.sleep(.3)
                self.elements['P{}Turn'.format(self.turn[-1])] = ''
                print(self.drawScreen(hide))
                time.sleep(.3)
        self.turnComplete = True
        self.event = ''

    def eventWildCard(self):
        hide = False
        if not self.forcedWild:
            if self.players[self.turn].getType() == 'Human':
                self.elements['Console'] = 'Wild Card! Specifiy a Color: (B)lue, (R)ed, (G)reen, (Y)ellow'
                self.elements['Error'] = 'Specifiy A Color'
                print(self.drawScreen())
                playerInput = str(input("Color Change: "))
                checked = self.checkColorInput(playerInput)
                while not checked['valid']:
                    if checked['entry'] == '<':
                        self.handPosition -= 1
                        if self.handPosition == -1:
                            self.handPosition = self.players[self.turn].maxScroll
                        self.buildHandVisual(self.turn)
                    elif checked['entry'] == '>':
                        self.handPosition += 1
                        if self.handPosition > self.players[self.turn].maxScroll:
                            self.handPosition = 0
                        self.buildHandVisual(self.turn)
                    print(self.drawScreen())
                    playerInput = str(input("Color Change: "))
                    checked = self.checkColorInput(playerInput)
            else:
                hide = self.hideComputerHands
                checked = self.checkColorInput(self.player[self.turn].getWildColor())
            self.wildColorChange = checked['entry']
        else:
            self.wildColorChange = self.checkColorInput(random.choice(('r','b','g','y')))['entry']
            self.forcedWild = False
        self.currentColor = self.wildColorChange
        self.elements['Error'] = ""
        if self.displayEffects and not self.simulation:
            self.elements['Console'] = 'Wild Card! Changing Color.'
            seed = 1
            for i in range(10):
                i #unused
                if seed > 4:
                    seed = 1
                print(self.drawScreen(hide,wildSeed=seed))
                time.sleep(.1)
                seed += 1
        self.pile[0].changeColor(self.wildColorChange)
        self.wildColorChange = ''
        cardBigNums = self.pile[0].getBigNum(self.reverse)
        self.elements['oHeader'] = '{}\u2666\u2666\u2666=========\u2666\u2666\u2666\033[0m\t'.format(self.pile[0].getColorCode())
        self.elements['oHeader'] = cardBigNums
        self.event = ''

    def eventDraw(self):
        self.players[self.turn].addForceDraw(self.drawAmount)
        self.drawAmount = 0
        self.event = ''

    def dealCard(self. playerID):

        card = self.deck.draw()
        self.players[playerID].addCard(card)

        ### Adjust Hand Visual ###
        self.players[playerID].maxScroll = math.ceil((self.players[playerID].getCardNum() / 10)-1)
        self.handPosition = self.players[playerID].maxScroll
        self.buildHandVisual(playerID)

        ### Ajust Player Title ###
        
