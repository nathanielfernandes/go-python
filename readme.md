# go-python?

A couple of functions and decorators that bring some of golangs features into python.

I don't intend to actually use these, it was just a fun exploration and learning experience!

### Features

- `defer`
- `go`
- `chan`
- `WaitGroup`
- `select`

### How it works

```py
@with_defer     # injects a defer method into the function scope
@with_select    # injects a select method into the function scope
@golang         # injects both defer and select into the function scope
```

- `defer` works by wrapping a function and making use of python's `contextlib.ExitStack()`
- `select` works by wrapping a function and using python's `queue.Queue`
- `go` works by just starting a `thread` to run the function
- `chan` works by using python's `queue.Queue` and adding some extra behavoirs to match go
- `WaitGroup` works by using python's `threading.Mutex` and `threading.Condition` to keep track of tasks

### Example Usage

<hr/>

##### go

```go
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
```

##### python

```py
from go import *

@golang
def main():
    c1 = chan()
    c2 = chan()

    def f1():
        time.sleep(1)
        c1.s("one")
    go(f1)

    def f2():
        time.sleep(2)
        c2.s("two")
    go(f2)

    for _ in range(2):
        c, msg = select(c1, c2)
        if c is c1:
            print("recieved (from c1)", msg)
        elif c is c2:
            print("recieved (from c2)", msg)

main()
```

<hr/>

##### go

```go
package main

import "fmt"

func main() {
    fmt.Println("counting")

    var a *int
    for i := 0; i < 10; i++ {
        a = &i
        defer fmt.Println(*a, i)
    }

    x := 42
    a = &x

    fmt.Println("done")
}
```

##### python

```python
from go import *

@golang
def main():
    print("counting")

    a = 0
    for i in range(10):
        a = i
        defer(print, a, i)

    x = 42
    a = x

    print("done")

main()
```

<hr/>
