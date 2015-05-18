# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2015 Francesco Ceruti <ceppofrancy@gmail.com>
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

from functools import wraps, partial
from operator import xor
from threading import Thread, Lock, RLock

# TODO: test for memory leaks
_synchronized_meta_lock = Lock()


def async(target):
    """A decorator for make a function asynchronous.

    The decorated function is executed in a differed thread.
    """

    @wraps(target)
    def wrapped(*args, **kwargs):
        Thread(target=target, args=args, kwargs=kwargs, daemon=True).start()

    return wrapped


def async_in_pool(pool):
    """A decorator for make a function asynchronous in a specified pool.

    The decorated function is executed in the specified threads-pool.
    Can be used if you have a method that you want to be non blocking but you
    want to specify a concurrency "limit".

    Usage::

        class MyClass:
            __MyPool = ThreadPoolExecutor(10)

            @async_in_pool(__MyPool)
            def do_some_heavy_task(self)
                # Do some async stuff

    """

    def decorator(target):
        @wraps(target)
        def wrapped(*args, **kwargs):
            pool.submit(target, *args, **kwargs)

        return wrapped

    return decorator


def synchronized_on(lock, blocking=True, timeout=-1):
    """A decorator for make a function synchronized using a specified lock.

    Only one thread at time can access the decorated function, but the same
    thread can reenter the function.
    """

    def decorator(target):
        @wraps(target)
        def wrapped(*args, **kwargs):
            try:
                if lock.acquire(blocking=blocking, timeout=timeout):
                    return target(*args, **kwargs)
            finally:
                try:
                    lock.release()
                except RuntimeError:
                    pass

        return wrapped

    return decorator


@synchronized_on(_synchronized_meta_lock)
def synchronized(target=None, *, blocking=True, timeout=-1):
    """A decorator for make a function synchronized.

    Only one thread at time can access the decorated function, but the same
    thread can reenter the function.

    .. Usage::

        class MyClass:
            @synchronized
            def sync():
                pass

            @synchronized(timeout=5)
            def sync_timeout():
                pass

            @synchronized(blocking=False)
            def sync_no_block():
                pass

    """

    # If called with (keywords) arguments
    if target is None:
        return partial(synchronized, blocking=blocking, timeout=timeout)

    # If the lock is not defined, then define it
    if not hasattr(target, '_sync_lock'):
        target._sync_lock = RLock()

    return synchronized_on(target._sync_lock, blocking, timeout)(target)


def typechecked(target):
    """A decorator to make a function check its arguments types at runtime.

    Annotations are used for checking the type (e.g. def fun(a: int, b: str)),
    this decorator should be used only if really needed, duck typing is the
    python-way, furthermore this will add a little overhead.
    """

    @wraps(target)
    def wrapped(*args, **kwargs):
        for index, name in enumerate(target.__code__.co_varnames):
            annotation = target.__annotations__.get(name)
            # Only check if annotation exists and it is as a type
            if isinstance(annotation, type):
                # First len(args) are positional, after that keywords
                if index < len(args):
                    value = args[index]
                elif name in kwargs:
                    value = kwargs[name]
                else:
                    continue

                if not isinstance(value, annotation):
                    raise TypeError('Incorrect type for "{0}"'.format(name))

        return target(*args, **kwargs)

    return wrapped


def check_state(*states, not_in=False):
    """Decorator to check the state of the object that own the target function.

    The target is called only if the object state is successfully checked.

    .. warning::
        Can be used only on bounded-methods, of objects with a "state"
        attribute.

    :param states: The states to check
    :param not_in: When True, check that the object is not in on of the states
    """

    def decorator(target):
        @wraps(target)
        def wrapped(self, *args, **kwargs):
            if xor(self.state in states, not_in):
                return target(self, *args, **kwargs)

        return wrapped

    return decorator