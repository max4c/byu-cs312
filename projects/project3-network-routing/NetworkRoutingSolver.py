#!/usr/bin/python3


from CS312Graph import *
import time


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network
        self.shortest_path_to_node = {node.node_id: float('inf') for node in self.network.nodes} #key: node_id (type int), value: cost from src to node (type int)
        prev = {} # dict of nodes that contain the last edge from previous node to current node in index

    def dijkstra_array(self,srcIndex):
        self.shortest_path_to_node[srcIndex] = 0
        priority_queue = [node for node in self.network.nodes]

        while len(priority_queue) > 0:

            u = min(priority_queue, key=lambda node: self.shortest_path_to_node[node.node_id])
            priority_queue.remove(u) # remove the found node from the queue

            for edge in u.neighbors: # for each out_degree edge connected to the node
                new_distance = self.shortest_path_to_node[u.node_id] + edge.length
                if new_distance < shortest_path_to_node[edge.dest.node_id]: # check if the cost is less than the cost for that node found in dictionary
                    shortest_path_to_node[edge.dest.node_id] = new_distance # update dictionary
                    prev[edge.dest.node_id] = u.node_id #update prev with last edge connected to node
        
        return prev, self.shortest_path_to_node

    def getShortestPath( self, destIndex):
        self.dest = destIndex
        # TODO: RETURN THE SHORTEST PATH FOR destIndex
        #       INSTEAD OF THE DUMMY SET OF EDGES BELOW
        #       IT'S JUST AN EXAMPLE OF THE FORMAT YOU'LL 
        #       NEED TO USE
        path_edges = []
        total_length = 0
        
        key = prev[destIndex]

        while True:
            try:
                key = prev[key]
            except KeyError:
                break
            

        # use prev dictionary
        # start with destIndex key
            # add the edge.length from value to key to total_length
            # add the edge to path_edges
        # move to the value node 
        # continue until you can't find a key (you find the root node)

        node = self.network.nodes[self.source]
        edges_left = 3
        while edges_left > 0:
            edge = node.neighbors[2]
            path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
            total_length += edge.length
            node = edge.dest
            edges_left -= 1
        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()
        if use_heap:
            return None
        else:
            dijkstra_array(srcIndex)
        # TODO: RUN DIJKSTRA'S TO DETERMINE SHORTEST PATHS.
        #       ALSO, STORE THE RESULTS FOR THE SUBSEQUENT
        #       CALL TO getShortestPath(dest_index)
        t2 = time.time()
        return (t2-t1)

