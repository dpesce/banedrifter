---
title: "Simulating simple gameplay"
date: 2024-04-06
mathjax: true
---

Given a pair of decks, how can we assess which one is better?

More specifically: given two decks that have both been constructed using the same restrictions, and both of which are being fielded within an environment containing only other decks that have built under the same restrictions, which of the two decks is going to achieve a higher win rate across all matchups in that environment?

In most MTG formats, this question is really difficult to answer because the outcome of a matchup depends not only on the contents of the decks but also on the gameplay decisions.  And it's not at all obvious what set of moves would constitute "perfect gameplay" in a matchup between any particular pair of decks.  In fact -- and somewhat incredibly -- it turns out that determining perfect gameplay in MTG is actually an [undecidable problem](https://en.wikipedia.org/wiki/Undecidable_problem) (see [Churchill, Biderman, & Herrick 2019](https://arxiv.org/abs/1904.09828)), at least for some possible deck builds.  But even if we were to assume that we've solved the perfect gameplay problem, and even if one deck can consistently beat another deck using such gameplay, then that still doesn't imply that the first deck will outperform the second (in terms of win rate) within the broader environment.  And this sort of Rock-Paper-Scissors quality means that [greedy algorithms](https://en.wikipedia.org/wiki/Greedy_algorithm) will not necessarily be able to answer the question well, and one would potentially need to resort to a comprehensive exploration of the typically absurdly large number of possible decks that could be built and the even more absurdly large corresponding number of matchups that could be played.  Such a task seems intractable, it's not clear that you could come up with a representative enough subset of the space of matchups (if such a thing even exists) to make any meaningful headway.

However, in our case we've restricted the space of possible decks (and thus the space of possible matchups) so severely that the problem starts to at least feel approachable.  We have already solved the simpler part of the problem, which is to enumerate all possible deck builds and thus all possible pairings of decks.  And the resulting numbers -- ${\sim}10^4$ and ${\sim}10^8$, respectively -- are in the realm of what it seems like we could plausibly explore with accessible amounts of computation.

All that's left to do is to solve the problem of perfect gameplay.

***

### Building a toolbox

Unfortunately, I'm not actually sure how to determine what constitutes perfect gameplay.  So to help things along, I've started by putting together a Python toolkit for simulating interactions between decks that contain only the four cards we're considering.  All of the functionality is contained in the `banedrifter.py` file within the main repository.

#### Cards

The basic unit of a deck is a card.  Within `banedrifter.py`, there is a "card" class that we can initialize using something like the following:

```
> import banedrifter as bd
> ba = bd.card("Baneslayer Angel")
> md = bd.card("Mulldrifter")
> pl = bd.card("Plains")
> il = bd.card("Island")
```

Card objects keep track of some basic information like the card type, the mana cost for playing a card, and whether or not it is currently tapped.  Note that only a small handful of relevant cards are currently recognized by `banedrifter.py`, so if you initialize something like "Black Lotus" then it won't automatically populate most of the card's attributes.

#### Hands

The "hand" class is simply a collection of cards equipped with a couple of convenience functions.  To create a hand, simply pass a list of cards to the initialization function:

```
> h = bd.hand([ba,md,pl,il])
> h
Baneslayer Angel
Mulldrifter
Plains
Island
```

With a hand, you can do some simple things like count the number of cards,

```
> h.count()
7
```

or add some more cards to the hand:

```
> h.add_cards([bd.card("Plains"), bd.card("Island")])
> h
Baneslayer Angel
Mulldrifter
Plains
Island
Plains
Island
```

#### Decks

The "deck" class is similar to the hand class in that it is largely just a collection of cards, but the convenience functions for decks are somewhat different than those for hands.  Mechanically, I think the code would probably be more economical if both hands and decks were subclasses of some more general "card_group" type of object, but I suppose in this case the flavor matters more to me than the code efficiency.

Decks are also where I've really started to heavily restrict what kinds of cards can even be considered by the code.  To initialize a deck, you need to tell it how many of each card ought to be present:

```
> d = bd.deck(N_bane=5, N_mull=5, N_land=5)
> d
Tundra
Mulldrifter
Mulldrifter
Tundra
Baneslayer Angel
Mulldrifter
Baneslayer Angel
Mulldrifter
Baneslayer Angel
Tundra
Tundra
Baneslayer Angel
Mulldrifter
Baneslayer Angel
Tundra
```

You'll notice that at the moment, a deck object only cares about the total number of lands and not on the specific breakdown between Plains and Islands.  I've built it this way because for the first set of simulations I intend to care only about the total mana cost of a card and not about its specific colored cost.  So the modest drawback of Baneslayer Angel's 3WW cost compared to Mulldrifter's 4U will not initially be simulated.  This choice is equivalent to simply filling the deck with [Tundra](https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=286) lands rather than with Plains and Islands, so that's how I've chosen to display it above.

A deck starts out shuffled, but it can also be re-shuffled at any time by calling the `shuffle()` function:

