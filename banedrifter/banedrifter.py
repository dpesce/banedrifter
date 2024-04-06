###################################################
# imports

import numpy as np
rng = np.random.default_rng()

###################################################
# useful constants

ba = "Baneslayer Angel"
md = "Mulldrifter"
bl = "Tundra"

creature = "Creature"
land = "Land"

white = "White"
blue = "Blue"
black = "Black"
red = "Red"
green = "Green"

###################################################
# card class

class card:
    """
    An individual card
    """

    def __init__(self,name):

        self.name = name

        self.tapped = False
        self.sick = True

        self.type = None
        self.cmc = None
        self.mc = None
        self.color = None
        self.altcost = None

        if (name == ba):
            self.type = creature
            self.cmc = 5
            self.mc = '3WW'
            self.color = white
            self.altcost = 0

        if (name == md):
            self.type = creature
            self.cmc = 5
            self.mc = '4U'
            self.color = blue
            self.altcost = 3

        if (name == "Plains"):
            self.type = land
            self.cmc = 0
            self.mc = '0'
            self.color = None
            self.altcost = 0

        if (name == "Island"):
            self.type = land
            self.cmc = 0
            self.mc = '0'
            self.color = None
            self.altcost = 0

        if (name == "Tundra"):
            self.type = land
            self.cmc = 0
            self.mc = '0'
            self.color = None
            self.altcost = 0

    # show the card name when printed
    def __repr__(self):
        return self.name

###################################################
# deck class

class deck:
    """
    The cards in the deck
    """

    def __init__(self,N_bane,N_mull,N_land):

        # add the appropriate cards to the deck
        self.cards = list()
        for i in range(N_bane):
            self.cards.append(card(ba))
        for i in range(N_mull):
            self.cards.append(card(md))
        for i in range(N_land):
            self.cards.append(card(bl))
        self.cards = np.array(self.cards)

        # start with the deck randomly shuffled
        self.shuffle()

    # show the list of cards when printed
    def __repr__(self):
        return '\n'.join(self.cardnames())

    # count the cards
    def count(self):
        return len(self.cards)

    # list of card names
    def cardnames(self):
        return np.array([c.name for c in self.cards])

    # shuffle the deck
    def shuffle(self):
        ind = rng.permutation(self.count())
        self.cards = self.cards[ind]

    # draw some cards
    def draw(self,N=1):
        if (N < 0):
            raise Exception("I don't know how to draw a negative number of cards.")
        if (N > 0) & (self.count() == 0):
            print("No more cards left to draw!")
        else:
            cards_to_be_drawn = self.cards[:N]
            self.cards = self.cards[N:]

        return cards_to_be_drawn

###################################################
# hand class

class hand:
    """
    The cards in hand
    """

    def __init__(self,cards):
        
        self.cards = cards

    # show the list of cards when printed
    def __repr__(self):
        return '\n'.join(self.cardnames())

    # count the cards
    def count(self):
        return len(self.cards)

    # list of card names
    def cardnames(self):
        return np.array([c.name for c in self.cards])

    # add some cards to hand
    def add_cards(self,cards):
        self.cards = np.concatenate((self.cards,cards))

###################################################
# player class

