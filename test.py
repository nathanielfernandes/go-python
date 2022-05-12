from go import with_defer, go, defer, chan, select, with_select, golang, WaitGroup
import time


@with_defer
def soup():
    print("inner start")
    for i in range(5):
        # time.sleep(0.1)
        defer(print, i)

    print("inner end")


@with_defer
def poop(a=None):
    # print(a)
    defer(print, a)
    # print("inner start")
    # time.sleep(0.2)
    # for i in range(5):
    #     defer(print, i)
    pass
    # print("inner end")


@with_defer
def goop(a=None):
    # print(a)
    defer(print, a)
    # return a


def clear(a):
    a.clear()


@with_defer
def hello(a):
    defer(clear, a)

    # a.append("noura")
    # a.append("hello")

    defer(poop, "a")
    defer(poop, "a")

    return a + ["bye"]


a = []
# b = hello(a)

# print(b)
# print(a)


def main():
    messages = chan(1)

    def f():
        messages.s("ping")
        print("sent")

    messages.s("pong2")
    go(f)

    # def g():
    # messages.send("pong2")

    # msg = messages.recieve()

    # print(msg)

    # msg = messages.recieve()

    # print(msg)

    msg = messages.r()
    print(msg)

    time.sleep(1)

    msg = messages.r()
    print(msg)

    # g()


"""
package main

import (
    "fmt"
    "time"
)

func main() {

    c1 := make(chan string)
    c2 := make(chan string)

    go func() {
        time.Sleep(1 * time.Second)
        c1 <- "one"
    }()
    go func() {
        time.Sleep(2 * time.Second)
        c2 <- "two"
    }()

    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-c1:
            fmt.Println("received", msg1)
        case msg2 := <-c2:
            fmt.Println("received", msg2)
        }
    }

"""


@golang
def main2():
    c1 = chan()
    c2 = chan()

    def f1():
        time.sleep(1)
        c1.s("one")

    def f2():
        time.sleep(2)
        c2.s("two")

    go(f1)
    # go(f1)
    go(f2)
    go(f2)

    # print(c1.__queue__)
    print(c1.r())

    # for _ in range(2):
    #     c, msg = select(c1, c2)

    #     if c is c1:
    #         print("from c1:", msg)
    #     elif c is c2:
    #         print("from c2:", msg)

    # c2.close()
    # for msg in c2:
    #     print(msg)


def soup0():
    main2()

    time.sleep(5)


# soup0()

wg = WaitGroup()


def greeting(g, times):
    for i in range(times):
        print(g)
        time.sleep(1)

    wg.Done()


def main3():
    wg.Add(2)

    go(greeting, "hi", 10)
    go(greeting, "hello", 10)

    wg.Wait()
    print("Done")


@golang
def test123():
    print("counting")

    a = 0
    for i in range(10):
        a = i
        defer(print, a, i)

    x = 42
    a = x

    print("done")


test123()
