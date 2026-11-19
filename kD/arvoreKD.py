import random 
import math
import matplotlib.pyplot as plt

class Node:
    def __init__(self, point, axis, parent = None, left=None, right=None):
        self.point = point
        self.axis = axis
        self.parent = parent
        self.left = left
        self.right = right
        self.count = 1

class KDTree:
    def __init__(self, k=2):
        self.root = None
        self.k = k

    def search(self, point):
        curr = self.root
        depth = 0
        while curr is not None:
            if curr.point == point:
                return curr
            axis = depth % self.k
            curr = curr.left if point[axis] < curr.point[axis] else curr.right
            depth += 1
        return None    

    def insert(self, point):
        existing = self.search(point)
        if existing is not None:
            existing.count +=1
            return
        if self.root is None:
            self.root = Node(point, axis = 0)
            return

        curr = self.root
        depth = 0
        while True:
            axis = depth % self.k
            if point[axis] < curr.point[axis]:
                if curr.left is None:
                    curr.left = Node(point, axis=(depth+1) % self.k, parent=curr)
                    break
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = Node(point, axis=(depth+1) % self.k, parent=curr)
                    break
                curr = curr.right
            depth +=1        
        
    def find_min(self, node, target_axis, depth):
        if node is None:
            return None
        curr_axis = depth % self.k
        if curr_axis == target_axis:
            return node if node.left is None else self.find_min(node.left, target_axis, depth+1)

        left_min = self.find_min(node.left, target_axis, depth+1)
        right_min = self.find_min(node.right, target_axis, depth+1)

        best = node
        for candidate in (left_min, right_min):
            if candidate is not None and candidate.point[target_axis] < best.point[target_axis]:
                best = candidate
        return best

    def delete(self, point):
        target = self.search(point)
        if target is None:
            return False
        if target.count > 1:
            target.count -=1
            return True

        self.root = self._delete_recursive(self.root, point, depth=0)
        if self.root is not None:
            self.root.parent = None
        return True

    def _delete_recursive(self, node, point, depth):
        if node is None:
            return None
        axis = depth % self.k

        if node.point == point:
            if node.right is not None:
                min_node = self.find_min(node.right, axis, depth+1)
                node.point = min_node.point
                node.count = min_node.count
                min_node.count = 1
                node.right = self._delete_recursive(node.right, min_node.point, depth+1)
                if node.right: 
                    node.right.parent = node
            elif node.left is not None:
                min_node = self.find_min(node.left, axis, depth+1)
                node.point = min_node.point
                node.count = min_node.count
                min_node.count = 1
                node.right = self._delete_recursive(node.left, min_node.point, depth+1)
                node.left = None
                if node.right: 
                    node.right.parent = node
            else: 
                return None
            return node

        if point[axis] < node.point[axis]:
            node.left = self._delete_recursive(node.left, point, depth+1)
            if node.left:
                node.left.parent = node
        else:
            node.right = self._delete_recursive(node.right, point, depth+1)
            if node.right:
                node.right.parent = node
        return node


    def rebalance(self):
        items = []
        def _collect(node):
            if node:
                _collect(node.left)
                items.append((node.point, node.count))
                _collect(node.right)
        _collect(self.root)    


        def _build(sub_items, depth=0, parent=None):
            if not sub_items:
                return None
            axis = depth % self.k
            sub_items.sort(key=lambda x: x[axis])
            mid = len(sub_items) // 2
            pt, cnt = sub_items[mid]
            node = Node(pt, axis=axis, parent=parent)
            node.count = cnt
            node.left = _build(sub_items[:mid], depth+1, node)
            node.right = _build(sub_items[mid+1:], depth+1, node)
            return node
        self.root = _build(items)

    def nearest_neighbour(self, query_point):
        best = {"node": None, "dist": float("inf")}    

        def _search(node, depth):
            if node is None:
                return
            dist = math.dist(query_point, node.point)
            if dist < best["dist"]:
                best["dist"] = dist
                best["node"] = node

            axis = depth % self.k
            diff = query_point[axis] - node.point[axis]
            first, second = (node.left, node.right) if diff < 0 else (node.right, node.left)

            _search(first, depth+1)
            if abs(diff) < best["dist"]:
                _search(second, depth+1)

            _search(self.root, 0)
            return best["node"], best["dist"]

    def node_count(self, node=None):
        if node is None:
            node = self.root
        if node is None:
            return 0
        l_count = self.node_count(node.left) if node.left else 0  
        r_count = self.node_count(node.right) if node.right else 0      
        return 1 + l_count + r_count


    def plot_tree(self, query=None, nearest=None):
        if self.root is None:
            print("Árvore vazia")
            return

        fig, (ax_tree, ax_space) = plt.subplots(1, 2, figsize=(16, 7))

        ax_tree.axis('off')
        ax_tree.set_title("Vermelho = X-axis, Azul = Y-axis")

        def draw_tree(node, x, y, spacing):
            if node is None:
                return
            if node.left:
                ax_tree.plot([x, x - spacing], [y, y - 1], color='gray', linewidth=1.2, zorder=1)
                draw_tree(node.left, x - spacing, y - 1, spacing / 2)
            if node.right:
                ax_tree.plot([x, x + spacing], [y, y - 1], color='gray', linewidth=1.2, zorder=1)
                draw_tree(node.right, x + spacing, y - 1, spacing / 2)

            color = "#d62728" if node.axis == 0 else "#1f77b4"
            lbl = f"{node.point[0]},{node.point[1]}" + (f"\n(x{node.count})" if node.count > 1 else "")
            ax_tree.scatter(x, y, s=620, color=color, edgecolors='black', zorder=2)
            ax_tree.text(x, y, lbl, color='white', ha='center', va='center', fontsize=7.5, fontweight='bold', zorder=3)

        draw_tree(self.root, 0, 0, 16)

        ax_space.set_xlim(0, 100)
        ax_space.set_ylim(0, 100)
        ax_space.set_xlabel("X")
        ax_space.set_ylabel("Y")
        ax_space.grid(True, linestyle=':', alpha=0.5)

        def draw_space(node, min_x, max_x, min_y, max_y):
            if node is None:
                return
            px, py = node.point
            if node.axis == 0:
                ax_space.plot([px, px], [min_y, max_y], color='#d62728', linewidth=1.4, alpha=0.8)
                draw_space(node.left, min_x, px, min_y, max_y)
                draw_space(node.right, px, max_x, min_y, max_y)
            else:
                ax_space.plot([min_x, max_x], [py, py], color='#1f77b4', linewidth=1.4, alpha=0.8)
                draw_space(node.left, min_x, max_x, min_y, py)
                draw_space(node.right, min_x, max_x, py, max_y)

            ax_space.scatter(px, py, color='black', s=40, zorder=4)
            ax_space.text(px + 1, py + 1, f"({px},{py})", fontsize=7.5)

        draw_space(self.root, 0, 100, 0, 100)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    tree = KDTree(k=2)

    points = []
    while len(points) < 25:
        pt = (random.randint(5, 95), random.randint(5, 95))
        if pt not in points:
            points.append(pt)

    for p in points:
        tree.insert(p)

    tree.insert(points[0])
    print("Total de nós:", tree.node_count())

    tree.rebalance()
    tree.plot_tree()

    target = (50, 50)
    nearest, dist = tree.nearest_neighbour(target)
    print(f"Mais perto para {target}: {nearest.point} (distance = {dist:.2f})")

  
    for p_rem in points[1:4]:
        print(f"Removendo: {p_rem}")
        tree.delete(p_rem)

    print("Nós após remoção:", tree.node_count())
    tree.plot_tree()
             
    