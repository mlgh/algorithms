
import pytest
import random
from algolib.persistent_pointer_machine import *

class TestNode(object):
    @pytest.fixture
    def common(self):
        return Common(max_links=1)

    @pytest.fixture
    def node_factory(self, common):
        return lambda name=None: Node(common, name=name)

    @pytest.fixture
    def node(self, node_factory):
        return node_factory()

    def test_simple(self, node):
        rev = node.set_field('test', 'value')
        assert rev.get_field('test') == 'value'

    def test_update_value(self, node):
        rev1 = node.set_field('test', 'value1')
        rev2 = node.set_field('test', 'value2')

        assert rev1.get_field('test') == 'value1'
        assert rev2.get_field('test') == 'value2'

    def test_missing_field(self, node):
        rev1 = node.set_field('test1', 'value1')
        rev2 = node.set_field('test2', 'value2')
        with pytest.raises(NodeKeyError) as exc_info:
            rev1.get_field('test2')
        assert exc_info.value[0] == 'test2'

    def test_overflow_mods(self, node):
        rev1 = latest(node).set_field('test1', 'value1')
        rev2 = latest(node).set_field('test1', 'value2')
        rev3 = latest(node).set_field('test1', 'value3')
        rev4 = latest(node).set_field('test1', 'value4')

        assert rev4.node.get_field('test1', rev4.version) == 'value4'
        assert rev1.node.get_field('test1', rev1.version) == 'value1'
        assert rev1.node.next_node is not None

    def test_linking(self, node_factory):
        node1 = node_factory("node1")
        node2 = node_factory("node2")
        latest(node1).set_field('friend', node2)
        latest(node2).set_field('test1', 'value1')
        latest(node2).set_field('test1', 'value2')
        rev3 = latest(node2).set_field('test1', 'value3')
        linked_node_2 = latest(node1).get_field('friend', rev3.version)

        assert linked_node_2.get_field('test1', rev3.version) == 'value3'

    def test_overwrite_linkning(self, node_factory):
        node1 = node_factory()
        node2 = node_factory()
        node3 = node_factory()

        latest(node1).set_field('friend', latest(node2))
        latest(node1).set_field('friend', latest(node3))
        # Oops, ref2 still has backlink to ref1
        latest(node2).set_field('test1', 'value1')
        latest(node2).set_field('test2', 'value2')
        latest(node2).set_field('test3', 'value3')
        last_rev = latest(node3).set_field('test4', 'value4')

        friend = latest(node1).get_field('friend', last_rev.version)
        assert friend.get_field('test4', last_rev.version) == 'value4'



class TestLinkedList(object):
    @pytest.fixture
    def common(self):
        return Common(max_links=10)

    @pytest.fixture
    def lst(self, common):
        return LinkedList(common)

    @pytest.fixture
    def node_factory(self, common):
        def factory(name, value):
            node = Node(common, name=name)
            node.set_field('value', value)
            return node
        return factory

    def get_values(self, snapshot):
        return [
            node.get_field('value', snapshot.version)
            for node in snapshot
        ]

    def test_empty(self, lst):
        assert self.get_values(lst.get_snapshot()) == []

    def test_push_back(self, lst, node_factory):
        snap1 = lst.push_back(node_factory("node1", 1))
        snap2 = lst.push_back(node_factory("node2", 2))
        snap3 = lst.push_back(node_factory("node3", 3))
        assert self.get_values(snap1) == [1]
        assert self.get_values(snap2) == [1, 2]
        assert self.get_values(snap3) == [1, 2, 3]

    def test_pop_back(self, lst, node_factory):
        snap1 = lst.push_back(node_factory("node1", 1))
        snap2 = lst.push_back(node_factory("node2", 2))
        snap3 = lst.pop_back()
        snap4 = lst.push_back(node_factory("node3", 3))
        snap5 = lst.pop_back()
        snap6 = lst.pop_back()


        assert self.get_values(snap1) == [1]
        assert self.get_values(snap2) == [1, 2]
        assert self.get_values(snap3) == [1]
        assert self.get_values(snap4) == [1, 3]
        assert self.get_values(snap5) == [1]
        assert self.get_values(snap6) == []

    def test_random(self, lst, node_factory):
        deque = collections.deque()

        lst_snapshots = []
        deque_snaphots = []

        rnd = random.Random(0)

        for i in xrange(500):
            choices = ['push_front', 'push_back']
            if deque:
                choices += ['pop_front', 'pop_back']
            choice = rnd.choice(choices)
            if choice == 'push_front':
                num = rnd.randrange(100)
                deque.appendleft(num)
                snap = lst.push_front(node_factory('node', num))
            elif choice == 'push_back':
                num = rnd.randrange(100)
                deque.append(num)
                snap = lst.push_back(node_factory('node', num))
            elif choice == 'pop_front':
                deque.popleft()
                snap = lst.pop_front()
            elif choice == 'pop_back':
                deque.pop()
                snap = lst.pop_back()
            assert list(deque) == self.get_values(snap)
            lst_snapshots.append(snap)
            deque_snaphots.append(list(deque))
        for lst_snap, deque_snap in zip(lst_snapshots, deque_snaphots):
            assert deque_snap == self.get_values(lst_snap)

