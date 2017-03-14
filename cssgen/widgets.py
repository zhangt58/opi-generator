import xml.etree.ElementTree as et
from cssgen import nodes


class Widget(object):

    def __init__(self, id, x, y, width, height, name='widget'):
        self.x = nodes.TextNode(x)
        self.y = nodes.TextNode(y)
        self.width = nodes.TextNode(width)
        self.height = nodes.TextNode(height)
        self._name = name
        self._children = []
        self._parent = None
        self._typeId = id

    def assemble(self):
        if self._parent is None:
            self._node = et.Element(self._name)
        else:
            self._node = et.SubElement(self._parent.get_node(), self._name)
        self._node.set('typeId', self._typeId)
        for child in self._children:
            child.assemble()
        for var, val in sorted(vars(self).items()):
            if not var.startswith('_'):
                node = et.SubElement(self._node, var)
                val.render(node)

    def get_node(self):
        return self._node

    def set_parent(self, parent):
        self._parent = parent

    def add_child(self, child):
        self._children.append(child)
        child.set_parent(self)

    def __str__(self):
        self.assemble()
        return str(et.tostring(self._node))

    def write_to_file(self, filename):
        self.assemble()
        tree = et.ElementTree(self._node)
        tree.write(filename)


class Display(Widget):

    ID = 'org.csstudio.opibuilder.Display'

    def __init__(self, width, height):
        super(Display, self).__init__(Display.ID, 0, 0, width, height,
                                      name='display')
        self.auto_zoom_to_fit_all = nodes.TextNode('false')
        self.show_grid = nodes.TextNode('true')


class Rectangle(Widget):

    ID = 'org.csstudio.opibuilder.widgets.Rectangle'

    def __init__(self, x, y, width, height):
        super(Rectangle, self).__init__(Rectangle.ID, x, y, width, height)


class GroupingContainer(Widget):

    ID = 'org.csstudio.opibuilder.widgets.groupingContainer'

    def __init__(self, x, y, width, height):
        super(GroupingContainer, self).__init__(GroupingContainer.ID, x, y,
                                                width, height)