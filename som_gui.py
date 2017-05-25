from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush, QColor, QFont
from PyQt5.QtWidgets import QGraphicsSimpleTextItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsRectItem
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene


class SomGui(QtWidgets.QMainWindow):
    def __init__(self, som, element_dict, element_freq_dict, graph):
        super().__init__()
        self.som = som
        self.elements = element_dict
        self.element_freq = element_freq_dict
        self.graph = graph
        self.graphic_view = None
        self.scene = None
        self.item_dict = {}
        self.initUI()
        self.show_mapping()

    def initUI(self):
        self.resize(self.som.width*1.2, self.som.height*1.2)
        self.graphic_view = QGraphicsView()
        self.scene = QGraphicsScene()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self.scene.setBackgroundBrush(brush)
        self.graphic_view.setScene(self.scene)
        self.setCentralWidget(self.graphic_view)
        self.show()

    def show_mapping(self):
        for node in self.graph.nodes(data=True):
            element_vector = self.elements[node[0]]
            bmu = self.som.get_bmu(element_vector)
            # print(element + " : " + str(bmu.position))
            self.add_text(bmu.position[0], bmu.position[1], node[0], node[1]['freq'])
        self.add_edge()
        self.add_u_matrix()

    def add_text(self, pos_x, pos_y, text, freq):
        min_freq = self.som.min_freq
        max_freq = self.som.max_freq
        size = 10 + 36 * (freq-min_freq)/(max_freq-min_freq)
        psize = 8 + 8 * (freq-min_freq)/(max_freq-min_freq)
        text_label = QGraphicsSimpleTextItem(text)
        font = QFont()
        font.setPointSize(psize)
        text_label.setFont(font)
        text_label.setPos(pos_x + 5, pos_y)
        pen = QPen()
        pen.setStyle(Qt.NoPen)
        color = QColor(255, 0, 0, 120)
        brush = QBrush(color)
        circle = QGraphicsEllipseItem(pos_x-size/2, pos_y-size/2, size, size)
        circle.setPen(pen)
        circle.setBrush(brush)
        i = 0
        for item in self.item_dict.values():
            delta_x = text_label.pos().x() - item[0].pos().x()
            delta_y = text_label.pos().y() - item[0].pos().y()
            '''if delta_x < 50 and delta_y < 0:
                text_label.setPos(text_label.pos().x(),text_label.pos().y()+pow(-1, i)*5)
                circle.setPos(circle.pos().x(),circle.pos().y()+pow(-1, i)*5)
                for j in item:
                    j.setPos(j.pos().x(),j.pos().y()-pow(-1, i+1)*5)'''
            i += 1
        self.item_dict[text] = [text_label, circle]
        self.scene.addItem(circle)
        self.scene.addItem(text_label)

    def add_edge(self):
        for edge in self.graph.edges(data=True):
            u, v, d = edge
            weight = d['weight']
            print(weight)
            pos_1 = self.item_dict[u][0].pos()
            pos_2 = self.item_dict[v][0].pos()
            x1 = pos_1.x() - 5
            y1 = pos_1.y()
            x2 = pos_2.x() - 5
            y2 = pos_2.y()
            color = QColor(0, 0, 255, 100)
            pen = QPen(color)
            width = 0.4 + 8*weight/ self.som.max_weight
            pen.setWidthF(width)
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setZValue(-10)
            line.setPen(pen)
            self.scene.addItem(line)

    def add_u_matrix(self):
        size = self.som.size
        for i in range(self.som.x_num):
            for j in range(self.som.y_num):
                u = self.som.u_matrix[i][j]
                node = self.som.node_matrix[i][j]
                value = 255 - (u-self.som.min_u)/(self.som.max_u-self.som.min_u) * 255
                color = QColor(value, value, value)
                color.setAlpha(180)
                brush = QBrush(color)
                pen = QPen()
                pen.setStyle(Qt.NoPen)
                rect = QGraphicsRectItem(node.position[0]-size/2.0, node.position[1]-size/2.0, size, size)
                rect.setBrush(brush)
                rect.setPen(pen)
                rect.setZValue(-100)
                self.scene.addItem(rect)
                pass
        pass