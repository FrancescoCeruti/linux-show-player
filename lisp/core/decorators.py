# This file is part of Linux Show Player
#
# Copyright 2016 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

import logging
from functools import wraps, partial
from threading import Thread, Lock, RLock


def async_function(target):
    """Decorator. Make a function asynchronous.

    The decorated function is executed in a differed thread.
    """

    @wraps(target)
    def wrapped(*args, **kwargs):
        Thread(target=target, args=args, kwargs=kwargs, daemon=True).start()

    return wrapped


def async_in_pool(pool):
    """Decorator. Make a function asynchronous in a specified pool.

    The decorated function is executed in the specified threads-pool.

    .. Usage::

        class MyClass:
            __MyPool = ThreadPoolExecutor(10)

            @async_in_pool(__MyPool)
            def do_some_task(self):
                pass

    """

    def decorator(target):
        @wraps(target)
        def wrapped(*args, **kwargs):
            pool.submit(target, *args, **kwargs)

        return wrapped

    return decorator


def locked_function(target=None, *, lock=None, blocking=True, timeout=-1):
    """Decorator. Make a *function* "synchronized".

    Only one thread at time can access the decorated function.

    :param target: the function to decorate
    :param lock: the lock to be used (if not specified an RLock is created)
    :param blocking: if True the lock-acquirement is blocking
    :param timeout: timeout for the lock-acquirement
    """

    # If called with (keywords) arguments
    if target is None:
        return partial(
            locked_function, lock=lock, blocking=blocking, timeout=timeout
        )

    if lock is None:
        target.__lock__ = RLock()
    else:
        target.__lock__ = lock

    @wraps(target)
    def locked(*args, **kwargs):
        try:
            if target.__lock__.acquire(blocking=blocking, timeout=timeout):
                return target(*args, **kwargs)
            else:
                return
        finally:
            try:
                target.__lock__.release()
            except RuntimeError:
                pass

    return locked


def locked_method(target=None, *, blocking=True, timeout=-1):
    """Decorator. Make a *method* "synchronized".

    Only one thread at time can access the decorated method.

    :param target: the function to decorate
    :param blocking: if True the lock-acquirement is blocking
    :param timeout: timeout for the lock-acquirement
    """

    # If called with (keywords) arguments
    if target is None:
        return partial(locked_method, blocking=blocking, timeout=timeout)

    # generate a lock_name like "__method_name_lock__"
    lock_name = "__" + target.__name__ + "_lock__"
    target.__meta_lock__ = Lock()

    @wraps(target)
    def locked(self, *args, **kwargs):
        with target.__meta_lock__:
            lock = getattr(self, lock_name, None)

            # If the lock is not defined, then define it
            if lock is None:
                lock = RLock()
                setattr(self, lock_name, lock)

        try:
            if lock.acquire(blocking=blocking, timeout=timeout):
                return target(self, *args, **kwargs)
            else:
                return
        finally:
            try:
                lock.release()
            except RuntimeError:
                pass

    return locked


def suppress_exceptions(target=None, *, log=True):
    """Decorator. Suppress all the exception in the decorated function.

    :param log: If True (the default) exceptions are logged as warnings.
    """

    if target is None:
        return partial(suppress_exceptions, print_exc=log)

    @wraps(target)
    def wrapped(*args, **kwargs):
        try:
            return target(*args, **kwargs)
        except Exception:
            logging.warning("Exception suppressed.", exc_info=True)

    return wrapped


def memoize(callable_):
    """Decorator. Caches a function's return value each time it is called.

    If called later with the same arguments, the cached value is returned
    (not reevaluated).

    .. Note::
        This works for any callable object.
        The arguments are cached (as strings) in object.cache.
    """
    cache = callable_.cache = {}

    @wraps(callable_)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = callable_(*args, **kwargs)
        return cache[key]

    return memoizer
