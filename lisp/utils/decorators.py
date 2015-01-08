##########################################
# Copyright 2012-2014 Ceruti Francesco & contributors
#
# This file is part of LiSP (Linux Show Player).
##########################################

from threading import Thread, Lock, RLock
from functools import wraps, partial


_synchronized_meta_lock = Lock()


def async(wrapped=None, *, pool=None):
    '''Decorator to execute a method asynchronously.'''

    # If called with (keyword) arguments
    if wrapped is None:
        return partial(async, pool=pool)

    # Execute in a new thread
    if pool is None:
        @wraps(wrapped)
        def _async(*args, **kwds):
            Thread(target=wrapped, args=args, kwargs=kwds, daemon=True).start()
    # Execute in the specified pool
    else:
        @wraps(wrapped)
        def _async(*args, **kwds):
            pool.submit(wrapped, *args, **kwds)

    return _async


def synchronized(wrapped=None, *, blocking=True, timeout=-1):
    '''Decorator for synchronized instance method.'''

    # If called with (keyword) arguments
    if wrapped is None:
        return partial(synchronized, blocking=blocking, timeout=timeout)

    @wraps(wrapped)
    def _synchronized(self, *args, **kwargs):
        lock = vars(self).get('_synchronized_lock', None)

        # If the lock is not defined, then define it
        if lock is None:
            global _synchronized_meta_lock

            with _synchronized_meta_lock:
                if vars(self).get('_synchronized_lock', None) is None:
                    lock = RLock()
                    setattr(self, '_synchronized_lock', lock)

        try:
            if lock.acquire(blocking=blocking, timeout=timeout):
                return wrapped(self, *args, **kwargs)
        finally:
            try:
                lock.release()
            except Exception:
                pass

    return _synchronized
