# Copyright 2011 Alex Zvoleff
#
# This file is part of the pyabm agent-based modeling toolkit.
# 
# pyabm is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# pyabm is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# pyabm.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact Alex Zvoleff in the Department of Geography at San Diego State 
# University with any comments or questions. See the README.txt file for 
# contact information.

"""
Contains miscellaneous functions useful in running statistics for agent-based models.
"""

from pyabm import np

class UnitsError(Exception):
    pass

class StatisticsError(Exception):
    pass

def convert_probability_units(probability, prob_time_units):
    """
    Converts probability so units match timestep used in the model, assuming probability 
    function is uniform across the interval.

    Conversions are made accordingly using conditional probability.
    """
    # If the probability time units don't match the model timestep units, then the 
    # probabilities need to be converted.
    if prob_time_units == 'months':
        pass
    elif prob_time_units == 'years':
        for key, value in probability.iteritems():
            probability[key] = 1 - (1 - value)**(1/12.)
    elif prob_time_units == 'decades':
        for key, value in probability.iteritems():
            probability[key] = 1 - (1 - value)**(1/120.)
    else:
        raise UnitsError("unhandled prob_time_units")
    return probability

def get_probability_index(t, prob_time_units):
    """
    Matches units of time in model to those the probability is expressed in. For 
    instance: if probabilities are specified for decades, whereas the model runs in 
    months, ``get_probability_index``, when provided with an age in months, will convert 
    it to decades, rounding down. NOTE: all probabilities must be expressed with the 
    same time units.
    """
    if prob_time_units == 'months':
        return t
    elif prob_time_units == 'years':
        return int(round(t / 12.))
    elif prob_time_units == 'decades':
        return int(round(t / 120.))
    else:
        raise UnitsError("unhandled prob_time_units")

def draw_from_prob_dist(prob_dist):
    """
    Draws a random number from a manually specified probability distribution,
    where the probability distribution is a tuple specified as::

        ([a, b, c, d], [1, 2, 3])

    where a, b, c, and d are bin limits, and 1, 2, and 3 are the probabilities 
    assigned to each bin. Notice one more bin limit must be specified than the 
    number of probabilities given (to close the interval).
    """
    # First randomly choose the bin, with the bins chosen according to their 
    # probability.
    binlims, probs = prob_dist
    num = np.random.rand() * np.sum(probs)
    n = 0
    probcumsums = np.cumsum(probs)
    for problim in probcumsums[0:-1]:
        if num < problim:
            break
        n += 1
    upbinlim = binlims[n+1]
    lowbinlim = binlims[n]
    # Now we know the bin lims, so draw a random number evenly distributed 
    # between those two limits.
    return np.random.uniform(lowbinlim, upbinlim)

def calc_prob_from_prob_dist(prob_dist, attribute):
    """
    Calculated the probability of something based on a manually specified 
    probability distribution, where the probability distribution is a tuple 
    specified as::

        ([a, b, c, d], [1, 2, 3])

    where a, b, c, and d are bin limits, and 1, 2, and 3 are the probabilities 
    assigned to each bin. Notice one more bin limit must be specified than the 
    number of probabilities given (to close the interval). The bin limits are 
    closed on the right, open on the left.

    The correct probability to draw is based on the bin that the 'attribute' 
    parameter falls into. For example, to draw the probability of marrying a 
    spouse based on the difference in age between the spouse and a particular 
    agent, 'attribute' should be the age difference. This function will then 
    return the probability of marrying that spouse based on the bin that the 
    spouse age difference falls into.
    """
    binlims, probs = prob_dist
    n = 0
    for uplim in binlims[1:]:
        if attribute <= uplim:
            break
        n += 1
    # Now we know the bin lims, so draw a random number evenly distributed 
    # between those two limits.
    return probs[n]

def calc_coefficient(coef_tuple):
    """
    Use to handle uncertainty in regression coefficients. ``calc_coefficient`` 
    takes in a tuple of two floats::

        (coef, stderror)

    where coef is the estimated regression coefficient, and stderror is the 
    standard error of the estimated coefficient.
    """
    if len(coef_tuple) != 2:
        raise ValueError("coef_tuple must be of the from (coef, stderror)")
    return coef_tuple[0] + np.random.randn() * coef_tuple[1]
