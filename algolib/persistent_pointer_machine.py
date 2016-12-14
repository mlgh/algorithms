
import weakref

"""
PoC Implementation of
https://courses.csail.mit.edu/6.851/spring14/lectures/L01.html
page 4:
Making any pointer machine partially persistent.
That is - you can only modify the latest version, but you have
read-only access to any previous version
"""

class Mod(object):
    def __init__(self, field, value, version):
        self.field = field
        self.value = value
        self.version = version

class Common(object):
    def __init__(self, max_links, max_mods=None):
        self.max_links = max_links
        if max_mods is None:
            max_mods = 2 * self.max_links
        self.max_mods = max_mods

        self.version = 0

    def increment_version(self):
        self.version += 1

NO_VALUE = object()

class NodeKeyError(KeyError):
    pass

class Revision(object):
    def __init__(self, node, version):
        self.node = node
        self.version = version

    def get_field(self, field):
        return self.node.get_field(field, self.version)

class BackLink(object):
    def __init__(self, from_node, by_field):
        self.from_node = from_node
        self.by_field = by_field

    def __repr__(self):
        return 'BackLink(%r, %r)' % (self.from_node, self.by_field)

class Link(object):
    def __init__(self, to_node, by_field, backlink_idx):
        self.to_node = to_node
        self.by_field = by_field
        self.backlink_idx = backlink_idx

class NodeWatcher(object):
    def __init__(self, node):
        self.node = node

    def __enter__(self):
        self.node.add_watcher(self)
        return self

    def __exit__(self, *args):
        self.node.remove_watcher(self)

    def change_node(self, new_node):
        self.node = new_node
        self.node.add_watcher(self)

class Node(object):
    def __init__(self, common, name=None):
        self.common = common
        self.name = name

        self.fields = {}
        self.mods = []
        self.links = [None] * self.common.max_links
        self.backlinks = [None] * self.common.max_links

        self.node_watchers = []

        self.is_frozen = False

    def add_watcher(self, watcher):
        self.node_watchers.append(weakref.ref(watcher))

    def remove_watcher(self, watcher):
        self.node_watchers.remove(weakref.ref(watcher))

    def get_field(self, field, version, default=NO_VALUE):
        result = self.fields.get(field, default)
        for mod in self.mods:
            if mod.version > version:
                break
            if mod.field == field:
                result = mod.value
        if result is NO_VALUE:
            raise NodeKeyError(field, version)

        return result

    def get_fields(self, version):
        result = dict(self.fields)
        for mod in self.mods:
            if mod.version > version:
                break
            result[mod.field] = mod.value
        return result

    def add_backlink(self, from_node, by_field):
        vacant_position = None
        for i, backlink in enumerate(self.backlinks):
            if backlink is None:
                self.backlinks[i] = BackLink(from_node, by_field)
                return i
        raise ValueError("No vacant backlinks in %r" % (self,))

    def find_link(self, by_field):
        for i, link in enumerate(self.links):
            if link is not None and link.by_field == by_field:
                return i
        return None

    def find_vacant_link(self):
        for i, l in enumerate(self.links):
            if l is None:
                return i
        raise ValueError("No vacant links in %r", (self,))

    def set_field(self, field, value):
        if self.is_frozen:
            raise ValueError("Node is frozen", self)

        link_idx = self.find_link(field)

        if link_idx is not None:
            link = self.links[link_idx]
            link.to_node.backlinks[link.backlink_idx] = None
            self.links[link_idx] = None

        if isinstance(value, Node):
            backlink_idx = value.add_backlink(self, field)
            link = Link(to_node=value, by_field=field, backlink_idx=backlink_idx)
            self.links[self.find_vacant_link()] = link

        if len(self.mods) < self.common.max_mods:
            self.common.increment_version()
            self.mods.append(Mod(field, value, self.common.version))
            return Revision(self, self.common.version)

        new_node = Node(self.common, name=str(self.name) + "_cloned")

        for watcher_ref in self.node_watchers:
            watcher = watcher_ref()
            if watcher is not None:
                watcher.change_node(new_node)

        self.is_frozen = True

        self.common.increment_version()
        new_node.fields = self.get_fields(self.common.version)
        # Apply mod by hand
        new_node.fields[field] = value
        new_node.links = list(self.links)

        # Follow links
        for link in self.links:
            if link is None:
                continue
            link.to_node.backlinks[link.backlink_idx] = BackLink(new_node, link.by_field)

        # Follow backlinks
        for i, backlink in enumerate(self.backlinks):
            if backlink is None:
                continue
            backlink.from_node.set_field(backlink.by_field, new_node)

        return Revision(new_node, self.common.version)

class LinkedList(object):
    def __init__(self, common):
        self.common = common

        self.root = Node(common, "root")
        self.root.set_field('prev', self.root)
        self.root.set_field('next', self.root)
        assert not self.root.is_frozen

    def push_back(self, node):
        root = self.root
        prev = root.get_field('prev', self.common.version)
        with NodeWatcher(self.root) as w_root, NodeWatcher(prev) as w_prev, NodeWatcher(node) as w_node:
            w_prev.node.set_field('next', w_node.node)
            w_root.node.set_field('prev', w_node.node)
            w_node.node.set_field('prev', w_prev.node)
            res = w_node.node.set_field('next', w_root.node)
            self.root = w_root.node

        return self.get_snapshot()

    def push_front(self, node):
        root = self.root
        nxt = root.get_field('next', self.common.version)
        with NodeWatcher(root) as w_root, NodeWatcher(nxt) as w_nxt, NodeWatcher(node) as w_node:
            w_root.node.set_field('next', w_node.node)
            w_nxt.node.set_field('prev', w_node.node)
            w_node.node.set_field('prev', w_root.node)
            w_node.node.set_field('next', w_nxt.node)
            self.root = w_root.node

        return self.get_snapshot()

    def pop_back(self):
        root = self.root
        node = root.get_field('prev', self.common.version)
        if node is root:
            raise ValueError("pop_back from empty list")
        prev = node.get_field('prev', self.common.version)

        with NodeWatcher(root) as w_root, NodeWatcher(node) as w_node, NodeWatcher(prev) as w_prev:
            w_node.node.set_field('prev', None)
            w_node.node.set_field('next', None)
            w_prev.node.set_field('next', w_root.node)
            w_root.node.set_field('prev', w_prev.node)

            self.root = w_root.node
        return self.get_snapshot()

    def pop_front(self):
        root = self.root
        node = root.get_field('next', self.common.version)

        if node is root:
            raise ValueError("pop_front from empty list")

        nxt = node.get_field('next', self.common.version)

        with NodeWatcher(root) as w_root, NodeWatcher(node) as w_node, NodeWatcher(nxt) as w_nxt:
            w_node.node.set_field('prev', None)
            w_node.node.set_field('next', None)
            w_nxt.node.set_field('prev', w_root.node)
            w_root.node.set_field('next', w_nxt.node)

            self.root = w_root.node

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
