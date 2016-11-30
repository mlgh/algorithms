
"""
PoC Implementation of
https://courses.csail.mit.edu/6.851/spring14/lectures/L01.html
page 4:
Making any pointer machine partially persistent.
That is - you can only modify the latest version, but you have
read-only access to any previous version
"""

import collections

class Mod(object):
    def __init__(self, field, value, version):
        self.field = field
        self.value = value
        self.version = version

NO_VALUE = object()

class NodeKeyError(KeyError):
    pass

class Common(object):
    def __init__(self, max_links):
        self.max_links = max_links

        self.max_mods = self.max_links * 2
        self.version = 0

    def increment_version(self):
        self.version += 1

class Revision(object):
    def __init__(self, node, version):
        self.node = node
        self.version = version

    def get_field(self, field):
        return self.node.get_field(field, self.version)

def latest(value):
    if isinstance(value, Node):
        return value.get_latest()
    return value

class BackLink(object):
    def __init__(self, field, node):
        self.field = field
        self.node = node

    def __repr__(self):
        return 'BackLink(%r, %r)' % (self.field, self.node)

class Node(object):
    def __init__(self, common, name=None):
        self.common = common
        self.name = name

        self.fields = {}
        self.mods = []
        self.refs = {}
        self.next_node = None

    def __repr__(self):
        return "Node(%s)" % self.name

    def get_latest(self):
        node = self
        while node.next_node is not None:
            node = node.next_node
        return node

    def get_field(self, field, version, default=NO_VALUE):
        result = self.fields.get(field, default)
        for mod in self.mods:
            if mod.version > version:
                break
            if mod.field == field:
                result = mod.value
        if result is NO_VALUE:
            raise NodeKeyError(field)
        return result

    def get_fields(self, version):
        fields = dict(self.fields)
        for mod in self.mods:
            if mod.version > version:
                break
            fields[mod.field] = mod.value
        return fields

    def get_backlink_fields(self):
        for i in xrange(self.common.max_links):
            yield '_backlink_%d' % i

    def allocate_backlink_field(self, field, node):
        vacant_backlink_field = None
        fields = self.get_fields(self.common.version)
        for backlink_field in self.get_backlink_fields():
            backlink = fields.get(backlink_field)
            if backlink is None:
                if vacant_backlink_field is None:
                    vacant_backlink_field = backlink_field
                continue
        if vacant_backlink_field is None:
            raise ValueError("No vacant backlink field", self, fields)
        return vacant_backlink_field

    def find_backlink_field(self, field, node):
        fields = self.get_fields(self.common.version)
        for backlink_field in self.get_backlink_fields():
            backlink = fields.get(backlink_field)
            if backlink is None:
                continue
            if backlink.node is node and backlink.field == field:
                return backlink_field
        return None

    @staticmethod
    def replace_node(old_node, new_node, queue):
        common = new_node.common
        fields = new_node.get_fields(common.version)
        # Follow all backlinks and update corresponding fields
        for backlink_field in new_node.get_backlink_fields():
            backlink = fields.get(backlink_field)
            if backlink is None:
                continue
            other_node = latest(backlink.node)
            other_node.add_mod(backlink.field, new_node, queue)
        # Some other nodes may have backlinks to us, fix them
        for field, value in fields.iteritems():
            if not isinstance(value, Node):
                continue
            other_node = latest(value)
            backlink_field = other_node.find_backlink_field(field, old_node)
            other_node.add_mod(backlink_field, BackLink(field, new_node), queue)


    def set_field(self, field, value):
        queue = collections.deque()

        # This is the only place where we introduce new connections
        old_value = self.get_field(field, self.common.version, None)
        if isinstance(old_value, Node):
            # Must also remove backlink here
            backlink_field = old_value.find_backlink_field(field, self)
            assert backlink_field is not None
            old_value.add_mod(backlink_field, None, queue)
        self.add_mod(field, value, queue)
        if isinstance(value, Node):
            backlink_field = value.find_backlink_field(field, self)
            if backlink_field is None:
                backlink_field = value.allocate_backlink_field(field, self)
            value.add_mod(backlink_field, BackLink(field, self), queue)

        # Here we only replace old nodes with new one
        while queue:
            node = queue.popleft()
            if node.next_node is not None:
                continue
            new_node = Node(self.common, str(node.name) + '_cloned')
            node.next_node = new_node
            new_node.fields = node.get_fields(self.common.version)
            node.mods = node.mods[:self.common.max_mods]
            self.replace_node(node, new_node, queue)

        return Revision(latest(self), self.common.version)

    def add_mod(self, field, value, queue):
        if self.next_node is not None:
            raise ValueError("Node is frozen", self)
        self.common.increment_version()
        version = self.common.version
        self.mods.append(Mod(field, value, version))

        if len(self.mods) > self.common.max_mods:
            queue.append(self)

        return Revision(self, version)

class LinkedList(object):
    def __init__(self, common):
        self.common = common

        self.root = Node(common, "root")
        self.root.set_field('prev', self.root)
        self.root.set_field('next', self.root)

    def push_back(self, node):
        root = self.root
        prev = latest(root).get_field('prev', self.common.version)
        latest(prev).set_field('next', latest(node))
        latest(root).set_field('prev', latest(node))
        latest(node).set_field('prev', latest(prev))
        res = latest(node).set_field('next', latest(root))
        self.root = latest(self.root)

        return self.get_snapshot()

    def push_front(self, node):
        root = self.root
        nxt = latest(root).get_field('next', self.common.version)
        latest(root).set_field('next', latest(node))
        latest(nxt).set_field('prev', latest(node))
        latest(node).set_field('prev', latest(root))
        latest(node).set_field('next', latest(nxt))
        self.root = latest(self.root)

        return self.get_snapshot()

    def pop_back(self):
        root = self.root
        node = latest(root).get_field('prev', self.common.version)
        if node is root:
            raise ValueError("pop_back from empty list")

        prev = node.get_field('prev', self.common.version)

        latest(node).set_field('prev', None)
        latest(node).set_field('next', None)

        latest(prev).set_field('next', latest(root))
        latest(root).set_field('prev', latest(prev))

        self.root = latest(root)
        return self.get_snapshot()

    def pop_front(self):
        root = self.root
        node = latest(root).get_field('next', self.common.version)
        if node is root:
            raise ValueError("pop_back from empty list")

        nxt = node.get_field('next', self.common.version)

        latest(node).set_field('prev', None)
        latest(node).set_field('next', None)

        latest(nxt).set_field('prev', latest(root))
        latest(root).set_field('next', latest(nxt))

        self.root = latest(root)
        return self.get_snapshot()

    def get_snapshot(self):
        return ListSnapshot(self.root, self.common.version)

class ListSnapshot(object):
    def __init__(self, root, version):
        self.root = root
        self.version = version

    def __iter__(self):
        runner = self.root.get_field('next', self.version)
        while runner is not self.root:
            yield runner
            runner = runner.get_field('next', self.version)
