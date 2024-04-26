###################################################
# imports

import banedrifter as bd
import numpy as np

###################################################
# card-playing rulesets

def cardplay_01(p1,p2):

    # start by playing a land
    if bd.bl in p1.hand.cardnames():
        p1.play(bd.bl)

    # then try to play cards regularly
    while p1.count_untapped_lands() >= 5:

        # play a Baneslayer Angel if possible
        if (bd.ba in p1.hand.cardnames()):
            p1.play(bd.ba)

        # if not, play a Mulldrifter
        elif ((bd.md in p1.hand.cardnames()) & (p1.decksize() >= 2)):
            p1.play(bd.md)

        else:
            break

    # otherwise, try to evoke a Mulldrifter
    while p1.count_untapped_lands() >= 3:

        # evoke a Mulldrifter
        if ((bd.md in p1.hand.cardnames()) & (p1.decksize() >= 2)):
            p1.play(bd.md,use_altcost=True)

        else:
            break

###################################################
# combat rulesets

def combat_01(p1,p2):

    # if you can, attack with all Baneslayers
    N_attacking = 0
    attacking_banes = list()
    attacking_ind = list()
    for ibane, bane in enumerate(p1.banes):
        if (not bane.tapped) & (not bane.sick):
            p1.attack(bd.ba)
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
            p1.gamelog += str(N_attacking) + ' ' + bd.ba + 's die attacking.' + '\n'
            p2.banes = np.delete(p2.banes,blocking_ind)
            p2.grave = np.concatenate((p2.grave,blocking_banes))
            p2.gamelog += str(N_blocking) + ' ' + bd.ba + 's die blocking.' + '\n'

        # if there are more attackers than blockers
        if (N_attacking > N_blocking):

            # blocking player gains 5 life for each blocker
            p2.gain_life(N_blocking*5)

            # blocking player loses 5 life for each extra attacker
            p2.lose_life((N_attacking-N_blocking)*5)

            # all blocking creatures die
            p2.banes = np.delete(p2.banes,blocking_ind)
            p2.grave = np.concatenate((p2.grave,blocking_banes))
            if (N_blocking > 0):
                p2.gamelog += str(N_blocking) + ' ' + bd.ba + 's die blocking.' + '\n'

            # a number of attacking creatures equal to the number of blockers dies
            p1.banes = np.delete(p1.banes,attacking_ind[:N_blocking])
            p1.grave = np.concatenate((p1.grave,attacking_banes[:N_blocking]))
            if (N_blocking > 0):
                p1.gamelog += str(N_blocking) + ' ' + bd.ba + 's die attacking.' + '\n'

        # if there are more blockers than attackers
        if (N_attacking < N_blocking):

            # blocking player gains 5 life for each attacker
            p2.gain_life(N_attacking*5)

            # all attacking creatures die
            p1.banes = np.delete(p1.banes,attacking_ind)
            p1.grave = np.concatenate((p1.grave,attacking_banes))
            p1.gamelog += str(N_attacking) + ' ' + bd.ba + 's die attacking.' + '\n'

            # a number of blocking creatures equal to the number of attackers dies
            p2.banes = np.delete(p2.banes,blocking_ind[:N_attacking])
            p2.grave = np.concatenate((p2.grave,blocking_banes[:N_attacking]))
            p2.gamelog += str(N_attacking) + ' ' + bd.ba + 's die blocking.' + '\n'

###################################################
# discard rulesets

def discard_01(p1,p2):

    while p1.handsize() > 7:

        N_banes = (p1.hand.cardnames() == bd.ba).sum()
        N_mulls = (p1.hand.cardnames() == bd.md).sum()
        N_lands = (p1.hand.cardnames() == bd.bl).sum()

        if ((N_banes > N_mulls) & (N_banes > N_lands)):
            p1.discard(bd.ba)
        elif ((N_mulls > N_banes) & (N_mulls > N_lands)):
            p1.discard(bd.md)
        elif ((N_lands >= N_banes) & (N_lands >= N_mulls)):
            p1.discard(bd.bl)
        elif ((N_banes == N_mulls) & (N_banes >= N_lands)):
            p1.discard(bd.md)
        elif ((N_banes == N_mulls) & (N_banes < N_lands)):
            p1.discard(bd.bl)
        elif ((N_banes >= N_mulls) & (N_banes == N_lands)):
            p1.discard(bd.bl)
        elif ((N_banes < N_mulls) & (N_banes == N_lands)):
            p1.discard(bd.md)
        elif ((N_mulls >= N_banes) & (N_mulls == N_lands)):
            p1.discard(bd.bl)
        elif ((N_mulls < N_banes) & (N_mulls == N_lands)):
            p1.discard(bd.ba)

        else:
            raise Exception("This case isn't captured!")
            