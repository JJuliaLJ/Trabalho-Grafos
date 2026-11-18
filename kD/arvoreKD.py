import random 
import matplotlib.pyplot as plt

class Node:
    def __init__(self, point, left=None, right=None):
        self.point = point
        self.left = left
        self.right = right

class KDTree:
    def __init__(self):
        self.root = None

    def insert(self):
        
    def _add_node(self):    
       

if __name__ == "__main__":
    tree =  KDTree()

    numbers = random.sample(range(1, 100), 21)
    for number in numbers:
        tree.insert(number)
        
    tree.plot_tree()
    