class player:
    """
    A player and associated board state
    """

    def __init__(self,starting_deck,handsize=7,linelength=100):

        self.deck = starting_deck

        # start with a hand of cards randomly drawn from the deck
        self.hand = hand(self.deck.draw(handsize))

        # start out not being dead
        self.alive = True
        self.loss_reason = None
        self.life = 20

        # start out with nothing on the field
        self.banes = self.deck.draw(0)
        self.mulls = self.deck.draw(0)
        self.lands = self.deck.draw(0)

        # start out with nothing in the graveyard
        self.grave = self.deck.draw(0)

        # initialize a game log
        self.linelength = linelength
        self.turncount = 0
        self.gamelog = '='*self.linelength + '\n'

    # show the board state when printed
    def __repr__(self):
        return self.boardstate()

    def boardstate(self):
        strout = '*'*self.linelength + '\n'
        strout += ('* Life total: ' + str(self.life)).ljust(self.linelength-1) + '*' + '\n'
        strout += ('* Cards in hand: ' + str(self.handsize())).ljust(self.linelength-1) + '*' + '\n'
        strout += ('* Cards in deck: ' + str(self.decksize())).ljust(self.linelength-1) + '*' + '\n'
        strout += ('* Cards in graveyard: ' + str(self.gravesize())).ljust(self.linelength-1) + '*' + '\n'
        strout += '* ' + '-'*(self.linelength-4) + ' *' + '\n'

        strcard = '* '
        for land in self.lands:
            if land.tapped:
                strcard += 'L(T) '
            else:
                strcard += 'L '
        strcard = strcard.ljust(self.linelength-1) + '*' + '\n'
        strout += strcard

        strcard = '* '
        for mull in self.mulls:
            if mull.tapped:
                strcard += 'M(T) '
            else:
                strcard += 'M '
        strcard = strcard.ljust(self.linelength-1) + '*' + '\n'
        strout += strcard

        strcard = '* '
        for bane in self.banes:
            if bane.tapped:
                strcard += 'B(T) '
            else:
                strcard += 'B '
        strcard = strcard.ljust(self.linelength-1) + '*' + '\n'
        strout += strcard

        strout += '*'*self.linelength + '\n'
        return strout

    def handstate(self):
        strout = '*'*self.linelength + '\n'
        strout += ('* Hand:').ljust(self.linelength-1) + '*' + '\n'
        for cardname in self.hand.cardnames():
            strout += ('*       '+cardname).ljust(self.linelength-1) + '*' + '\n'
        return strout

    # log the current board state
    def log_boardstate(self):
        self.gamelog += '\n'
        self.gamelog += self.handstate()
        self.gamelog += self.boardstate()
        self.gamelog += '\n'

    # how many cards in hand
    def handsize(self):
        return self.hand.count()

    # how many cards in deck
    def decksize(self):
        return self.deck.count()

    # how many cards in graveyard
    def gravesize(self):
        return len(self.grave)

    # lose life
    def lose_life(self,N):
        self.life -= N
        self.gamelog += 'Losing ' + str(N) + ' life.' + '\n'
        if self.life <= 0:
            self.alive = False
            self.gamelog += 'PLAYER LOSES VIA LIFE TOTAL' +'\n'
            self.loss_reason = 'life'

    # gain life
    def gain_life(self,N):
        self.life += N
        self.gamelog += 'Gaining ' + str(N) + ' life.' + '\n'

    # draw some cards
    def draw(self,N=1):
        if N > self.deck.count():
            self.alive = False
            self.gamelog += 'PLAYER LOSES VIA MILLING' +'\n'
            self.loss_reason = 'mill'
            return 0
        cards_drawn = self.deck.draw(N)
        self.hand.add_cards(cards_drawn)

        # log it
        if N == 1:
            self.gamelog += 'Drawing 1 card.' + '\n'
        else:
            self.gamelog += 'Drawing ' + str(N) + ' cards.' + '\n'

    # discard a card
    def discard(self,cardname):

        # check that we know this card at all
        if cardname not in [ba,md,bl]:
            raise Exception("Card not recognized!")

        # check that you have the card in your hand
        indarr = (self.hand.cardnames() == cardname)
        if indarr.sum() == 0:
            raise Exception("You can't discard a card that you aren't holding!")
        ind = np.where(indarr)[0][0]

        # remove the card from hand
        card_to_discard = self.hand.cards[ind]
        self.hand = hand(np.delete(self.hand.cards,ind))

        # add the card to the graveyard
        self.grave = np.concatenate((self.grave,[card_to_discard]))

        # log it
        self.gamelog += 'Discarding ' + cardname + '.' + '\n'

    # count how many untapped lands you have
    def count_untapped_lands(self):
        i = 0
        for landcard in self.lands:
            if not landcard.tapped:
                i += 1
        return i

    # play a card
    def play(self,cardname,use_altcost=False):
        
        # check that we know this card at all
        if cardname not in [ba,md,bl]:
            raise Exception("Card not recognized!")

        # check that you have the card in your hand
        indarr = (self.hand.cardnames() == cardname)
        if indarr.sum() == 0:
            raise Exception("You can't play a card that you aren't holding!")
        ind = np.where(indarr)[0][0]

        # check that you have enough mana to play this card
        if not use_altcost:
            cost = self.hand.cards[ind].cmc
        else:
            cost = self.hand.cards[ind].altcost
        if self.count_untapped_lands() < cost:
            raise Exception("You do not have enough mana to play this card!")

        # otherwise, tap the necessary amount of mana
        manacount = 0
        if cost > 0:
            for landcard in self.lands:
                if not landcard.tapped:
                    landcard.tapped = True
                    manacount += 1
                if manacount == cost:
                    break
        if manacount > 0:
            self.gamelog += 'Tapping ' + str(manacount) + ' lands.' + '\n'

        # remove the card from hand
        card_to_play = self.hand.cards[ind]
        self.hand = hand(np.delete(self.hand.cards,ind))

        # place the card on the field or into the graveyard, as appropriate
        if cardname == ba:
            self.banes = np.concatenate((self.banes,[card_to_play]))
            self.gamelog += 'Playing ' + ba + '.' + '\n'
        if cardname == md:
            if not use_altcost:
                self.mulls = np.concatenate((self.mulls,[card_to_play]))
                self.gamelog += 'Playing ' + md + '.' + '\n'
            else:
                self.grave = np.concatenate((self.grave,[card_to_play]))
                self.gamelog += 'Evoking ' + md + '.' + '\n'
        if cardname == bl:
            self.lands = np.concatenate((self.lands,[card_to_play]))
            self.gamelog += 'Playing ' + bl + '.' + '\n'

        # additional effects
        if cardname == md:
            self.draw(2)

    # attack with a creature
    def attack(self,cardname):

        # check that we know this card at all
        if cardname not in [ba,md,bl]:
            raise Exception("Card not recognized!")

        # make sure we're not attacking with a land
        if cardname == bl:
            raise Exception("Lands can't attack!")

        # check that you have the card on the field
        condition = ((cardname == ba) & (len(self.banes) < 1))
        condition |= ((cardname == md) & (len(self.mulls) < 1))
        if condition:
            raise Exception("You can't attack with a creature that's not on the field!")

        # check that the creature isn't tapped and doesn't have summoning sickness
        avail = False
        if cardname == ba:
            for bane in self.banes:
                if ((not bane.sick) & (not bane.tapped)):
                    avail = True
        if cardname == md:
            for mull in self.mulls:
                if ((not mull.sick) & (not mull.tapped)):
                    avail = True
        if not avail:
            raise Exception("You have no "+cardname+"s able to attack!")

        # otherwise, attack with it
        if cardname == ba:
            for bane in self.banes:
                if ((not bane.sick) & (not bane.tapped)):
                    bane.tapped = True
                    self.gamelog += 'Attacking with '+ ba + '.' + '\n'
                    break
        if cardname == md:
            for mull in self.mulls:
                if ((not mull.sick) & (not mull.tapped)):
                    mull.tapped = True
                    attackcount += 1
                    self.gamelog += 'Attacking with '+ md + '.' + '\n'
                    break

        # additional effects
        if cardname == ba:
            self.gain_life(5)

    # the first turn for the first player is slightly different
    def first_turn(self):
        if self.turncount != 0:
            raise Warning("Just noting that it's a bit odd to call this first turn function when it's not the first turn.")
        self.turncount += 1
        self.gamelog += '-'*self.linelength + '\n'
        self.gamelog += 'Turn ' + str(self.turncount) + '\n' + '\n'

    # reset things at the beginning of the turn
    def start_turn(self):

        # log the start of the turn
        self.turncount += 1
        self.gamelog += '-'*self.linelength + '\n'
        self.gamelog += 'Turn ' + str(self.turncount) + '\n' + '\n'

        # untap everything and remove summoning sickness
        for land in self.lands:
            land.tapped = False
            land.sick = False
        for bane in self.banes:
            bane.tapped = False
            bane.sick = False
        for mull in self.mulls:
            mull.tapped = False
            mull.sick = False
                
        # draw a card
        self.draw(1)

    # do end-of-turn stuff
    def end_turn(self):

        while self.handsize() > 7:

            N_banes = (self.hand.cardnames() == ba).sum()
            N_mulls = (self.hand.cardnames() == md).sum()
            N_lands = (self.hand.cardnames() == bl).sum()

            if ((N_banes > N_mulls) & (N_banes > N_lands)):
                self.discard(ba)
            elif ((N_mulls > N_banes) & (N_mulls > N_lands)):
                self.discard(md)
            elif ((N_lands >= N_banes) & (N_lands >= N_mulls)):
                self.discard(bl)
            elif ((N_banes == N_mulls) & (N_banes >= N_lands)):
                self.discard(md)
            elif ((N_banes == N_mulls) & (N_banes < N_lands)):
                self.discard(bl)
            elif ((N_banes >= N_mulls) & (N_banes == N_lands)):
                self.discard(bl)
            elif ((N_banes < N_mulls) & (N_banes == N_lands)):
                self.discard(md)
            elif ((N_mulls >= N_banes) & (N_mulls == N_lands)):
                self.discard(bl)
            elif ((N_mulls < N_banes) & (N_mulls == N_lands)):
                self.discard(ba)

            else:
                raise Exception("This case isn't captured!")

