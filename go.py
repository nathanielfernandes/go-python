from __future__ import annotations
from typing import Callable, Any, Iterator, Generic, TypeVar

import functools
from threading import Thread, Lock, Condition
from contextlib import ExitStack
from queue import Queue


def go(fn: Callable, /, *args, **kwargs):
    Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()


def defer(fn: Callable, /, *args, **kwargs) -> Callable:
    raise Exception(
        "Attempted to defer function without using `with_defer` or `golang` decorator"
    )


def with_defer(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with ExitStack() as stack:

            def defer(fn: Callable, /, *args, **kwargs):
                stack.callback(fn, *args, **kwargs)

            fn.__globals__.update({"defer": defer})
            return fn(*args, **kwargs)

    return wrapper


T = TypeVar("T")


class chan(Generic[T]):
    __slots__ = ("__queue__", "__capacity__", "__closed__", "__mutex__", "__count__")

    def __init__(self, capacity: int = 1) -> None:
        self.__capacity__ = capacity
        self.__queue__ = Queue(maxsize=capacity)
        self.__mutex__ = Lock()
        self.__closed__ = False
        self.__count__ = 0

    def __len__(self) -> int:
        return self.__count__

    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> T:
        with self.__mutex__:
            if self.__closed__ and self.__count__ == 0:
                raise StopIteration

        return self.r()

    def s(self, msg: T):
        """send msg to channel"""
        with self.__mutex__:
            if self.__closed__:
                raise Exception("attempted to send on closed channel")
            self.__count__ += 1
        self.__queue__.put(msg)

    def r(self) -> T:
        """recieve msg from channel"""
        with self.__mutex__:
            if self.__closed__ and self.__count__ == 0:
                return None
            self.__count__ -= 1
        return self.__queue__.get()

    def r_go(self) -> tuple[T, bool]:
        with self.__mutex__:
            if self.__closed__ and self.__count__ == 0:
                return None, False
            self.__count__ -= 1
        return self.__queue__.get(), True

    def cap(self) -> int:
        return self.__capacity__

    def close(self) -> int:
        with self.__mutex__:
            self.__closed__ = True


def select(*chans: chan) -> tuple[chan, Any]:
    raise Exception(
        "Attempted to select without using `with_select` or `golang` decorator"
    )


def with_select(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        selected = {}

        def select(*chans: chan):
            selected_chan = selected.get(chans, chan(0))

            def collect(c: chan):
                selected_chan.s((c, c.r()))

            for c in chans:
                go(collect, c)

            return selected_chan.r()

        fn.__globals__.update({"select": select})
        return fn(*args, **kwargs)

    return wrapper


def golang(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with ExitStack() as stack:
            selected = {}

            def defer(fn: Callable, /, *args, **kwargs):
                stack.callback(fn, *args, **kwargs)

            def select(*chans: chan):
                selected_chan = selected.get(chans, chan(0))

                def collect(c: chan):
                    selected_chan.s((c, c.r()))

                for c in chans:
                    go(collect, c)

                return selected_chan.r()

            fn.__globals__.update({"defer": defer, "select": select})
            return fn(*args, **kwargs)

    return wrapper


class WaitGroup:
    __slots__ = ("__tasks__", "__mutex__", "__all_done__")

    def __init__(self) -> None:
        self.__tasks__ = 0
        self.__mutex__ = Lock()
        self.__all_done__ = Condition(self.__mutex__)

    def Add(self, tasks: int):
        with self.__mutex__:
            self.__tasks__ += tasks

    def Done(self):
        with self.__all_done__:
            tasks_left = self.__tasks__ - 1
            if tasks_left <= 0:
                self.__all_done__.notify_all()
            self.__tasks__ = tasks_left

    def Wait(self):
        with self.__all_done__:
            self.__all_done__.wait_for(lambda: self.__tasks__ <= 0)
