# -*- coding: utf-8 -*-
""" ResultMultiPlayers.ResultMultiPlayers class to wrap the simulation results, for the multi-players case."""

__author__ = "Lilian Besson"
__version__ = "0.1"

import numpy as np


class ResultMultiPlayers:
    """ ResultMultiPlayers accumulators, for the multi-players case.
    """

    def __init__(self, nbArms, horizon, nbPlayers):
        self.choices = np.zeros((nbPlayers, horizon))
        self.rewards = np.zeros((nbPlayers, horizon))
        self.pulls = np.zeros((nbPlayers, nbArms))
        self.collisions = np.zeros((nbArms, horizon))

    def store(self, time, choices, rewards, pulls, collisions):
        self.choices[:, time] = choices
        self.rewards[:, time] = rewards
        self.pulls += pulls
        # FIXME it chould simply be computed as a difference between choices and pulls at the end right ?
        self.collisions[:, time] += collisions