```
> d.shuffle()
> d
Baneslayer Angel
Mulldrifter
Tundra
Mulldrifter
Baneslayer Angel
Mulldrifter
Tundra
Tundra
Tundra
Baneslayer Angel
Tundra
Baneslayer Angel
Baneslayer Angel
Mulldrifter
Mulldrifter
```

You can also draw cards from a deck by calling the `draw(N)` function:

```
> drawn_cards = d.draw(7)
> d
Tundra
Tundra
Baneslayer Angel
Tundra
Baneslayer Angel
Baneslayer Angel
Mulldrifter
Mulldrifter
```

Drawing cards retains the deck ordering but removes the topmost N cards and returns them as an array (note: not as a hand object).  The self-consistent coupling between cards in the deck and cards in the hand is enforced in a separate class.

#### Players

The last class that I've put together -- and by far the most involved one -- is the "player" class.  This class is intended to keep track of a player's board state as it changes during a game of MTG.  To initialize a player, you need to pass a deck to the initialization function:

```
> d = bd.deck(N_bane=12, N_mull=11, N_land=17)
> p = bd.player(d)
> p
****************************************************************************************************
* Life total: 20                                                                                   *
* Cards in hand: 7                                                                                 *
* Cards in deck: 33                                                                                *
* Cards in graveyard: 0                                                                            *
* ------------------------------------------------------------------------------------------------ *
*                                                                                                  *
*                                                                                                  *
*                                                                                                  *
****************************************************************************************************
```

The printed representation of the player object provides a quick view of some commonly-desired information, such as the current life total and the number of cards in hand, in the deck, and in the graveyard.  There is also a bottom field of the printed representation that shows the state of the battlefield, though in the above initialized player that battlefield is empty.

A player starts out with 20 life and initially draws 7 cards from the provided deck and stores them in an internally-generated hand object that we can view:

```
> p.hand
Tundra
Tundra
Mulldrifter
Tundra
Tundra
Baneslayer Angel
Mulldrifter
```

