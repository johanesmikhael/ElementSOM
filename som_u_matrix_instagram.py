import csv
import random
import sys

import networkx
from PyQt5.QtWidgets import QApplication
from som_gui import SomGui

from som import SelfOrganizingMap

elements_list = []
element_dict = {}
element_weighted_dict = {}
element_freq_dict = {}
element_index = {}
element_list = []
graph = networkx.Graph()


with open("data/11052017 sevel cikini elements.csv", newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        try:
            data = row[0]
            elements = data.split(", ")
            elements_list.append(elements)
        except IndexError:
            pass

i = 0
for elements in elements_list:
    for element in elements:
        if element not in element_dict:  # the word is not exist yet
            element_dict[element] = []
            element_weighted_dict[element] = []
            element_freq_dict[element] = 0
            element_list.append(element)
            element_index[element] = i
            graph.add_node(element)
            print(i)
            print(element)
            i += 1

z = 0
for key in element_dict.keys():
    print(key)
    print("elem len")
    print(len(element_list))
    o = 0
    for element in element_list:
        print(element)
        element_dict[key].append(0)
        element_weighted_dict[key].append(0)
        print(o)
        o+=1
    print(z)
    z+=1

max_count = 0
min_freq = 0
max_freq = 0

for elements in elements_list:  # getting connectivity
    i = 0
    for element in elements:
        element_freq_dict[element] += 1
        if element_freq_dict[element] > max_freq:
            max_freq = element_freq_dict[element]
        j = 0
        for checked_elem in elements:
            print(element)
            print(checked_elem)
            # print("j" + str(j))
            if not i == j:  # not refer to self
                index = element_index[checked_elem]
                # print("indext" + str(index))
                print("------------------------------------------------------------------")
                print(i)
                print(j)
                print(index)
                print(element_dict[element])
                if element_dict[element][index] == 0:
                    element_dict[element][index] = 1
                else:
                    element_dict[element][index] += 1
                element_weighted_dict[element][index] += 1
                if element_weighted_dict[element][index] > max_count:
                    max_count = element_weighted_dict[element][index]
            j += 1
        i += 1



# creating weighted graph
for element in element_list:
    graph.node[element]['freq'] = element_freq_dict[element]
    vector = element_weighted_dict[element]
    for i in range(len(element_list)):
        weight = vector[i]
        if weight > 0:  # element is connected to another
            if not graph.has_edge(element, element_list[i]):  # no edge yet
                graph.add_edge(element, element_list[i], weight=weight)

for edge in graph.edges(data=True):
    # print(edge)
    pass


for key in element_dict:
    pass
    # print(key + " = " + str(element_dict[key]))

for elem in element_list:
    pass
    # print("e  : " + elem)
    # print(element_index[elem])

# start som training
is_learning = False # set either the som will lear or used previous training result
num_of_epoch = 5000
max_vector_weight = max_count
vector_len = len(element_list)
counter = 0
width = 1200
x_num = 60
y_num = 60
print("max vector " + str(max_vector_weight))
som = SelfOrganizingMap(width, x_num, y_num, num_of_epoch, vector_len, max_vector_weight)
som.min_freq = min_freq
som.max_freq = max_freq
if is_learning:
    epoch = num_of_epoch
    while epoch > 0:
        print(epoch)
        pick_index = random.randrange(vector_len)
        element = element_list[pick_index]
        element_vector = element_dict[element]
        som.learn(element_vector)
        epoch -= 1
    som.create_u_matrix()
    som.write()
else:
    som.read()
    som.create_u_matrix()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SomGui(som, element_dict, element_freq_dict, graph)
    sys.exit(app.exec_())
