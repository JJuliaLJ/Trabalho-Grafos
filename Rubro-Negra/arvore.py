import random
import matplotlib.pyplot as plt

class Node:
    def __init__(self, value, parent = None, left = None, right = None):
        self.value = value
        self.parent = parent
        self.left = left
        self.right = right
        self.color = 1 #1 = vermelho, 0 = preto

    def grandparent(self):
        if self.parent == None:
            return None    
        return self.parent.parent

    def sibling(self):
        if self.parent == None:
            return None
        if self == self.parent.left:
            return self.parent.right
        return self.parent.left

    def uncle(self):
        if self.parent == None:
            return None
        return self.parent.sibling()

class RBTree:
    def __init__(self):
        self.root = None

    def leftRotation(self, node):
        other_node = node.right
        node.right = other_node.left
        if other_node.left is not None:
            other_node.left.parent = node
        other_node.parent = node.parent
        if node.parent is None:
            self.root = other_node
        elif node == node.parent.left:
            node.parent.left = other_node
        else:
            node.parent.right = other_node
        other_node.left = node
        node.parent = other_node     


    def rightRotation(self, node):
        other_node = node.left
        node.left = other_node.right
        if other_node.right is not None:
            other_node.right.parent = node
        other_node.parent = node.parent
        if node.parent is None:
            self.root = other_node
        elif node == node.parent.right:
            node.parent.right = other_node
        else:
            node.parent.left = other_node
        other_node.right = node
        node.parent = other_node    

    def insert(self, value):
        new_node = Node(value)
        new_node.color = 1
        if self.root is None:
            self.root = new_node
        else:
            curr_node = self.root
            while True:
                if value < curr_node.value:
                    if curr_node.left is None:
                        curr_node.left = new_node
                        new_node.parent = curr_node
                        break
                    else:
                        curr_node = curr_node.left
                else:
                    if curr_node.right is None:
                        curr_node.right = new_node
                        new_node.parent = curr_node
                        break
                    else:
                        curr_node = curr_node.right        
        self.insert_fix(new_node)                


    def insert_fix(self, new_node):
        while new_node != self.root and new_node.parent.color == 1:
            if new_node.parent == new_node.grandparent().left:
                uncle = new_node.uncle()
                if uncle and uncle.color == 1:
                    new_node.parent.color = 0
                    uncle.color = 0
                    new_node.grandparent().color = 1
                    new_node = new_node.grandparent()
                else:
                    if new_node == new_node.parent.right:
                        new_node = new_node.parent
                        self.leftRotation(new_node)
                    new_node.parent.color = 0
                    new_node.grandparent().color = 1
                    self.rightRotation(new_node.grandparent())  
            else:
                uncle = new_node.uncle()
                if uncle and uncle.color == 1:
                    new_node.parent.color = 0
                    uncle.color = 0
                    new_node.grandparent().color = 1
                    new_node = new_node.grandparent()
                else:
                    if new_node == new_node.parent.left:
                        new_node = new_node.parent
                        self.rightRotation(new_node)
                    new_node.parent.color = 0
                    new_node.grandparent().color = 1
                    self.leftRotation(new_node.grandparent()) 
        self.root.color = 0


    def delete(self, value):
        node_remove = self.search(value)

        if node_remove is None:
            return

        if node_remove.left is None or node_remove.right is None:
            self.replace_node(node_remove, node_remove.left or node_remove.right)
        else:
            next = self.find_min(node_remove.right)
            node_remove.value = next.value
            self.replace_node(next, next.right)

        self.fix_delete(node_remove)    

    def fix_remove(self, node):
        while node != self.root and node.color == 1:
            if node == node.parent.left:
                sibling = node.sibling()
                if sibling.color == 0:
                    sibling.color = 1
                    node.parent.color = 0  
                    self.leftRotation(node.parent)
                    sibling = node.sibling()
                if (sibling.left is None or sibling.left.colot == 1) and (sibling.right is None or sibling.right.color == 1):
                    sibling.color = 0
                    node = node.parent
                else:
                    if sibling.right is None or sibling.right.color == 0:
                        sibling.left.color = 1
                        sibling.color = 0
                        self.rightRotation(sibling)
                        sibling = node.sibling()
                    sibling.color = node.parent.color
                    node.parent.color = 1
                    if sibling.right:
                        sibling.right.color = 1
                    self.leftRotation(node.parent)
                    node = self.root
            else:
                sibling = node.sibling()
                if sibling.color == 0:
                    sibling.color = 1
                    node.parent.color = 0
                    self.rightRotation(node.parent)
                    sibling = node.sibling()
                if(sibling.left is None or sibling.left.color == 1) and (sibling.right is None or sibling.right.color == 1):
                    sibling.color = 0
                    node = node.parent
                else:

                    if sibling.left is None or sibling.left.color == 1:
                        sibling.right.color = 1
                        sibling.color = 0 
                        self.leftRotation(sibling)
                        sibling = node.sibling()
                    sibling.color = node.parent.color
                    node.parent.color = 1
                    if sibling.left:
                        sibling.left.color = 1
                    self.rightRotation(node.parent)
                    node = self.root

        node.color = 1        

    def search(self, value):
        curr_node = self.root
        while curr_node is not None:
            if value == curr_node.value:
                return curr_node
            elif value < curr_node.value:
                curr_node = curr_node.left
            else:
                curr_node = curr_node.right
        return None    


    def find_min(self, node):
        while node.left is not None:
            node = node.left
        return node    

    def replace_node(self, old_node, new_node):
        if old_node.parent is None:
            self.root = new_node
        else:
            if old_node == old_node.parent.left:
                old_node.parent.left = new_node
            else:
                old_node.parent.right = new_node
        if new_node is not None:
            new_node.parent = old_node.parent

    def inorder_traversal(self, node):
        res = []
        if node is not None:
            res.extend(self.inorder_traversal(node.left))
            res.append(str(node.value)) 
            res.extend(self.inorder_traversal(node.right))
        return res

    def plot_tree(self):
        if self.root is None:
            print("Árvore vazia")
            return

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')

        def draw(node, x, y, x_spacing):
            if node is None:
                return
            node_color = 'red' if node.color == 1 else 'black'            
            if node.left:
                ax.plot([x, x - x_spacing], [y, y - 1], color='gray', zorder=1)
                draw(node.left, x - x_spacing, y - 1, x_spacing / 2)
            if node.right:
                ax.plot([x, x + x_spacing], [y, y - 1], color='gray', zorder=1)
                draw(node.right, x + x_spacing, y - 1, x_spacing / 2)
            ax.scatter(x, y, color=node_color, s=600, zorder=2, edgecolors='black')
            ax.text(x, y, str(node.value), color='white', weight='bold',
                    ha='center', va='center', fontsize=10, zorder=3)

        draw(self.root, x=0, y=0, x_spacing=10)
        plt.title("Árvore Rubro-Negra", fontsize=14, weight='bold')
        plt.show()           

if __name__ == "__main__":
    tree = RBTree()

    numbers = random.sample(range(1, 100), 21)
    for number in numbers:
        tree.insert(number)
        
    tree.plot_tree()
    
