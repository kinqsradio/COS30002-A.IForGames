from vector2d import Vector2D
from node import Node
import math

def astar(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    
    start_node, end_node = Node(None, start), Node(None, end)
    start_node.g = start_node.h = start_node.f = 0
    end_node.g = end_node.h = end_node.f = 0

    open_list, closed_list = [start_node], []

    while open_list:
        current_node = min(open_list, key=lambda o:o.f)
        open_list.remove(current_node)
        closed_list.append(current_node)

        if current_node == end_node:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1] # Return reversed path

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares
            node_position = Vector2D(current_node.position.x + new_position[0], current_node.position.y + new_position[1])

            if 0 <= node_position.x < len(maze) and 0 <= node_position.y < len(maze[0]) and maze[node_position.x][node_position.y] == 0:
                new_node = Node(current_node, node_position)
                children.append(new_node)

        for child in children:
            if child in closed_list:
                continue
            
            child.g = current_node.g + 1
            child.h = ((child.position.x - end_node.position.x) ** 2) + ((child.position.y - end_node.position.y) ** 2)
            child.f = child.g + child.h

            if add_to_open_list(child, open_list): # see next function
                open_list.append(child)

def add_to_open_list(child, open_list):
    for open_node in open_list:
        if child == open_node and child.g > open_node.g:
            return False
    return True


def dijkstra(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    
    start_node, end_node = Node(None, start), Node(None, end)
    start_node.g = 0

    open_list, closed_list = [start_node], []

    while open_list:
        current_node = min(open_list, key=lambda o:o.g)
        open_list.remove(current_node)
        closed_list.append(current_node)

        if current_node.position == end_node.position:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1] # Return reversed path

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares
            node_position = Vector2D(current_node.position.x + new_position[0], current_node.position.y + new_position[1])

            if 0 <= node_position.x < len(maze) and 0 <= node_position.y < len(maze[0]) and maze[node_position.x][node_position.y] == 0:
                new_node = Node(current_node, node_position)
                children.append(new_node)

        for child in children:
            if any(child.position == closed_child.position for closed_child in closed_list):
                continue
            
            child.g = current_node.g + 1
            
            if not any(child.position == open_node.position and child.g > open_node.g for open_node in open_list):
                open_list.append(child)
