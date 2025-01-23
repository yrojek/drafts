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

    def add_publishers_to_watch(self, *publishers):
        self._publishers = self._publishers + [p.__subscribe(self) for p in publishers]

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

    # a graph consists of 5 nodes
    # DateNode(INPUT) NameNode (INPUT)
    #       |          /     |
    #       |         /      |
    #       |        /       |
    #       |       /        |
    #     OccupancyNode    PersonalDataNode
    #          \            /
    #           \          /
    #            \        /
    #            ReportNode (OUTPUT)

    class DateNode(GraphNode):
        def __init__(self):
            super().__init__()
            self._moved_in_date = None

        @graph_input
        def move_in(self, current_date):
            print('DateNode move_in()')
            self._moved_in_date = current_date

        def get_moved_in_date(self):
            print('DateNode get_moved_in_date()')
            return self._moved_in_date

    class NameNode(GraphNode):
        def __init__(self):
            super().__init__()
            self._occupant_name = None

        @graph_input
        def move_in(self, name):
            print('NameNode move_in()')
            self._occupant_name = name

        def get_occupant_name(self):
            print('NameNode get_occupant_name()')
            return self._occupant_name

    class OccupancyNode(GraphNode):
        def __init__(self, date_node, name_node):
            super().__init__(date_node, name_node)
            self._date_node = date_node
            self._name_node = name_node

        def update(self):
            print('OccupancyNode update()')

        def get_data(self):
            print('OccupancyNode get_data()')
            return "{} moved in on {}".format(self._name_node.get_occupant_name(), self._date_node.get_moved_in_date())

    class PersonalDataNode(GraphNode):
        def __init__(self, name_node):
            super().__init__(name_node)
            self._name_node = name_node
            self._personal_data = None

        def update(self):
            print('PersonalDataNode update()')
            person_name = self._name_node.get_occupant_name()
            # get personal data from a database
            person_telephone = "+1-111-555-1111"
            person_address = "123, High street, London, UK, RG1 3DW"
            self._personal_data = (person_name, person_telephone, person_address)

        def get_data(self):
            print('PersonalDataNode get_data()')
            return "Name: {}, Address: {}, Telephone: {}".format(*self._personal_data)

    class ReportNode(GraphNode):
        def __init__(self, occupancy_node, personal_data_node):
            super().__init__(occupancy_node, personal_data_node)
            self._occupancy_node = occupancy_node
            self._personal_data_node = personal_data_node
            self._report = None

        def update(self):
            print('ReportNode update()')
            self._report = self._personal_data_node.get_data() + '. ' + self._occupancy_node.get_data()

        @graph_output
        def get_data(self):
            print('ReportNode get_data()')
            return self._report

    class HotelBuilder:
        def __init__(self):
            self._date = DateNode()
            self._name = NameNode()
            self._occupancy = OccupancyNode(self._date, self._name)
            self._personal = PersonalDataNode(self._name)
            self._report = ReportNode(self._occupancy, self._personal)

        def date_node(self): return self._date
        def name_node(self): return self._name
        def report_node(self): return self._report


    hotel_builder = HotelBuilder()

    print('Have built a hotel')
    hotel_builder.name_node().move_in('John Doe')
    hotel_builder.date_node().move_in('2025-01-01')
    print(hotel_builder.report_node().get_data())
