##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
#
# Python3 porting of qtractor fade functions,
# based on Robert Penner's easing equations.
##########################################

'''
    Functor arguments normalization.

    t = (x - x0) / (x1 - x0)   where 'x' is the time  (x0 initial, x1 final)
    a = y1 - y0                where 'y' is the value (y0 initial, y1 final)
    b = y0
'''


def fade_linear(t, a, b):
    ''' Linear fade. '''
    return a * t + b


def fadein_quad(t, a, b):
    ''' Quadratic (t^2) fade in: accelerating from zero velocity. '''
    return a * (t ** 2) + b


def fadeout_quad(t, a, b):
    ''' Quadratic (t^2) fade out: decelerating to zero velocity. '''
    return a * (t * (2 - t)) + b


def fade_inout_quad(t, a, b):
    '''
        Quadratic (t^2) fade in-out: acceleration until halfway,
        then deceleration.
    '''
    t *= 2
    if t < 1.0:
        return 0.5 * a * (t ** 2) + b
    else:
        t -= 1
        return 0.5 * a * (1 - (t * (t - 2))) + b


def ntime(time, begin, duration):
    ''' Return normalized time '''
    return (time - begin) / (duration - begin)