There are then a number of internal functions that control the various actions that a player can take.  For instance, a player may want to draw some number of cards, which can be done by calling the `draw()`` function:

```
> p.draw(2)
> p
****************************************************************************************************
* Life total: 20                                                                                   *
* Cards in hand: 9                                                                                 *
* Cards in deck: 31                                                                                *
* Cards in graveyard: 0                                                                            *
* ------------------------------------------------------------------------------------------------ *
*                                                                                                  *
*                                                                                                  *
*                                                                                                  *
****************************************************************************************************
```

A player can also play a card using the `play()` function:

```
> p.play("Tundra")
> p
****************************************************************************************************
* Life total: 20                                                                                   *
* Cards in hand: 8                                                                                 *
* Cards in deck: 31                                                                                *
* Cards in graveyard: 0                                                                            *
* ------------------------------------------------------------------------------------------------ *
* L                                                                                                *
*                                                                                                  *
*                                                                                                  *
****************************************************************************************************
```

Once a card is played, it shows up on the battlefield.  In this case, we played Tundra, which appears on the battlefield as just an "L" (for "Land") because we're not currently distinguishing between land types.  Since all of the spells in our hand cost 5 mana, if this were a game of MTG we'd have to end the turn here and discard down to 7 cards.  That can be accomplished by calling the `discard()` function:

```
> p.discard("Mulldrifter")
> p
****************************************************************************************************
* Life total: 20                                                                                   *
* Cards in hand: 7                                                                                 *
* Cards in deck: 31                                                                                *
* Cards in graveyard: 1                                                                            *
* ------------------------------------------------------------------------------------------------ *
* L                                                                                                *
*                                                                                                  *
*                                                                                                  *
****************************************************************************************************
```

And at this point, we would be able to pass the turn to the opposing player.

Other actions become relevant later in the game.  Let's just assume we've moved 5 turns ahead and played several more lands along the way:

```
> p.draw(5)
> p.play("Tundra")
> p.play("Tundra")
> p.play("Tundra")
> p.play("Tundra")
> p
****************************************************************************************************
* Life total: 20                                                                                   *
* Cards in hand: 8                                                                                 *
* Cards in deck: 26                                                                                *
* Cards in graveyard: 1                                                                            *
* ------------------------------------------------------------------------------------------------ *
* L L L L L                                                                                        *
*                                                                                                  *
*                                                                                                  *
****************************************************************************************************
```

Now we have enough lands on the field to actually play either Baneslayer Angel or Mulldrifter.  To do either one, we use the `play()` function again:

```
> p.play("Baneslayer Angel")
> p
****************************************************************************************************
* Life total: 20                                                                                   *
* Cards in hand: 7                                                                                 *
* Cards in deck: 26                                                                                *
* Cards in graveyard: 1                                                                            *
* ------------------------------------------------------------------------------------------------ *
* L(T) L(T) L(T) L(T) L(T)                                                                         *
*                                                                                                  *
* B                                                                                                *
****************************************************************************************************
```

Upon playing Baneslayer Angel, a couple of things have changed on the battlefield.  First, all of the lands now have a parenthetical "(T)" next to them, indicating that they are tapped.  Second, a new card -- the played Baneslayer Angel -- has appeared on the battlefield indicated by a "B."

Because it has just entered the battlefield this turn, the Baneslayer Angel currently has summoning sickness and cannot attack until the next turn.  We could manually modify the attributes of the card to bypass this restriction, but it's simpler to use the convenience `start_turn()` function:

```
> p.start_turn()
> p
****************************************************************************************************
* Life total: 20                                                                                   *
* Cards in hand: 8                                                                                 *
* Cards in deck: 25                                                                                *
* Cards in graveyard: 1                                                                            *
* ------------------------------------------------------------------------------------------------ *
* L L L L L                                                                                        *
*                                                                                                  *
* B                                                                                                *
****************************************************************************************************
```

We see that this function has caused the player to draw a card, and it has untapped all of the lands.  It also removed summoning sickness from the Baneslayer Angel, so that we can now attack with it using the `attack()` function:

```
> p.attack("Baneslayer Angel")
> p
****************************************************************************************************
* Life total: 25                                                                                   *
* Cards in hand: 8                                                                                 *
* Cards in deck: 25                                                                                *
* Cards in graveyard: 1                                                                            *
* ------------------------------------------------------------------------------------------------ *
* L L L L L                                                                                        *
*                                                                                                  *
* B(T)                                                                                             *
****************************************************************************************************
```

The act of attacking further modified the board state in two ways.  First, the Baneslayer Angel is now tapped, as it ought to be when attacking.  Second, the player's life total has increased by 5, because it internally understands that the Baneslayer Angel has lifelink and that there are no possible card interactions in this restricted format that will prevent the attacking player from gaining 5 life once a Baneslayer Angel attacks.

Since there are still 5 untapped lands open, the player could also play a Mulldrifter during this turn:

```
> p.play("Mulldrifter")
> p
****************************************************************************************************
* Life total: 25                                                                                   *
* Cards in hand: 9                                                                                 *
* Cards in deck: 23                                                                                *
* Cards in graveyard: 1                                                                            *
* ------------------------------------------------------------------------------------------------ *
* L(T) L(T) L(T) L(T) L(T)                                                                         *
* M                                                                                                *
* B(T)                                                                                             *
****************************************************************************************************
```

Upon playing Mulldrifter, we see that five lands have been tapped, a new card (denoted by "M") has appeared on the battlefield, and the player now has 2 additional cards in hand.  Again, the function understands that there are no possible card interactions in this restricted format that will prevent the player from drawing two cards upon playing Mulldrifter.

Mulldrifter can also be played using its evoke ability by passing the "use_altcost" keyword argument to the `play()` function:

```
> p.start_turn()
> p.play("Mulldrifter", use_altcost=True)
> p
****************************************************************************************************
* Life total: 25                                                                                   *
* Cards in hand: 11                                                                                *
* Cards in deck: 20                                                                                *
* Cards in graveyard: 2                                                                            *
* ------------------------------------------------------------------------------------------------ *
* L(T) L(T) L(T) L L                                                                               *
* M                                                                                                *
* B                                                                                                *
****************************************************************************************************
```

We see that in this case, while 2 cards were still drawn, only 3 lands were tapped for mana (reflecting the lower evoke cost).  Furthermore, the played Mulldrifter is not present on the battlefield but has instead gone directly to the graveyard, because there are no possible card interactions in this restricted format that will prevent it from getting sacrificed upon being evoked.

There are a number of other convenience functions implemented within the player class, but the above examples cover most of the important use cases.  One last piece of information that it is useful to be aware of when using the player class is that it comes with an internal gamelog that gets updated with every action taken.  We can access the gamelog for the above sequence of examples using:

```
> print(p.gamelog)
====================================================================================================
Drawing 2 cards.
Playing Tundra.
Discarding Mulldrifter.
Drawing 5 cards.
Playing Tundra.
Playing Tundra.
Playing Tundra.
Playing Tundra.
Tapping 5 lands.
Playing Baneslayer Angel.
----------------------------------------------------------------------------------------------------
Turn 1

Drawing 1 card.
Attacking with Baneslayer Angel.
Gaining 5 life.
Tapping 5 lands.
Playing Mulldrifter.
Drawing 2 cards.
----------------------------------------------------------------------------------------------------
Turn 2

Drawing 1 card.
Tapping 3 lands.
Evoking Mulldrifter.
Drawing 2 cards.
```

Note that the gamelog has a notion of "turns" and that it only registered two turns throughout all of the above actions.  This is just because we've been calling functions without regard to the actual rules of the game, just to see their effects.  When a game is instead sequenced using calls to the `start_turn()` and `end_turn()` functions, the turn count will increment properly in the gamelog.
