import random
from math import log10, exp, sqrt
import xml.etree.cElementTree as ET


class CNode(object):
    def __init__(self, x, y, size, size_of_vector, max_weight):
        self.weights = []
        self.size_of_vector = size_of_vector
        self.max_vector = float(max_weight)
        self.position = (x, y)
        self.size_radius = size / 2.0
        self.init_weights()
        self.min_freq = 0
        self.max_freq = 0

    def init_weights(self):
        i = 0
        while i < self.size_of_vector:
            self.weights.append(random.random() * self.max_vector)  # init random weight for each weight
            i += 1

    def get_distance(self, weight_input):
        distance = 0.0
        i = 0
        for weight in self.weights:
            distance += pow(weight_input[i] - weight, 2)
            i += 1
        return distance

    def get_distance_to_node(self, node):
        x_distance = self.position[0] - node.position[0]
        y_distance = self.position[1] - node.position[1]
        distance = pow(x_distance, 2) + pow(y_distance, 2)
        return distance

    def get_euclidean_distance_to_node(self, node):
        return sqrt(self.get_distance_to_node(node))

    def weight_distance_to_node(self, node):
        sum_squared = 0
        for i in range(len(self.weights)):
            sum_squared += pow(self.weights[i] - node.weights[i], 2)
        return sqrt(sum_squared)

    def adjust_weight(self, input_weight, learning_rate, influence):
        i = 0
        for weight in self.weights:  # iterate all over the weight
            self.weights[i] = weight + learning_rate * influence * (input_weight[i] - weight)
            i += 1


class SelfOrganizingMap(object):
    def __init__(self, width, x_num, y_num, epoch, vector_length, max_weight):
        self.x_num = x_num
        self.y_num = y_num
        self.size = width / x_num
        self.width = width
        self.height = y_num * self.size
        self.epoch = epoch
        self.max_weight = max_weight
        self.vector_length = vector_length
        self.nodes = []
        self.node_matrix = []
        self.initial_learning_rate = 0.1
        self.learning_rate = self.initial_learning_rate
        self.initial_radius = max([self.width, self.height]) / 2.0
        self.time_constant = self.epoch / log10(self.initial_radius)
        self.radius = self.initial_radius
        self.init_learning = False
        self.bmu = None
        self.epoch_count = 0
        self.u_matrix = []
        self.min_u = 0
        self.max_u = 0
        self.create_nodes()

    def reset_param(self):
        self.learning_rate = self.initial_learning_rate
        self.radius = self.initial_radius
        self.bmu = None
        self.epoch_count = 0

    def create_nodes(self):
        for i in range(self.x_num):
            row = []
            for j in range(self.y_num):
                x = i * self.size + self.size / 2.0
                y = j * self.size + self.size / 2.0
                node = CNode(x, y, self.size, self.vector_length, self.max_weight)
                row.append(node)
                self.nodes.append(node)
            self.node_matrix.append(row)

    def learn(self, sample):
        self.set_bmu(sample)
        self.calculate_neighbourhood_radius()
        self.adjust_node_weight(sample)
        self.epoch_count += 1

    def set_bmu(self, sample):
        min_distance = 999999999999999999999.9
        r = len(self.nodes)
        for i in range(r):
            test_node = self.nodes[i]
            distance = test_node.get_distance(sample)
            if distance < min_distance:
                self.bmu = test_node
                min_distance = distance

    def get_bmu(self,sample):
        min_distance = 999999999999999999999.9
        r = len(self.nodes)
        bmu = None
        for i in range(r):
            test_node = self.nodes[i]
            distance = test_node.get_distance(sample)
            if distance < min_distance:
                bmu = test_node
                min_distance = distance
        return bmu

    def calculate_neighbourhood_radius(self):
        self.radius = self.initial_radius * exp(-self.epoch_count / self.time_constant)
        # print("radius = " + str(self.radius))

    def adjust_node_weight(self, sample):
        for node in self.nodes:
            distance_to_bmu_squared = node.get_distance_to_node(self.bmu)
            radius_squared = pow(self.radius, 2)
            if distance_to_bmu_squared < radius_squared:
                influence = exp(-distance_to_bmu_squared / (2 * radius_squared))
                node.adjust_weight(sample, self.learning_rate, influence)
        self.calculate_learning_rate()

    def calculate_learning_rate(self):
        self.learning_rate = self.initial_learning_rate * exp(-self.epoch_count / self.epoch)

    def create_u_matrix(self):
        min_u = 99999999999999.0
        max_u = 0.0
        for i in range(self.x_num):
            row = []
            for j in range(self.y_num):
                distance_list = self.get_u_distance(i, j)
                sum_u = 0
                for distance in distance_list:
                    sum_u += distance
                u_distance = sum_u/len(distance_list)
                if u_distance > max_u:
                    max_u = u_distance
                if u_distance < min_u:
                    min_u = u_distance
                row.append(u_distance)
            self.u_matrix.append(row)
        self.min_u = min_u
        self.max_u = max_u


    def get_u_distance(self, i, j):
        selected_node = self.node_matrix[i][j]
        distance = []
        try:
            if i-1 >= 0:
                node = self.node_matrix[i-1][j]
                distance.append(selected_node.weight_distance_to_node(node))
        except IndexError:
            pass
        try:
            if j-1 >= 0:
                node = self.node_matrix[i][j-1]
                distance.append(selected_node.weight_distance_to_node(node))
        except IndexError:
            pass
        try:
            node = self.node_matrix[i+1][j]
            distance.append(selected_node.weight_distance_to_node(node))
        except IndexError:
            pass
        try:
            node = self.node_matrix[i][j+1]
            distance.append(selected_node.weight_distance_to_node(node))
        except IndexError:
            pass
        return distance

    def write(self):
        root_xml = ET.Element("root")
        nodes_xml = ET.SubElement(root_xml, "nodes")
        for node in self.nodes:
            node_xml = ET.SubElement(nodes_xml, "node")
            position_xml = ET.SubElement(node_xml, "position")
            ET.SubElement(position_xml, "x").text = str(node.position[0])
            ET.SubElement(position_xml, "y").text = str(node.position[1])
            weights_xml = ET.SubElement(node_xml, "weights")
            for weight in node.weights:
                ET.SubElement(weights_xml, "w").text = str(weight)
        tree = ET.ElementTree(root_xml)
        tree.write("data/training.xml")

    def read(self):
        xml = ET.parse("data/training.xml").getroot()
        nodes_xml = xml[0]
        i = 0
        for node_xml in nodes_xml:
            node = self.nodes[i]
            for child in node_xml:
                if child.tag == 'position':
                    node.position = (float(child[0].text), float(child[1].text))
                if child.tag == 'weights':
                    j = 0
                    while j < len(node.weights):
                        node.weights[j] = float(child[j].text)
                        j += 1
                    # print(node.weights)
            i += 1

