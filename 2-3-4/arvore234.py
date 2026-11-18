import random
import matplotlib.pyplot as plt

class Node:
    def __init__(self, leaf=True, parent=None):
        self.keys = []
        self.children = []
        self.leaf = leaf
        self.parent = parent

    def is_full(self):
        return len(self.keys) == 3    

class Tree234:
    def __init__(self):
        self.root = Node(leaf=True)

    def search(self, key, node=None):
        if node is None:
            node = self.root

        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return(node, i)
        if node.leaf:
            return None
        return self.search(key, node.children[i])

    def split_child(self, parent, child_idx):
        full_node = parent.children[child_idx]
        new_node = Node(leaf=full_node.leaf, parent=parent)

        middle_key = full_node.keys[1]
        new_node.keys = [full_node.keys[2]]
        full_node.keys = [full_node.keys[0]]

        if not full_node.leaf:
            new_node.children = full_node.children[2:]
            for child in new_node.children:
                child.parent = new_node
            full_node.children = full_node.children[:2]

        parent.keys.insert(child_idx, middle_key)
        parent.children.insert(child_idx + 1, new_node)

    def insert(self, key):
        if self.search(key) is not None:
            return False

        curr_root = self.root
        if curr_root.is_full():
            new_root = Node(leaf=False)
            self.root = new_root
            new_root.children.append(curr_root)
            curr_root.parent = new_root
            self.split_child(new_root, 0)
            self._insert_non_full(new_root, key)
        else: 
            self._insert_non_full(curr_root, key)
        return True

    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i+1] = node.keys[i]
                i -= 1
            node.keys[i+1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if node.children[i].is_full():
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)

    def delete(self, key):
        if self.search(key) is None:
            return False
        self._delete_recursive(self.root, key)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]
            self.root.parent = None
        return True

    def _delete_recursive(self, node, key):
        idx = 0
        while idx < len(node.keys) and node.keys[idx] < key:
            idx += 1

        if idx < len(node.keys) and node.keys[idx] == key:
            if node.leaf:
                node.keys.pop(idx)
            else:
                self._delete_internal_node(node, idx)
        else:
            if node.leaf:
                return
            is_last_child = (idx == len(node.keys))
            if len(node.children[idx].keys) < 2:
                self._fill_child(node, idx)
            if is_last_child and idx > len(node.keys):
                self._delete_recursive(node.children[idx-1], key)
            else:
                self._delete_recursive(node.children[idx], key)


    def _delete_internal_node(self, node, idx):
        key = node.keys[idx]
        if len(node.children[idx].keys) >= 2:
            pred = self._get_predecessor(node, idx)
            node.keys[idx] = pred
            self._delete_recursive(node.children[idx], pred)
        elif len(node.children[idx+1].keys) >= 2:
            succ = self._get_successor(node, idx)
            node.keys[idx] = succ
            self._delete_recursive(node.children[idx+1], succ)
        else:
            self.merge(node, idx)
            self._delete_recursive(node.children[idx], key)


    def _get_predecessor(self, node, idx):         
        curr = node.children[idx]
        while not curr.leaf:
            curr = curr.children[-1]
        return curr.keys[-1]                                                     

    
    def _get_successor(self, node, idx):     
        curr = node.children[idx + 1]
        while not curr.leaf:
            curr = curr.children[0]
        return curr.keys[0]                                             

    def _fill_child(self, node, idx):
        if idx != 0 and len(node.children[idx - 1].keys) >=2:
            self.borrow_from_prev(node, idx)
        elif idx != len(node.keys) and len(node.children[idx + 1].keys) >= 2:
            self.borrow_from_next(node, idx)
        else:
            if idx != len(node.keys):
                self.merge(node, idx)
            else:
                self.merge(node, idx -1)

    def borrow_from_prev(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx-1]
        child.keys.insert(0, node.keys[idx-1])
        if not child.leaf:
            moved_child = sibling.children.pop()
            moved_child.parent = child
            child.children.insert(0, moved_child)
        node.keys[idx-1] = sibling.keys.pop()          


    def borrow_from_next(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx+1]
        child.keys.append(node.keys[idx])
        if not child.leaf:
            moved_child = sibling.children.pop(0)
            moved_child.parent = child
            child.children.append(moved_child)
        node.keys[idx] = sibling.keys.pop(0)                      


    def merge(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx + 1]
        child.keys.append(node.keys.pop(idx))
        child.keys.extend(sibling.keys)
        if not child.leaf:
            for grand_child in sibling.children:
                grand_child.parent = child
            child.children.extend(sibling.children)
        node.children.pop(idx + 1) 

    def count_keys(self, node=None):
        if node is None:
            node = self.root
        total = len(node.keys)
        for child in node.children:
            total += self.count_keys(child)
        return total 

    def inorder_traversal(self, node=None):
        if node is None:
            node = self.root
        res = []
        for i in range(len(node.keys)):
            if not node.leaf:
                res.extend(self.inorder_traversal(node.children[i]))
            res.append(str(node.keys[i]))
        if not node.leaf:
            res.extend(self.inorder_traversal(node.children[-1]))
        return res  

    def plot_tree(self):
        if not self.root.keys:
            print("Árvore vazia")
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')

        def draw(node, x, y, width):
            num_children = len(node.children)
            if num_children > 0:
                step = width / num_children
                start_x = x - width / 2 + step / 2
                for i, child in enumerate(node.children):
                    child_x = start_x + i * step
                    ax.plot([x, child_x], [y, y-1], color='gray', linewidth=1.5, zorder=1)
                    draw(child, child_x, y-1, step)

            label = " | ".join(map(str, node.keys))
            ax.text(x, y, label, color='white', ha='center', va='center', fontsize=9, fontweight='bold', zorder=3, 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='#1f77b4', edgecolor="black", linewidth=1.2))
        
        draw(self.root, x=0, y=0, width=32)
        plt.title("Árvore 2-3-4", fontsize=14, weight='bold')
        plt.show()           

if __name__ == "__main__":
    tree = Tree234()

    numbers = random.sample(range(1, 100), 21)
    for n in numbers:
        tree.insert(n)
        
    tree.plot_tree()

    for n_del in numbers[1:4]:
        print(f"Removendo: {n_del}")
        tree.delete(n_del)

    tree.plot_tree()



   