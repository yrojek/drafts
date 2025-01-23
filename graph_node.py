import functools

# You need to implement only update() method and correctly initialize the object via parent __init__()
# The base class' __init__() accepts a list of nodes that are publishers for the node.
# There may be other dependencies that do not need to be updated in any order or updated at all.
# You only want to decorate setters for input nodes and getters for output nodes of the graph
# All intermediary nodes can have arbitrary getters/setters
# It is recommended to use a builder design pattern for constructing a graph and only expose
# inputs and outputs from the builder
# Graph should have no loops or else you end up with an infinite recursion and memory overflow!


def graph_input(func):
    # method decorator for setters of graph input nodes
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        is_changed = func(self, *args, **kwargs)
        if is_changed:
            self.invalidate()
        return is_changed

    return wrapper


def graph_output(func):
    # method decorator for getters of output nodes
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.request_update()
        return func(self)

    return wrapper


class GraphNode(object):
    def __init__(self, *publishers):
        self._need_update = True
        self._publishers = [p.__subscribe(self) for p in publishers]
        self._subscribers = []
        pass

    def update(self):
        # The only method that needs to be overwritten
        pass

    def __subscribe(self, subscriber):
        self._subscribers.append(subscriber)
        return self

    def invalidate(self):
        # should never be overloaded or called directly
        if self._need_update:
            # stop the recursion here
            return

        self._need_update = True
        [s.invalidate() for s in self._subscribers]

    def request_update(self):
        # should never be overloaded or called directly
        if not self._need_update:
            # stop the recursion
            return

        [p.request_update() for p in self._publishers]
        self.update()
        self._need_update = False


if __name__ == '__main__':
    class A1(GraphNode):

        def __init__(self, i1, i2):
            super().__init__(i1, i2)
            self._i1 = i1
            self._i2 = i2

            self._data = None

        def update(self):
            self._data = self._i1.get_value() + self._i2.get_value()

        @graph_output
        def get_value(self):
            return self._data

    class I1(GraphNode):
        @graph_input
        def check_new_input(self, v):
            self._v = v
            return False

        @graph_output
        def get_value(self):
            return self._v

    i1 = I1()
    i2 = I1()
    a1 = A1(i1, i2)
    i1.check_new_input(3.)
    i2.check_new_input(5.3)

    print(a1.get_value())

    i1.check_new_input(5)
    print(a1.get_value())
