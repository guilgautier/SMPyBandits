# -*- coding: utf-8 -*-
""" OracleNotFair: a multi-player policy with full knowledge and centralized intelligence to affect users to a FIXED arm, among the best arms.

- It allows to have absolutely *no* collision, if there is more channels than users (always assumed).
- But it is NOT fair on ONE run: the best arm is played only by one player.
- Note that in average, it is fair (who plays the best arm is randomly decided).
- Note that it IS affecting players on the best arms: it requires full knowledge of the means of the arms, not simply the number of arms.

- Note that they need a perfect knowledge on the arms, even this is not physically plausible.
"""
from __future__ import print_function

__author__ = "Lilian Besson"
__version__ = "0.1"

import numpy as np

from .ChildPointer import ChildPointer


class Fixed(object):
    """ Fixed: always select a fixed arm, as decided by the OracleNotFair multi-player policy.
    """

    def __init__(self, nbArms, armIndex):
        self.nbArms = nbArms
        self.armIndex = armIndex
        self.params = str(armIndex)

    def __str__(self):
        return "Fixed({})".format(self.params)

    def startGame(self):
        pass

    def getReward(self, arm, reward):
        pass

    def choice(self):
        return self.armIndex


class OracleNotFair(object):
    """ OracleNotFair: a multi-player policy which uses a centralized intelligence to affect users to affect users to a FIXED arm, among the best arms.
    """

    def __init__(self, nbPlayers, armsMAB):
        """
        - nbPlayers: number of players to create (in self._players).
        - armsMAB: MAB object that represents the arms.

        Examples:
        >>> s = OracleNotFair(10, MAB({'arm_type': Bernoulli, 'params': [0.1, 0.5, 0.9]}))

        - To get a list of usable players, use s.childs.
        - Warning: s._players is for internal use
        """
        assert nbPlayers > 0, "Error, the parameter 'nbPlayers' for OracleNotFair class has to be > 0."
        nbArms = armsMAB.nbArms
        if nbPlayers > nbArms:
            print("Warning, there is more users than arms ... (nbPlayers > nbArms)")  # XXX
        # Attributes
        self.nbPlayers = nbPlayers
        self.nbArms = nbArms
        # Internal vectorial memory
        means = np.array([arm.mean() for arm in armsMAB.arms])
        if nbPlayers <= nbArms:
            self._affectations = np.argsort(means)[-nbPlayers:]
        else:
            self._affectations = np.zeros(nbPlayers, dtype=int)
            self._affectations[:nbArms] = np.random.choice(nbArms, size=nbArms, replace=False)  # XXX a permutation
            # Try to minimize the number of doubled affectations, so all the other players are affected to the *same* arm
            worseArm = np.argmin(means)
            self._affectations[nbArms:] = worseArm
            # XXX this "trash" arm with max number of collision will not change, but it's the worse arm, so we are optimal!
        # Shuffle it once, just to be fair in average
        np.random.shuffle(self._affectations)
        print("OracleNotFair: initialized with {} arms and {} players ...".format(nbArms, nbPlayers))  # DEBUG
        print("It decided to use this affectation of arms :")  # DEBUG
        # Internal object memory
        self._players = [None] * nbPlayers
        self.childs = [None] * nbPlayers
        for playerId in range(nbPlayers):
            print(" - Player number {} will always choose the arm number {} ...".format(playerId + 1, self._affectations[playerId]))  # DEBUG
            self._players[playerId] = Fixed(nbArms, self._affectations[playerId])
            self.childs[playerId] = ChildPointer(self, playerId)
        self._printNbCollisions()  # DEBUG
        self.params = '{} x {}'.format(nbPlayers, str(self._players[0]))

    def __str__(self):
        return "OracleNotFair({})".format(self.params)

    def _printNbCollisions(self):
        """ Print number of collisions. """
        nbPlayersAlone = len(set(self._affectations))
        if nbPlayersAlone != self.nbPlayers:
            print("\n==> This affectation will bring collisions! Exactly {} at each step...".format(self.nbPlayers - nbPlayersAlone))
            for armId in range(self.nbArms):
                nbAffected = np.count_nonzero(self._affectations == armId)
                if nbAffected > 1:
                    print(" - For arm number {}, there is {} different child player affected on this arm ...".format(armId + 1, nbAffected))

    def startGame(self):
        for player in self._players:
            player.startGame()

    def getReward(self, arm, reward):
        for player in self._players:
            player.getReward(arm, reward)()

    def choice(self):
        choices = np.zeros(self.nbPlayers)
        for i, player in enumerate(self._players):
            choices[i] = player.choice()
        return choices  # XXX What to do with this ?

    def _startGame_one(self, playerId):
        return self._players[playerId].startGame()

    def _getReward_one(self, playerId, arm, reward):
        return self._players[playerId].getReward(arm, reward)

    def _choice_one(self, playerId):
        return self._players[playerId].choice()