import itertools, random, time, os
import StringFormatting
from DataStructures import Queue, CircularLinkedList

CURRENT_DIR = os.getcwd()
PLAYER_DIR = os.path.join(CURRENT_DIR, "Player_Hands")


class Card:

    RANK = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"}
    ROYALS = {"Jack": 11, "Queen": 12, "King": 13, "Ace": 14}
    SUITS = {"Diamonds", "Spades", "Hearts", "Clubs"}

    def __init__(self, rank, suit):
        if rank in Card.RANK and suit in Card.SUITS:
            self.rank = rank
            self.suit = suit
            self.value = self.findValue()
        else:
            return

    def findValue(self):
        try:
            return int(self.rank)
        except ValueError:
            return Card.ROYALS[self.rank]

    def getValue(self):
        return self.value

    def getRank(self):
        return self.rank

    def getSuit(self):
        return self.suit

    def __repr__(self):
        return self.rank + " of " + self.suit

    def __str__(self):
        return self.rank + " of " + self.suit

    def __eq__(self, other):
        return isinstance(other, Card) and (
            self.rank == other.rank and self.suit == other.suit
        )

    def __hash__(self):
        return hash((self.rank, self.suit))


class Deck:
    def __init__(self, numberOfDecks):
        deck = itertools.product(Card.RANK, Card.SUITS)
        self.cards = [
            Card(rank, suit) for (rank, suit) in deck for _ in range(numberOfDecks)
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def dealCard(self):
        return self.cards.pop(0)

    def addCard(self, card):
        self.cards.append(card)

    def addCards(self, cardList):
        self.cards.extend(cardList)


class Player:
    def __init__(self, name):
        self.money = 100
        self.name = name
        self.currentBet = 0
        self.currentPotContrib = 0
        self.totalPotContrib = 0
        self.folded = False
        self.isAllIn = False
        self.hole = []
        self.hand = []
        self.kickers = []
        self.handRank = 0

    def getCardHand(self, index):
        return self.hand[index]

    def getKicker(self, index):
        return self.kickers[index]

    def addCard(self, card):
        self.hole.append(card)
        self.hand.append(card)

    def addToHand(self, cards):
        self.hand.extend(cards)

    def setHand(self, cards):
        self.hand = cards

    def resetRound(self):
        self.currentBet = 0
        self.currentPotContrib = 0
        self.totalPotContrib = 0
        self.folded = False
        self.isAllIn = False
        self.hole = []
        self.hand = []
        self.kickers = []
        self.handRank = 0

    def call(self, stake):
        total = stake - self.currentBet
        self.money -= total
        self.currentBet = stake
        self.currentPotContrib += total
        self.totalPotContrib += total

        return self.currentBet

    def raiseOrBet(self, total):
        if self.money - total >= 0:
            self.currentBet += total
            self.money -= total
            self.currentPotContrib += total
            self.totalPotContrib += total
            if self.money == 0:
                self.isAllIn = True

            return self.currentBet

        return None

    def allIn(self):
        total = self.money
        self.currentBet += total
        self.currentPotContrib += self.money
        self.totalPotContrib += self.money
        self.money = 0
        self.isAllIn = True

        return self.currentBet

    def fold(self):
        self.folded = True

    def getValidChoices(self, stake, lastRaise, minBet):
        choices = set()
        if self.money - (stake - self.currentBet) > 0:
            if self.currentBet < stake:
                choices.add("call")
                if self.money - max(minBet, ((2 * lastRaise))) > 0:
                    choices.add("raise")

            else:
                choices.add("check")
                if self.money - max(minBet, (2 * lastRaise)) > 0:
                    choices.add("bet")

        choices.add("all in")
        choices.add("fold")
        choices.add("quit")

        return choices

    def validateRaiseBet(self, minBet, lastRaise, stake, raising=True):
        raisedBet = None
        increase = None

        if raising:
            stringRaiseOrBet = "raise"
        else:
            stringRaiseOrBet = "bet"

        StringFormatting.printWithSeperators(
            "type back at any time if you no longer want to " + stringRaiseOrBet, "*"
        )
        while not raisedBet:
            if raising:
                print("enter the amount you would like to raise to")
            amount = input(
                "how much would you like to " + stringRaiseOrBet + " "
            ).strip()

            if amount == "back":
                break
            try:
                amount = int(amount)
                if amount < 0:
                    print("You cannot " + stringRaiseOrBet + " a negative amount!")
                    continue

                elif amount < stake + (2 * lastRaise):
                    print(
                        "You must raise by a minimum of double the last raise or bet (min "
                        + str(2 * lastRaise)
                        + " chips) which takes the bet to "
                        + str(stake + (2 * lastRaise))
                        + " chips"
                    )

                elif amount < minBet:
                    print(
                        "You cannot "
                        + stringRaiseOrBet
                        + " less than the minimum bet which is "
                        + str(minBet)
                        + " chips"
                    )

                elif raising and amount == stake:
                    print(
                        "You must raise by at least "
                        + str(max(minBet, (2 * lastRaise)))
                        + " which takes the bet to "
                        + str(stake + max(minBet, (2 * lastRaise)))
                        + " chips"
                    )

                else:
                    if raising:
                        increase = amount - self.currentBet
                    else:
                        increase = amount

                    raisedBet = self.raiseOrBet(increase)

                    if not raisedBet:
                        print("Sorry but you don't have enough money!")

                    else:
                        raisedBet -= stake

            except ValueError:
                print("I'm sorry, you didn't enter a number")

        return raisedBet, increase

    def playTurn(self, stake, lastRaise, minBet):
        valid = self.getValidChoices(stake, lastRaise, minBet)
        played = False
        total = 0
        raisedBet = None
        infoString = (
            self.name
            + "'s chips: "
            + str(self.money)
            + "\npot contribution: "
            + str(self.totalPotContrib)
            + "\ntables bet: "
            + str(stake)
            + "\nyour current bet: "
            + str(self.currentBet)
        )
        while not played:
            StringFormatting.printWithSeperators(infoString, "*")
            choice = (
                input(self.name + " would you like to: " + ", ".join(valid) + " ")
                .lower()
                .strip()
            )
            if choice in valid:

                if choice == "raise":
                    raisedBet, total = self.validateRaiseBet(minBet, lastRaise, stake)

                    print("raised by " + str(raisedBet))

                elif choice == "bet":
                    raisedBet, total = self.validateRaiseBet(
                        minBet, lastRaise, stake, False
                    )

                elif choice == "check":
                    played = True

                elif choice == "call":
                    total = self.call(stake)

                elif choice == "all in":
                    total = self.allIn()

                elif choice == "fold":
                    self.fold()
                    played = True

                elif choice == "quit":
                    total = -1
                    self.currentBet = total

                if total:
                    played = True

                    if raisedBet:
                        lastRaise = raisedBet

                    if self.isAllIn:
                        print("You are all in")

            else:
                print("I'm sorry, that choice wasn't on the list!", end="")
                time.sleep(0.4)

        return total, lastRaise

    def __repr__(self):
        return self.name


class Pot:
    def __init__(self, total, players):
        self.total = total
        self.players = players

    def addChipsToPot(self):

        chipsLeft = 0

        lowestBet = min([player.currentPotContrib for player in self.players])

        for player in self.players:
            player.currentPotContrib -= lowestBet
            chipsLeft += player.currentPotContrib
            self.total += lowestBet

        if chipsLeft != 0:
            playersInNextPot = [
                player for player in self.players if player.currentPotContrib > 0
            ]

            return Pot(0, playersInNextPot)

        else:
            return None


# class requires classes CircularLinkedList, StringFormatting, Player, Card and Deck
class Poker:
    HAND_RANKS = {
        1: "Royal Flush",
        2: "Straight Flush",
        3: "Four Of A Kind",
        4: "Full House",
        5: "Flush",
        6: "Straight",
        7: "Three Of A Kind",
        8: "Two Pair",
        9: "Pair",
        10: "High Card",
    }

    def __init__(self, minBet=0, numberOfDecks=2, players=None):
        self.phase = 0
        self.community = []
        self.activePlayers = None
        self.deck = Deck(
            numberOfDecks
        )  # Game deck normally consits of 2 standard Decks
        self.minBet = minBet
        self.pots = Queue()

        # Allows you to skip initiation
        if players:
            self.players = players
        else:
            self.players = []

        self.initiate()

    def addPlayer(self, player):
        self.players.append(player)
        print("Hello " + player.name)

    def removePlayer(self, player):
        self.players.remove(player)
        print(player.name + " is out!")
        try:
            os.remove(os.path.join(PLAYER_DIR, player.name + ".txt"))

        except Exception as e:
            print("couldn't delete player file: ", e)

    # get new is false when the function is used to ensure player numbers are valid
    def getNewPlayers(self, getNew=True):

        if getNew and len(self.players) < 6:
            playerCheck = lambda x: x <= len(self.players)
        else:
            playerCheck = lambda x: x < len(self.players)

        numberOfPlayers = len(self.players)

        while (
            numberOfPlayers < 2 or numberOfPlayers > 6 or playerCheck(numberOfPlayers)
        ):
            try:
                numberOfPlayers = int(
                    input("How many players will be playing in total? ").strip()
                )
                if numberOfPlayers < 2:
                    print("You need at least 2 players to play poker!")
                if numberOfPlayers > 6:
                    print("There are only 6 seats available in Text Poker!")
                if numberOfPlayers < len(self.players):
                    print(
                        "There are "
                        + str(len(self.players))
                        + " players currently, include the current players in the total"
                    )

            except ValueError:
                print("I'm sorry, you didn't enter a number!")

        # if players need to be created
        if len(self.players) != numberOfPlayers:
            playerNames = {player.name for player in self.players}
            for _ in range(len(self.players), numberOfPlayers):
                valid = False
                while not valid:
                    playerName = input("Enter a Player Name: ").strip()
                    if playerName in playerNames:
                        print("I'm sorry, that name is taken!")
                    else:
                        valid = True
                        playerNames.add(playerName)
                        self.addPlayer(Player(playerName))

    def initiate(self):
        StringFormatting.printInFancyBox("Welcome to Text Poker!")

        self.getNewPlayers(False)

        # set min bet and big blind condition is for compile error
        maxBet = min([player.money for player in self.players])
        while self.minBet <= 0 or self.minBet > maxBet:
            try:
                print("Note, the big blind value is also the minimum bet")
                self.minBet = int(
                    input(
                        "How many chips would you like to set the big blind at? "
                    ).strip()
                )
                if self.minBet <= 0:
                    print("The big blind must cost some amount of chips!")
                elif self.minBet > maxBet:
                    print(
                        "Some of the players don't have enough money for that! Try anything below "
                        + str(maxBet)
                        + " chips"
                    )
            except ValueError:
                print("I'm sorry, you didn't enter a number!")

        # clear all previous games files
        if not os.path.isdir(PLAYER_DIR):
            os.mkdir(PLAYER_DIR)
        else:
            try:
                for f in os.listdir(PLAYER_DIR):
                    os.remove(os.path.join(PLAYER_DIR, f))

            except Exception as e:
                print("couldn't delete files because ", e)

    def checkActivePlayers(self):
        i = len(self.players) - 1
        while i >= 0:
            player = self.players[i]
            player.resetRound()
            if not player.money:
                self.removePlayer(player)
            i -= 1

        return len(self.players) > 1

    def deal(self):
        if self.checkActivePlayers():
            self.activePlayers = CircularLinkedList()
            for player in self.players:
                self.activePlayers.insertTail(player)
                self.clearFile(os.path.join(PLAYER_DIR, player.name + ".txt"))
                player.resetRound()
        else:
            return False

        self.deck.shuffle()
        numberOfPlayers = len(self.players)

        totalHoleCards = numberOfPlayers * 2

        cardsInPlay = []
        j = 0

        for i in range(totalHoleCards):
            if j == numberOfPlayers:
                j = 0

            cardsInPlay.append(self.deck.dealCard())
            self.players[j].addCard(cardsInPlay[i])
            self.writeToFile(
                os.path.join(PLAYER_DIR, self.players[j].name + ".txt"),
                str(cardsInPlay[i]),
            )
            j += 1

        self.community = [self.deck.dealCard() for _ in range(5)]

        self.deck.addCards(cardsInPlay)
        self.deck.addCards(self.community)
        self.phase = 1

        return True

    def rotateBlinds(self):
        self.players.append(self.players.pop(0))

    def writeToFile(self, filename, lines):
        lines = lines.splitlines()
        with open(filename, "a") as file:
            for line in lines:
                file.write(line + "\n")

    def clearFile(self, filename):
        open(filename, "w").close()

    # want to limit print statements to play and play turn function to allow code reusability
    def play(self):

        while self.deal():
            turnedCards = self.community[:2]
            button = self.activePlayers.tail
            smallBlind = button.next
            bigBlind = smallBlind.next
            currentPot = Pot(0, self.players)
            self.pots.enqueue(currentPot)

            print("button: " + button.data.name)
            print("big blind: " + bigBlind.data.name)
            print("small blind: " + smallBlind.data.name)

            bigBlind.data.raiseOrBet(self.minBet)
            smallBlind.data.raiseOrBet(self.minBet // 2)

            if bigBlind.data.isAllIn:
                print(bigBlind.data.name + " is all in")

            if smallBlind.data.isAllIn:
                print(smallBlind.data.name + " is all in")

            print("Betting Starting....")
            time.sleep(1)

            for i in range(4):
                if self.activePlayers.length == 1:
                    break

                if self.phase == 1:
                    self.bettingRound(bigBlind.next, self.minBet)
                    nextPot = currentPot.addChipsToPot()

                else:
                    self.bettingRound()
                    nextPot = currentPot.addChipsToPot()

                while nextPot:
                    currentPot = nextPot
                    self.pots.enqueue(currentPot)
                    nextPot = nextPot.addChipsToPot()

                if self.phase < 5:
                    turnedCards.append(self.community[self.phase])
                    communityString = ", ".join([str(card) for card in turnedCards])
                    StringFormatting.printPaddedInBox(communityString, "=")
                    time.sleep(1)

            if self.phase == 5:
                print("Turning over hole cards....")
                time.sleep(1)
                current = self.activePlayers.head
                while True:

                    holeStrings = [str(card) for card in current.data.hole]
                    width = len(max(holeStrings, key=lambda x: len(x)))
                    StringFormatting.padAndCentreLine(current.data.name, width)
                    StringFormatting.borderedText(holeStrings)
                    current = current.next
                    if current == self.activePlayers.head:
                        break

                time.sleep(2)

                activePlayersSet = self.activePlayers.getSet()
                lastPotValue = 0
                playersInPot = []
                potNumber = 0
                potName = None
                HandFound = False

                while not self.pots.isEmpty():
                    currentPot = self.pots.dequeue()
                    playersInPot = [
                        player
                        for player in currentPot.players
                        if player in activePlayersSet
                    ]
                    potName = (
                        "Main Pot" if potNumber == 0 else "Side Pot " + str(potNumber)
                    )

                    if len(playersInPot) == 1:
                        lastPotValue += currentPot.total

                    else:

                        winners = self.findWinner(playersInPot, HandFound)
                        text = (
                            "~"
                            + potName
                            + "~"
                            + "\nWinning Hand: "
                            + Poker.HAND_RANKS[winners[0].handRank]
                        )
                        StringFormatting.printInFancyBox(text, 10)

                        potNumber += 1

                        if not HandFound:
                            HandFound = True

                        if len(winners) == 1:
                            self.printPlayersHand(winners[0])
                            winners[0].money += currentPot.total
                            print(
                                winners[0].name
                                + " wins "
                                + str(currentPot.total)
                                + " chips!"
                            )

                        else:
                            split, extraChipsAwardee, extraChips = self.splitPot(winners, currentPot.total)

                            print(
                                "pot split "
                                + str(len(winners))
                                + " ways for a win of "
                                + str(split)
                                + " chips each"
                            )
                            print("winning hands:")
                            for winner in winners:
                                self.printPlayersHand(winner)

                            if extraChipsAwardee:
                                print(
                                    "\nWith "
                                    + str(extraChips)
                                    + " extra chips awarded to the player to the left of the dealer, "
                                    + str(extraChipsAwardee.name)
                                )
                        time.sleep(2)

                if lastPotValue:
                    StringFormatting.printInFancyBox(
                        "~" + potName + "~" + "\nOne Player Left In Pot"
                    )
                    print(
                        playersInPot[0].name + " wins " + str(lastPotValue) + " chips"
                    )
                    playersInPot[0].money += lastPotValue

            else:
                total = 0
                while not self.pots.isEmpty():
                    currentPot = self.pots.dequeue()
                    total += currentPot.total

                player = self.activePlayers.head.data
                player.money += total
                StringFormatting.printInFancyBox("~Main Pot~", 10)
                print(player.name + " wins " + str(total) + " chips!")

            self.rotateBlinds()
            print("~~~~~~~~~~~~~~~~~~~~")
            print("Round ended")

            if len(self.players) < 6:
                answer = None

                while not (answer == "y" or answer == "n"):
                    answer = (
                        input("would you like to add more players y/n ").lower().strip()
                    )
                    if not (answer == "y" or answer == "n"):
                        print("Invalid input, type y/n")

                if answer == "y":
                    self.getNewPlayers()
                    print("players added...")
                    time.sleep(0.5)
            print("Starting new round...")
            time.sleep(1)

        winner = self.players[0]
        StringFormatting.printInFancyBox(
            winner.name + " wins the game with " + str(winner.money) + " chips!"
        )

    def printPlayersHand(self, player):
        print(player.name + "'s hand > ", end="")
        print(", ".join([str(card) for card in player.hand]), end="")
        if player.kickers:
            print(", " + ", ".join([str(card) for card in player.kickers]))
        else:
            print("\n", end="")

    def splitPot(self, winners, potValue):
        n = len(winners)
        split = potValue // n

        for winner in winners:
            winner.money += split

        # extra chips go to the player next to the button
        if split * n != potValue:
            extraChips = potValue - (split * n)
            nextToButton = self.activePlayers.head
            winnerSet = set(winners)
            while nextToButton not in winnerSet:
                nextToButton = nextToButton.next
            nextToButton.money += extraChips

            return split, nextToButton, extraChips

        else:
            return split, None, None

    def bettingRound(self, nodeToStart=None, stake=0):

        if nodeToStart:
            node = nodeToStart
        else:
            nodeToStart = self.activePlayers.head
            node = nodeToStart

        player = node.data
        startBet = stake
        start = True
        lastRaise = 0

        # While loop conditionals for readability
        notFinishedLoop = lambda currentNode: currentNode != nodeToStart
        betNotChanged = lambda currentStake: currentStake == startBet
        playerNotMetBet = (
            lambda currentPlayer, currentStake: currentPlayer.currentBet != currentStake
        )
        multiplePlayersCanPlay = (
            lambda firstNodeNotAllIn: firstNodeNotAllIn
            != firstNotAllIn(firstNodeNotAllIn.next)
            if firstNodeNotAllIn
            else False
        )

        # find the first not all in player
        firstNotAllIn = lambda startNode: self.activePlayers.search(
            False, start=startNode, key=lambda x: x.isAllIn
        )

        firstNodeCanPlay = firstNotAllIn(nodeToStart)

        while (
            self.activePlayers.length > 1
            and (
                multiplePlayersCanPlay(firstNodeCanPlay)
                or playerNotMetBet(player, stake)
            )
            and (
                start
                or playerNotMetBet(player, stake)
                or (notFinishedLoop(node) and (betNotChanged(stake) or player.isAllIn))
            )
        ):

            if not player.isAllIn:
                bet, lastRaise = player.playTurn(stake, lastRaise, self.minBet)

                if player.currentBet > stake:
                    stake = player.currentBet
                    nodeToStart = node
                    firstNodeCanPlay = firstNotAllIn(nodeToStart)

                elif player.folded or player.currentBet == -1:
                    self.activePlayers.deleteNode(player)
                    if node == nodeToStart:
                        nodeToStart = nodeToStart.next

                    if player.currentBet == -1:
                        print("hi")
                        self.removePlayer(player)

            if start and not (player.folded or player.currentBet == -1):
                start = False

            node = node.next
            player = node.data
            time.sleep(0.5)

        # reset current bets at end of round
        if self.activePlayers.length > 1 and player.currentBet != 0:
            node = self.activePlayers.head
            player = node.data
            while True:
                player.currentBet = 0
                node = node.next
                player = node.data
                print(player)
                if node == self.activePlayers.head:
                    break

        self.phase += 1
        return

    def findWinner(self, playersInHand=None, HandFound=False):
        if not playersInHand:
            playersInHand = self.activePlayers.getList()
        for player in playersInHand:
            if not HandFound:
                player.addToHand(self.community)
                self.mergeSort(player.hand, Card.getValue)
                player.handRank, player.hand, player.kickers = self.getHandRank(
                    player.hand
                )

        self.mergeSort(playersInHand, lambda x: x.handRank)
        winners = [
            player
            for player in playersInHand
            if player.handRank == playersInHand[0].handRank
        ]

        if len(winners) >= 2:
            winners = self.findBiggestHand(
                winners,
                lambda i: lambda x: x.getCardHand(i).value,
                len(winners[0].hand),
            )

            if len(winners) > 1 and winners[0].kickers:
                winners = self.findBiggestHand(
                    winners,
                    lambda i: lambda x: x.getKicker(i).value,
                    len(winners[0].kickers),
                )

        return winners

    def findBiggestHand(self, players, closuredGetFunc, handLength):
        for i in range(handLength):
            getCard = closuredGetFunc(i)
            biggest = max(players, key=getCard)
            biggestCard = getCard(biggest)
            players = [
                player for player in players if getCard(player) == biggestCard
            ]
            if len(players) == 1:
                break
        return players

    def checkStraight(self, values):
        count = 1
        highestIndex = None
        startIndex = 0
        aceLow = False

        # if low ace straight possible
        if values[-1] == 14 and values[0] == 2:
            values = [1] + values
            aceLow = True

        for i in range(1, len(values)):
            if values[i] == values[i - 1] + 1:
                count += 1
                if count >= 5:
                    highestIndex = i

            elif values[i] == values[i - 1]:
                if count >= 5:
                    highestIndex = i
                else:
                    continue

            elif i > 3:
                break

            else:
                count = 1
                startIndex = i

        # because 1 is added to front
        if aceLow and highestIndex:
            startIndex -= 1
            highestIndex -= 1

        return startIndex, highestIndex

    def checkStraightFlush(self, straight):
        # boundary is 3 of a kind of different suits and then a straight flush
        extraSuit = {}
        suit = straight[0].suit
        straightFlush = [straight[0]]

        for i in range(1, len(straight)):
            if straight[i] == straight[i - 1]:
                continue
            elif straight[i].suit == suit:
                straightFlush.append(straight[i])

            elif i > 3:
                break

            elif straight[i].suit in extraSuit:
                suit = straight[i].suit
                straightFlush = [extraSuit[straight[i].suit], straight[i]]
                extraSuit = {}

            elif straight[i].value == straight[i - 1].value:
                extraSuit[straight[i].suit] = straight[i]

            else:
                straightFlush = [straight[i]]
                suit = straight[i].suit

        if len(straightFlush) >= 5:
            return straightFlush
        else:
            return None

    # returns rank, [cardsInHand], [kicker(s)] > first card is highest
    def getHandRank(self, cards):
        values = [card.value for card in cards]
        findKickers = lambda x, amount: [card for card in cards if card not in x][:-amount-1:-1]
        rank = None
        kickers = None
        hand = None
        aceLow = False
        straightStart, straightEnd = self.checkStraight(values)

        # straight
        straight = None
        if straightEnd:
            rank = 6

            # get array of straight cards, reorder if ace low
            if straightStart == -1:
                straightStart = 0
                #if the straight high is 5
                if cards[straightEnd].value == 5:
                    straight = []
                    i = 6
                    while i >= 4 and cards[i].value == 14:  # boundary is 3 Aces and a straight high 5 [2H,3H,4H,5H,AH,AC,AS]
                        cards[i].value = 1
                        acelow = True
                        straight.append(cards[i])
                        i -= 1

                    for i in range(4):
                        straight.append(cards[i])

            if not straight:
                straight = cards[straightStart:straightEnd + 1]

            straightFlush = self.checkStraightFlush(straight)

            if straightFlush:

                # royal flush
                if straightFlush[-1].value == 14:
                    rank = 1

                # straight flush
                else:
                    rank = 2

                return rank, straightFlush[:-6:-1], kickers

        # group cards of same rank, save to dictionary key = amount of same cards, value= array of card group arrays {2: [[2H,2C],[3H,3C]]}

        ofKind = {}

        rankGroups = (list(group) for rank, group in itertools.groupby(cards, Card.getValue))

        for group in rankGroups:
            if len(group) > 1:
                ofKind.setdefault(len(group), []).append(group)

        threeKind = None
        pairs = None

        if ofKind:
            # four of a kind
            if 4 in ofKind:
                hand = ofKind[4][0]
                kicker = [findKickers(hand, 1)[0]]
                rank = 3

                return rank, hand, kicker

            # fullhouse
            elif 3 in ofKind:
                threeKind = ofKind[3][-1]
                if 2 in ofKind:
                    rank = 4
                    hand = threeKind
                    hand.extend(ofKind[2][-1])
                    return rank, hand, kickers

                # three of a kind
                elif not rank:
                    rank = 7

            if not rank and 2 in ofKind:
                # two pair
                pairs = ofKind[2]
                if len(pairs) >= 2:
                    rank = 8
                # pair
                else:
                    rank = 9

        # find cards of same suit
        suitDict = {}

        for card in cards:
            suitDict.setdefault(card.suit, []).append(card)

        flush = [group for group in suitDict.values() if len(group) >= 5]

        if flush:
            hand = flush[0]
            if len(hand) > 5:
                hand = hand[:-6:-1]
            rank = 5

        # straight
        elif rank == 6:
            # to stop the same rank appearing twice in a hand. Could redefine equality but equality is defined as it should be
            hand = [straight[i - 1] for i in range(len(straight), 0, -1) if i == len(straight) or straight[i].value != straight[i - 1].value]
            hand = hand[:5]

        # three of a kind
        elif rank == 7:
            hand = threeKind
            kickers = findKickers(hand, 2)

        # two pair
        elif rank == 8:
            hand = pairs[-1]
            hand.extend(pairs[-2])
            kickers = findKickers(hand, 1)

        # pair
        elif rank == 9:
            hand = pairs[0]
            kickers = findKickers(pairs[0], 3)

        # high card
        elif not rank:
            rank = 10
            hand = [cards[-1]]
            kickers = cards[-2:-6:-1]

        #set ace value back to 14
        if aceLow and rank < 6:
            i = 0
            card = straight[0]
            while card.value == 1:
                card.value = 14
                i+=1
                card = straight[i]

        return rank, hand, kickers

    def mergeSort(self, arr, key=lambda x: x, decending=False):
        if decending:
            comp = lambda x, y: x >= y
        else:
            comp = lambda x, y: x <= y
        i = 0
        j = 0
        k = 0
        n = len(arr)
        if n > 1:
            pivot = n // 2
            left = arr[:pivot]
            right = arr[pivot:]
            self.mergeSort(left, key, decending)
            self.mergeSort(right, key, decending)
            nleft = len(left)
            nright = len(right)
            while i < nleft and j < nright:
                if comp(key(left[i]), key(right[j])):
                    arr[k] = left[i]
                    i += 1
                else:
                    arr[k] = right[j]
                    j += 1
                k += 1

            while i < nleft:
                arr[k] = left[i]
                i += 1
                k += 1
            while j < nright:
                arr[k] = right[j]
                j += 1
                k += 1
            return arr

if __name__ == "__main__":
    game = Poker()
    game.play()