###################################################
# gameplay function

def play_game(p1,p2,verbose=False):
    """
    Play out a game.
    """

    # first turn for player 1
    p1.first_turn()
    if bl in p1.hand.cardnames():
        p1.play(bl)
    p1.log_boardstate()

    # first turn for player 2
    p2.start_turn()
    if bl in p2.hand.cardnames():
        p2.play(bl)
    p2.log_boardstate()

    # subsequent turns
    while (p1.alive & p2.alive):

        ######################################
        # first player's turn

        p1.start_turn()

        # alive check
        if not p1.alive:
            break

        # play a land if possible
        if bl in p1.hand.cardnames():
            p1.play(bl)

        # alive check
        if not p1.alive:
            break

        while p1.count_untapped_lands() >= 5:

            # play a Baneslayer Angel if possible
            if (ba in p1.hand.cardnames()):
                p1.play(ba)

            # # if not, play a Mulldrifter
            # elif (md in p1.hand.cardnames()):
            #     # if ((p1.handsize() <= 5) & (p1.decksize() >= 2)):
            #     if (p1.decksize() >= 2):
            #         p1.play(md)
            #     else:
            #         break

            # if not, play a Mulldrifter
            elif ((md in p1.hand.cardnames()) & (p1.decksize() >= 2)):
                p1.play(md)

            else:
                break

            # alive check
            if not p1.alive:
                break

        # alive check
        if not p1.alive:
            break

        # if you can, attack with all Baneslayers
        N_attacking = 0
        attacking_banes = list()
        attacking_ind = list()
        for ibane, bane in enumerate(p1.banes):
            if (not bane.tapped) & (not bane.sick):
                p1.attack(ba)
                N_attacking += 1
                attacking_banes.append(bane)
                attacking_ind.append(ibane)

        # the opposing player will try to block as many as possible
        N_blocking = 0
        blocking_banes = list()
        blocking_ind = list()
        for ibane, bane in enumerate(p2.banes):
            if (not bane.tapped):
                N_blocking += 1
                blocking_banes.append(bane)
                blocking_ind.append(ibane)

        if N_attacking > 0:

            # if there are an equal number of attackers as blockers
            if (N_attacking == N_blocking):

                # blocking player gains 5 life for each blocker
                p2.gain_life(N_blocking*5)

                # all attacking and blocking creatures die
                p1.banes = np.delete(p1.banes,attacking_ind)
                p1.grave = np.concatenate((p1.grave,attacking_banes))
                p1.gamelog += str(N_attacking) + ' ' + ba + 's die attacking.'
                p2.banes = np.delete(p2.banes,blocking_ind)
                p2.grave = np.concatenate((p2.grave,blocking_banes))
                p2.gamelog += str(N_blocking) + ' ' + ba + 's die blocking.'

            # if there are more attackers than blockers
            if (N_attacking > N_blocking):

                # blocking player gains 5 life for each blocker
                p2.gain_life(N_blocking*5)

                # blocking player loses 5 life for each extra attacker
                p2.lose_life((N_attacking-N_blocking)*5)

                # all blocking creatures die
                p2.banes = np.delete(p2.banes,blocking_ind)
                p2.grave = np.concatenate((p2.grave,blocking_banes))
                p2.gamelog += str(N_blocking) + ' ' + ba + 's die blocking.'

                # a number of attacking creatures equal to the number of blockers dies
                p1.banes = np.delete(p1.banes,attacking_ind[:N_blocking])
                p1.grave = np.concatenate((p1.grave,attacking_banes[:N_blocking]))
                p1.gamelog += str(N_blocking) + ' ' + ba + 's die attacking.'

            # if there are more blockers than attackers
            if (N_attacking < N_blocking):

                # blocking player gains 5 life for each attacker
                p2.gain_life(N_attacking*5)

                # all attacking creatures die
                p1.banes = np.delete(p1.banes,attacking_ind)
                p1.grave = np.concatenate((p1.grave,attacking_banes))
                p1.gamelog += str(N_attacking) + ' ' + ba + 's die attacking.'

                # a number of blocking creatures equal to the number of attackers dies
                p2.banes = np.delete(p2.banes,blocking_ind[:N_attacking])
                p2.grave = np.concatenate((p2.grave,blocking_banes[:N_attacking]))
                p2.gamelog += str(N_attacking) + ' ' + ba + 's die blocking.'

        # alive check
        if not p1.alive:
            break

        p1.end_turn()
        p1.log_boardstate()

        ######################################
        # second player's turn

        p2.start_turn()

        # alive check
        if not p2.alive:
            break

        # play a land if possible
        if bl in p2.hand.cardnames():
            p2.play(bl)

        # alive check
        if not p2.alive:
            break

        while p2.count_untapped_lands() >= 5:

            # play a Baneslayer Angel if possible
            if (ba in p2.hand.cardnames()):
                p2.play(ba)

            # # if not, play a Mulldrifter
            # elif (md in p2.hand.cardnames()):
            #     # if ((p2.handsize() <= 5) & (p2.decksize() >= 2)):
            #     if (p2.decksize() >= 2):
            #         p2.play(md)
            #     else:
            #         break

            # if not, play a Mulldrifter
            elif ((md in p2.hand.cardnames()) & (p2.decksize() >= 2)):
                p2.play(md)

            else:
                break

            # alive check
            if not p2.alive:
                break

        # alive check
        if not p2.alive:
            break

        # if you can, attack with all Baneslayers
        N_attacking = 0
        attacking_banes = list()
        attacking_ind = list()
        for ibane, bane in enumerate(p2.banes):
            if (not bane.tapped) & (not bane.sick):
                p2.attack(ba)
                N_attacking += 1
                attacking_banes.append(bane)
                attacking_ind.append(ibane)

        # the opposing player will try to block as many as possible
        N_blocking = 0
        blocking_banes = list()
        blocking_ind = list()
        for ibane, bane in enumerate(p1.banes):
            if (not bane.tapped):
                N_blocking += 1
                blocking_banes.append(bane)
                blocking_ind.append(ibane)

        if N_attacking > 0:

            # if there are an equal number of attackers as blockers
            if (N_attacking == N_blocking):

                # blocking player gains 5 life for each blocker
                p1.gain_life(N_blocking*5)

                # all attacking and blocking creatures die
                p2.banes = np.delete(p2.banes,attacking_ind)
                p2.grave = np.concatenate((p2.grave,attacking_banes))
                p2.gamelog += str(N_attacking) + ' ' + ba + 's die attacking.'
                p1.banes = np.delete(p1.banes,blocking_ind)
                p1.grave = np.concatenate((p1.grave,blocking_banes))
                p1.gamelog += str(N_blocking) + ' ' + ba + 's die blocking.'

            # if there are more attackers than blockers
            if (N_attacking > N_blocking):

                # blocking player gains 5 life for each blocker
                p1.gain_life(N_blocking*5)

                # blocking player loses 5 life for each extra attacker
                p1.lose_life((N_attacking-N_blocking)*5)

                # all blocking creatures die
                p1.banes = np.delete(p1.banes,blocking_ind)
                p1.grave = np.concatenate((p1.grave,blocking_banes))
                p1.gamelog += str(N_blocking) + ' ' + ba + 's die blocking.'

                # a number of attacking creatures equal to the number of blockers dies
                p2.banes = np.delete(p2.banes,attacking_ind[:N_blocking])
                p2.grave = np.concatenate((p2.grave,attacking_banes[:N_blocking]))
                p2.gamelog += str(N_blocking) + ' ' + ba + 's die attacking.'

            # if there are more blockers than attackers
            if (N_attacking < N_blocking):

                # blocking player gains 5 life for each attacker
                p1.gain_life(N_attacking*5)

                # all attacking creatures die
                p2.banes = np.delete(p2.banes,attacking_ind)
                p2.grave = np.concatenate((p2.grave,attacking_banes))
                p2.gamelog += str(N_attacking) + ' ' + ba + 's die attacking.'

                # a number of blocking creatures equal to the number of attackers dies
                p1.banes = np.delete(p1.banes,blocking_ind[:N_attacking])
                p1.grave = np.concatenate((p1.grave,blocking_banes[:N_attacking]))
                p1.gamelog += str(N_attacking) + ' ' + ba + 's die blocking.'

        # alive check
        if not p2.alive:
            break

        p2.end_turn()
        p2.log_boardstate()

    if p1.alive & (not p2.alive):
        if verbose:
            print("Player 1 wins!")
        winner = 1
        loss_reason = p2.loss_reason
    if p2.alive & (not p1.alive):
        if verbose:
            print("Player 2 wins!")
        winner = 2
        loss_reason = p1.loss_reason
    if (p1.alive & p2.alive) | ((not p1.alive) & (not p2.alive)):
        if verbose:
            print("The game is a ... draw?")
        winner = 0
        loss_reason = None

    return p1, p2, winner, loss_reason

