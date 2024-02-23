#!/usr/bin/python3


from CS312Graph import *
import time


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network
        self.dist = {node.node_id: float('inf') for node in self.network.nodes} #key: node_id (type int), value: cost from src to node (type int)
        self.prev = {} # dict of nodes that contain the last edge from previous node to current node in index

    def dijkstra_array(self,srcIndex):
        self.dist[srcIndex] = 0
        priority_queue = [node for node in self.network.nodes] #make-queue O(n)

        while len(priority_queue) > 0:
            
            '''
            u = min(priority_queue, key=lambda node: self.dist[node.node_id]) # O(n)
            priority_queue.remove(u) # O(n)
            '''
            min_index=0

            for i in range(len(priority_queue)):
                if self.dist[priority_queue[i].node_id] < self.dist[priority_queue[min_index].node_id]:
                    min_index = i

            u = priority_queue[min_index]
            priority_queue.pop(min_index)

        
            for edge in u.neighbors: # for each out_degree edge connected to the node
                new_dist = self.dist[u.node_id] + edge.length
                if new_dist < self.dist[edge.dest.node_id]: # check if the cost is less than the cost for that node found in dictionary
                    self.dist[edge.dest.node_id] = new_dist # update dictionary
                    self.prev[edge.dest.node_id] = edge #update prev with the node that
        
        return self.prev, self.dist

    def parent(self,i):
        return (i - 1)//2

    def left(self,i):
        return 2*i + 1

    def right(self,i):
        return 2*i + 2
    
    def bubble_up(self,heap, pointers, i): # switch parents and children based off new costs of children
        parent_i = self.parent(i)
        if i > 0 and self.dist[heap[i].node_id] < self.dist[heap[parent_i].node_id]:
            pointers[heap[i].node_id], pointers[heap[parent_i].node_id] = parent_i, i
            heap[i], heap[parent_i] = heap[parent_i], heap[i]
            self.bubble_up(heap, pointers, parent_i)

    def sift_down(self, heap, pointers, i): # update the heap order to reflect the new root which is the last element
        i_of_smallest = i
        left_i = self.left(i)
        right_i = self.right(i)
        if left_i < len(heap) and self.dist[heap[left_i].node_id] < self.dist[heap[i_of_smallest].node_id]:
            i_of_smallest = left_i
        if right_i < len(heap) and self.dist[heap[right_i].node_id] < self.dist[heap[i_of_smallest].node_id]:
            i_of_smallest = right_i
        if i_of_smallest != i:
            heap[i], heap[i_of_smallest] = heap[i_of_smallest], heap[i]
            pointers[heap[i_of_smallest].node_id], pointers[heap[i].node_id] = i_of_smallest, i
            self.sift_down(heap, pointers, i_of_smallest)

    def pop(self, heap, pointers): # remove root from heap and pointers, last element is new root, reorganize heap with sift down
        root = heap[0]
        last_element = heap.pop()
        if heap:  
            heap[0] = last_element
            pointers[last_element.node_id] = 0
            self.sift_down(heap, pointers, 0)
        del pointers[root.node_id]
        return root
    
    def dijkstra_heap(self, srcIndex):
        self.dist[srcIndex] = 0

        heap = [None]
        pointers = {srcIndex: 0}
        for node in self.network.nodes:
            if node.node_id != srcIndex:
                heap.append(node)
                pointers[node.node_id] = len(heap) - 1
            else:
                heap[0] = node

        while len(heap) > 0:
            u = self.pop(heap, pointers)

            for edge in u.neighbors:
                new_dist = self.dist[u.node_id] + edge.length
                if new_dist < self.dist[edge.dest.node_id]: 
                    self.dist[edge.dest.node_id] = new_dist 
                    self.prev[edge.dest.node_id] = edge
                    self.bubble_up(heap, pointers, pointers[edge.dest.node_id])


    def getShortestPath( self, destIndex):
        self.dest = destIndex
        path_edges = []
        total_length = 0
        edge = self.prev.get(destIndex)
        
        while edge is not None:
            path_edges.append((edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
            total_length += edge.length
            edge = self.prev.get(edge.src.node_id)
        
        if len(path_edges) == 0:
            return {'cost': float('inf'), 'path': path_edges}

        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()
        if use_heap:
            self.dijkstra_heap(srcIndex)
        else:
            self.dijkstra_array(srcIndex)
        t2 = time.time()
        return (t2-t1)

