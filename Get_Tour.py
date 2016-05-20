from Get_Data import Node, Edge, find_locations, get_distances
from main import make_sure
from gurobipy import *
import numpy as np
import random
import time

class Tour:
    '''This class creates Tour objects.
    Each object has to be created with a starting point (lat,long), an optional ending point (if not provided it's asumed that it's the same starting point),
    a city in which the tour exists and a maximum time duration for the tour (in minutes).
    When the tour is calculated it will have a starting node (Node object) attribute, an ending node (Node object) attribute, a city attribute, a duration atribute with
    the duration calculated for the tour, a rating attribute with the best rating posible for the tour, the max_duration provided for the tour and a nodes
    attribute with the list of nodes visited in the tour.
    '''
    from Get_Data import Node, Edge, find_locations, get_distances

    def __init__(self, start=[[0,0]], end = [[0,0]], city_name = 'San_Francisco', max_duration = 300, start_time = 0, travel_type = 'driving'):
        self.start = Node('start', lat = start[0][0], long = start[0][1], buss_city = city_name, comp_time = start_time, open_hours = [start_time,start_time+max_duration])
        self.end = Node('end', lat = end[0][0], long = end[0][1], buss_city = city_name, comp_time = 0, open_hours = [start_time,start_time+max_duration])
        self.city_name = city_name
        self.duration = 'Tour not yet calculated'
        self.rating = 'Tour not yet calculated'
        self.num_types = []
        self.max_duration = max_duration
        self.start_time = start_time
        self.travel_type = travel_type
        self.nodes = []
        self.compleated = False
        self.id = ''

    

    def geo_interface(self):
        ''' This method converts the tour data in to GeoJSON format'''

        if len(self.nodes) == 0:
            return print("Tour not yet calculated")

        self.id = '{}_{}_Tour'.format(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))

        coordinates = [(node.lat,node.long) for node in self.nodes]
        node_names = [node.name for node in self.nodes]
        num_types = {}

        for buss_type in np.unique([node.buss_type for node in self.nodes]):
             num_types[buss_type] = [node.buss_type for node in self.nodes].count(buss_type)

        return {'type': 'feature', 'geometry':{ 'type' : 'multiPoint', 'coordinates': coordinates },
                'properties': {'rating' : self.rating, 'duration' : self.duration, 'start_time' : self.start_time, 'buss_names' : [node.name for node in self.nodes], 'city' : self.city_name,
                               'buss_types' : [node.buss_type for node in self.nodes] , 'num_types' : num_types, 'compleated' : self.compleated }, 'travel_type': self.travel_type, 'id' : self.id}


    def get_nodes(self, n = 100, buss_types = [], ran = False):
        ''' This method creates an array of nodes to be used for creating the tour or gets the nodes from file,
        depending on if the ran argument is True (random points in a city) or False (actual businesses from the city '''

        if ran == False:
            with open('{}_Data.json'.format(city_name)) as f:
                     data = json.load(f)
            selected = []
            for buss_type in buss_types:
                selected.extend([Node(feature['properties']['name'],feature['geometry']['coordinates'][0],feature['geometry']['coordinates'][1],
                                 feature['properties']['rating'], feature['properties']['buss_type'], feature['properties']['buss_categories'],
                                 feature['properties']['buss_image'], feature['properties']['buss_city'], feature['id']) for feature in random.sample([feature for feature in data['features'] if feature['properties']['buss_city'] == city_name if feature['properties']['buss_type'] == buss_type], n)])

            return selected

        elif ran == True:
            locations = find_locations(city_name, max_points = n)
            buss_types =  make_sure('buss_types')
            selected = []
            i=0
            for buss_type in random.sample(buss_types.keys(),4):
                 
                selected.extend([Node('{},{}'.format(location[0],location[1]),location[0],location[1],random.randrange(0,6), buss_type=buss_type,
                                    buss_categories = "[random.sample(buss_types[buss_type]['categories'],1)]", buss_image = '',
                                    buss_city = self.city_name, comp_time = buss_types[buss_type]['durations'], open_hours = make_sure('buss_types')[buss_type]['open_hours']) for location in locations[int(i*n/4):int((i+1)*n/4)]])
                i +=1

            return selected

    
    def get_edges(self, nodes = [], ran = False):
        ''' This method creates an array of edges betwwen nodes for creating the tour or gets the edges from file,
        depends if the ran argument is True (edges between the nodes with random distances) or False (actual distances between the nodes).
        Even if ran is False it is posible that some of the distances are random due that some of the distances in file can be random as well (See Add_edges function
        for further explanation)'''

        edges = []

        if ran == 'New':

            distances = get_distances(start = nodes,end = nodes, travel_type = self.travel_type)
            for node1 in nodes:
                for node2 in nodes:
                    if (node1.name,node2.name) not in distances.keys():
                        edges.append(Edge(node1.name, (node1.lat,node1.long), node2.name, (node2.lat,node2.long), random.randint(2,20), travel_type = self.travel_type, ran = 'Yes'))
                    else:
                        edges.append(Edge(node1.name, (node1.lat,node1.long), node2.name, (node2.lat,node2.long), distances[(node1.name,node2.name)], travel_type = self.travel_type, ran = 'Yes'))

        if ran == 'Old':
            with open('{}_Data.json'.format(self.city_name)) as f:
                        data = json.load(f)
            for node1 in nodes:
                for node2 in nodes:
                    if (node1.name,node2.name) in [['properties']['name'] for feature in data['features']]:
                        
                        edges.extend([Edge(feature['properties']['start_name'], feature['properties']['start_location'],feature['properties']['end_name'],
                                           feature['properties']['end_location'], feature['properties']['duration'], travel_type = feature['properties']['travel_type']) for feature in data['features'] if
                                           feature['geometry']['type'] == 'lineString' if feature['properties']['start_Name'] in [node.name for node in nodes] if
                                           feature['properties']['end_Name'] in [node.name for node in nodes]])
            
        if ran==True:
            for node1 in nodes:
                for node2 in nodes:
                    edges.append(Edge(node1.name, (node1.lat,node1.long), node2.name, (node2.lat,node2.long), random.randint(2,20), travel_type = self.travel_type, ran = 'Yes'))
        return edges

    def OS_TSP(self, n = 100, buss_types = [], short = True, ran = True):
        '''This method solves the Optional Stop Traveling Salesman Problem using Gurobi
        The problem is formulated as an Orienteering problem (we maximize the expected return with a max time constraint)
        If short == True the basic Orienteeting problem is solved. If short == False additional time constrains are added to the model'''

        def subtourelim(model, where):
            "This function adds a contraint to the model for every subtour in the solution"

            if where == GRB.Callback.MIPSOL:
                selected = []
                # make a list of edges selected in the solution
                for i in range(len(nodes)):
                    sol = model.cbGetSolution([model._vars[i,j] for j in range(len(nodes))])
                    selected += [(i,j) for j in range(len(nodes)) if sol[j] > 0.5]
                # find the shortest cycle in the selected edge list
                tour = subtour(selected)
                if len(tour) < len(selected):
                    # add a subtour elimination constraint
                    expr = 0
                    for i in range(len(tour)):
                        for j in range(i+1,len(tour)):
                            expr += model._vars[tour[i],tour[j]]
                    model.cbLazy(expr <= len(tour)-1)


        def subtour(sel):
            "This function identifies the shortest subtour"

            cycles = []
            lengths = []
            maybe2 = []
            selected = {}
            visited = {}

            for x,y in sel:
                maybe2.append(x)
                maybe2.append(y)
            for it in set(maybe2):
                selected[it] = []
                visited[it] = False
            for x,y in sel:
                selected[x].append(y)
            while True:
                current = [key for key in visited.keys() if visited[key] == False][0]             
                thiscycle = [current]
                while True:
                    visited[current] = True
                    neighbors = [x for x in selected[current] if not visited[x]]
                    if len(neighbors) == 0:
                        break
                    current = neighbors[0]
                    thiscycle.append(current)
                lengths.append(len(thiscycle))
                if sum(lengths) == len(sel):
                    break                    
            return cycles[lengths.index(min(lengths))]

        "Get data for the tour"
        buss_types = make_sure('buss_types')

        nodes = self.get_nodes(city_name = self.city_name, n = n, buss_types = buss_types, ran=ran)
        nodes.append(self.start)
        nodes.append(self.end)
        edges = self.get_edges(nodes,city_name = self.city_name, travel_type = self.travel_type, ran=True)

        end_time = self.start_time + self.max_duration
        nhours = math.ceil(end_time/60)
        ndays = math.ceil(end_time/(24*60))
        range_hours = [hour for hour in range(1,nhours+1)]

        "Model declaration"

        m = Model('MyModel')

        if short == True:

            "Variable declaration"
            edge_vars = dict() #The edge variables represent the rout between the businesses visited or not

            for i in range(len(nodes)):
                for j in range(len(nodes)):
                    edge_vars[i,j] = m.addVar(obj=nodes[j].rating,vtype=GRB.BINARY, name= '{}_{}_edge'.format(nodes[i].name,nodes[j].name)) #Edge variable, 1 if visited 0 if not

            m.modelSense = GRB.MAXIMIZE #Maximize the objective function

            m.update()

            "Constraints declaration"

            for j in range(len(nodes)):
                if nodes[j].name != 'start' and nodes[j].name != 'end':
                    m.addConstr(quicksum(edge_vars[i,j] for i in range(len(nodes))) - quicksum(edge_vars[j,i] for i in range(len(nodes)))  == 0, 'Conservation of flow node {}'.format(nodes[j].name)) #Number of edges going in to node = number of edges going out
                if nodes[j].name == 'end':
                    m.addConstr(quicksum(edge_vars[i,j] for i in range(len(nodes))) == 1, 'Start flow constraint') #One edge going out of start node
                if nodes[j].name == 'start':
                    m.addConstr(quicksum(edge_vars[i,j] for i in range(len(nodes))) == 0, 'Start in constraint') #No edges going in to start node
                if nodes[j].name == 'start':
                    m.addConstr(quicksum(edge_vars[j,i] for i in range(len(nodes))) == 1, 'End flow constraint') #One edge going in to end node
                if nodes[j].name == 'end':
                    m.addConstr(quicksum(edge_vars[j,i] for i in range(len(nodes))) == 0, 'End out constraint') #No edges going out of end node


            m.addConstr(quicksum(quicksum(([edge for edge in edges if edge.name == (nodes[i].name,nodes[j].name)][0].duration[self.travel_type] + nodes[i].comp_time ) * edge_vars[i,j] for i in range(len(nodes))) for j in range(len(nodes))) <= end_time, 'MaxDuration Constraint') #Duration of tour can't exceed the specified max duration

            m.update()

            #Bounds for centain nodes
            for i in range(len(nodes)):
                for j in range(len(nodes)):
                    if nodes[i].name == 'start' and nodes[j].name == 'end':
                        edge_vars[i,j].ub = 0
                    if nodes[i].name == 'end' and nodes[j].name == 'start':
                        edge_vars[i,j].ub = 0
                    if nodes[i].name == nodes[j].name:
                        edge_vars[i,j].ub = 0


            m.update()

        if short == False:

            #NOT FINISHED DON'T USE!!!!
            "Variable declaration"
            edge_vars = dict() #The edge variables represent the rout between the businesses visited or not
            time_vars = dict() #The time variables represent hour time spams for each edge

            for buss_type in np.unique([node.buss_type for node in nodes if node.name != 'start' if node.name != 'end']):
                for node in [node for node in nodes if buss_type == node.buss_type]:
                    time_vars[node.name] = m.addVar(ub=node.open_hours[1],lb=node.open_hours[0],vtype=GRB.CONTINUOUS, name=node.name)

            time_vars['end'] = m.addVar(ub=[node for node in nodes if node.name == 'end'][0].open_hours[1],lb=[node for node in nodes if node.name == 'end'][0].open[0],vtype=GRB.CONTINUOUS, name=node.name)
            time_vars['start'] = m.addVar(ub=[node for node in nodes if node.name == 'start'][0].open_hours[1],lb=[node for node in nodes if node.name == 'start'][0].open[0],vtype=GRB.CONTINUOUS, name=node.name)

            for edge in edges:
                edge_vars[(edge.start_name,edge.end_name)] = m.addVar(obj = [node.rating for node in nodes if edge.end_name == node.name][0], vtype=GRB.BINARY, name= '{}_edge'.format(edge.name)) #Arc variable, 1 if selected 0 if not


            m.modelSense = GRB.MAXIMIZE #Maximize the objective function

            m.update()

            "Constraints declaration"
        
            m.addConstr(time_vars['start'] == start_time, 'Start time arrival') #The start time for the starting node in the provided start time

            for node in [node for node in nodes if node.name != 'start' if node.name != 'end']:
                m.addConstr(quicksum(edge_vars[(edge.start_name,edge.end_name)] for edge in edges if edge.end_name == node.name) - quicksum(edge_vars[(edge.start_name,edge.end_name)] for edge in edges if edge.start_name == node.name) == 0, 'Conservation of flow')


            m.update()

            for edge in edges:
                m.addConstr(edge_vars[(edge.start_name,edge.end_name)] * (time_vars[[node for node in nodes if node.name == edge.end_name][0].name] - time_vars[[node for node in nodes if node.name == edge.start_name][0].name] - [node for node in nodes if node.name == edge.start_name][0].comp_time - edge.duration[travel_type]) <= 0)

            m.addConstr(quicksum(edge_vars[(edge.start_name,edge.end_name)] for edge in edges if edge.end_name == 'end') == 1, 'Start flow constraint' % node.name) #One edges to go out of start node
            m.addConstr(quicksum(edge_vars[(edge.start_name,edge.end_name)] for edge in edges if edge.start_name == 'start') == 1, 'End flow constraint' % node.name) #One edge has to go in to end node

            m.addConstr(quicksum(edge_vars[(edge.start_name,edge.end_name)] for edge in edges if [node.buss_type for node in nodes if edge.end_name == node][0] == 'Restaurant') <= 2*ndays) #Only 2 restaurants per day
        
            m.update()

        m.params.LazyConstraints = 1
        m._vars = edge_vars
        m.optimize(subtourelim)

        solution = m.getAttr('x', edge_vars)
        selected = [option for option in solution.keys() if solution[option] > 0.5]

        final_edges=[]
        for sol in selected:
            final_edges.append((nodes[sol[0]].name,nodes[sol[1]].name))

        edges_duration=0
        for fg in final_edges:
                edges_duration += [edge.duration[self.travel_type] for edge in edges if fg==edge.name][0]

        final_nodes=[]
        for x,y in final_edges:
            final_nodes.append(x)
            final_nodes.append(y)

        nodes_selected = set(final_nodes)

        for fg in nodes_selected:
            self.nodes.append([node for node in nodes if node.name == fg])

        nodes_duration = 0
        for fg in nodes_selected:
            nodes_duration += [node.comp_time for node in nodes if fg==node.name][0]

        self.duration = edges_duration + nodes_duration
        