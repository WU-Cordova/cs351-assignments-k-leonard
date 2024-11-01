
# this is a thiing that allows the code to be compatible between versions
from __future__ import annotations
# I HAVE NO IDEA WHAT THIS IS FOR, was here when i did my most recent pull
from typing import Callable, Generic, List, Optional, Sequence, Tuple
# This pulls from the other file called iavltree
from datastructures.iavltree import IAVLTree, K, V
#----------------------------------------------------------------------------------------------------------
""" 
This is the actual AVLNode class, where a node is a like a spot on the tree. This class takes in a key and value pair.
"""
# creating a class for our AVL nodes, which take a generic (aka not specific) key and value pairs.
class AVLNode(Generic[K, V]):

    def __init__(self, key: K, value: V, left: Optional[AVLNode] = None, right: Optional[AVLNode] = None):

        self._key = key  # Initializing the key of the node
        self._value = value  # Initializing the value of the node
        self._left = left  # Initializing the left child
        self._right = right  # Initializing the right child
        self._height = 1  # Setting the initial height of the node
#-------------------------------------------------------------------------------------------------------------------
    @property
    def key(self) -> K:  # Defining a getter for the key
        return self._key
#-----------------------------------------------------------------------------------------------------------------------
    @key.setter
    def key(self, new_key: K) -> None:  # setter for the key
        self._key = new_key
#-----------------------------------------------------------------------------------------------------------------------
 # LC: Added these to help with debugging
    def __str__(self) -> str:
        output = f'K: {self._key} V: {self._value} Height: {self._height}'
        output += ' L: ' +  f'{self._left._key}' if self._left else 'None'
        output += ' R: ' + f'{self._right._key}' if self._right else 'None'

        return output
#-----------------------------------------------------------------------------------------------------------------------
    # LC: Added these to help with debugging
    def __repr__(self) -> str:
        return str(self)
#-----------------------------------------------------------------------------------------------------------------------
class AVLTree(IAVLTree[K, V], Generic[K, V]):

    def __init__(self, starting_sequence: Optional[Sequence[Tuple]] = None):

        # LC: just added type hint Optional
        self._root: Optional[AVLNode] = None  # initalizes the root
        self._size = 0  # initalizes the size

        if starting_sequence:  # if starting pair(?) is provided put those in
            for key, value in starting_sequence:
                self.insert(key, value)
#-----------------------------------------------------------------------------------------------------------------------
# How we insert key value pairs into the tree, is really just a pretty name while the helper function does all of the work
    def insert(self, key: K, value: V) -> None:
        self._root = self.insert_helper(self._root, key, value)
#-----------------------------------------------------------------------------------------------------------------------
    # LC: Added two helper functions to make getting the node height and balance
    # factors less verbose when you need them in the insert code.

    def _node_height(self, node: Optional[AVLNode]) -> int:
        return node._height if node else 0

#-----------------------------------------------------------------------------------------------------------------------
    def _balance_factor(self, node: AVLNode) -> int:
        return self._node_height(node._left) - self._node_height(node._right) if node else 0
#-----------------------------------------------------------------------------------------------------------------------
    def insert_helper(self, node: Optional[AVLNode], key: K, value: V) -> AVLNode:

        if node is None:  # if the current node is empty, make one!

            return AVLNode(key, value)

        elif key < node.key:  # if a node exists, and the key is less than the current node's key, THEN insert into the left subtree

            node._left = self.insert_helper(node._left, key, value)

        else:  # In everyother case in which the node exists, put it into the right side of the tree
            node._right = self.insert_helper(node._right, key, value)


        # LC: Changing to use the _node_height() function
        max_height = max(self._node_height(node._left),
                         self._node_height(node._right))

        node._height = 1 + max_height

        # I'm hoping that this is balancing the tree

        # left heavy case?

        # if the left node exists, if it doesn't return 0, but if it does, get the height and then subtract the height of the right side (if it exists), and if that is greater than 1, its unbalanced to the left
    # -------------------------------------------------------------------------------
        # LL Problem

        # if (node._left._height if node._left else 0) - (node._right._height if node._right else 0) > 1:
        # LC: Rewriting the LL case to use the balance_factor() function
        if self._balance_factor(node) > 1 and node._left and self._balance_factor(node._left) >= 0:
            return self.rotate_right(node)

            # left_child = node._left  # assign left_child to be the left,node
            # right_child = node._right  # assign the right child ot be the right.nod

            # # if the left.node exists, get the height of the tree to the left of the child and subtract thhe height of the tree to the right of the left child, and if that is greaters than or equal to 0, then we need to flip
            # if (left_child._left._height if node._left else 0) - (left_child._right._height if node._right else 0) >= 0:
            #     return self.rotate_right(node)  # we do a rotate right
    # -------------------------------------------------------------------------------
        # RR case

        # LC: Rewriting the RR case to use the balance_factor() function
        if self._balance_factor(node) < -1 and node._right and self._balance_factor(node._right) <= 0:
            return self.rotate_left(node)

        # if (node._left._height if node._left else 0) - (node._right._height if node._right else 0) < -1:

        #     # we assign the left child to be the things to left of our given node
        #     left_child = node._left

        #     # we assign the right child to be the thing to the right of our given node
        #     right_child = node._right

        #     # if there is something to the left of the main node, look to the right child and get the height of the tree to the left, and then do that same thing to the right side, and subtract the values, and if that value is less than or equal to 0

        #     if (right_child._left._height if node._left else 0) - (right_child._right._height if node._right else 0) <= 0:

        #         return self.rotate_left(node)  # rotate left
    # -------------------------------------------------------------------------------
        # LR Case
        # LC: Rewriting the LR case to use the balance_factor() function
        if self._balance_factor(node) > 1 and node._left and self._balance_factor(node._left) < 0:
            node._left = self.rotate_left(node._left)
            return self.rotate_right(node)

        # RL case
        # LC: Rewriting the RL case to use the balance_factor function()
        if self._balance_factor(node) < -1 and node._right and self._balance_factor(node._right) > 0:
            node._right = self.rotate_right(node._right)
            return self.rotate_left(node)

            # if the value is not less than or equal to zero, rotate right
            # if (node._left._height if node._left else 0) - (node._right._height if node._right else 0) > 0:
            #     node.__right = self.rotate_right(right_child)

            #     return self.rotate_left(node)

        # LC: no rotations needed
        return node
#-----------------------------------------------------------------------------------------------------------------------
    # defining the rotating right function, which is how we adjust unbalanced trees
    def rotate_right(self, node: AVLNode) -> AVLNode:

        # take the thing to the left of our given node and call it the left child
        new_root = node._left

        # LC: Putting an assertion here to ensure this doesn't happen
        if not new_root:
            raise Exception("new_root should not be None")

        # take the thing to the right of our left child, and call it the subtree
        right_subtree = new_root._right
        # our given node will now because the thing to the right of our left child
        new_root._right = node

        # and now the thing we called our subtree (aka the node ot the right of our left child) and that is now becoming the thing to the left of our given node
        node._left = right_subtree

        node._height = 1 + max(  # this gets the height relative to the given node by looking to the left and right, getting their heights and then picking the max

            # LC: changed to use _node_height() function
            self._node_height(node._left),
            self._node_height(node._right)
        )

        new_root._height = 1 + max(  # this is finding the height of the left side, children and all by getting the heights if the left and right children and then getting the one thats the tallest

            # LC: changed to use _node_height() function
            self._node_height(new_root._left),
            self._node_height(new_root._right)
        )

        return new_root
#-----------------------------------------------------------------------------------------------------------------------
    def rotate_left(self, node: AVLNode) -> AVLNode:  # basically the same as above

        new_root = node._right

        # LC: Putting an assertion here to ensure this doesn't happen
        if not new_root:
            raise Exception("new_root should not be None")

        new_left_subtree = new_root._left

        # LC: this should set new_root._left to node because that's the new left
        new_root._left = node
        node._right = new_left_subtree

        # LC: changed to use _node_height_function.
        node._height = 1 + max(self._node_height(node._left), self._node_height(node._right))

        # LC: changed to use _node_height_function.
        new_root._height = 1 + max(self._node_height(new_root._left), self._node_height(new_root._right))

        return new_root
#-----------------------------------------------------------------------------------------------------------------------
# a fuction that sits pretty until it gets called
    def search(self, key: K) -> V | None:
        return self.search_helper(self._root, key)
#-----------------------------------------------------------------------------------------------------------------------
# a helper function that does all of the actual work
    def search_helper(self, node: Optional[AVLNode], key: K) -> Optional[V]:

        if node is None:  # if nothing is given, obviously we can't tell if it exists or not so return none

            return None

        elif node._key == key:  # if the key belonging to a node matches the key we are looking for, return the value associated with the key because we found it

            return node._value

        # if the key we are a looking for is less than our level 0 node, then the node we are looking for is to the left (if everything works), so go down the left side
        elif key < node._key:

            # call the function again, to check and see if the node we landed on is the one associated with the key,
            self.search_helper(node._left, key)

        else:  # if the node isn't what we are looking for, and isn't less than the node, than it must be larger, so we look to the right and call the search function again to see if the node we landed on is the one we are looking for

            self.search_helper(node._right, key)
#-----------------------------------------------------------------------------------------------------------------------
# pretty helper function that calls the helper

    def delete(self, key: K) -> None:

        self.root = self.delete_helper(self.root, key)
# thea single helper function that works to two jobs, loves its kids and never stops!

#-----------------------------------------------------------------------------------------------------------------------
    def delete_helper(self, node: Optional[AVLNode], key: K) -> AVLNode | None:

        if node is None:  # if the node given doesn't exist, scream
            raise KeyError(f"Key {key} not found in the tree.")

        elif key < node.key:  # if the key is less than the given node key, we need to go to the left of the node and check for the node
            node._left = self.delete_helper(node._left, key)

        elif key > node.key:  # if the key is greater than the given node, then we need to go to the right and check there for our target
            node._right = self.delete_helper(node._right, key)

        else:  # if we have found the node
            if node._left is None and node._right is None:  # if the node has no children
                return None  # do nothing

            elif node._left is None:  # if the parent node doesn't havef a left child,make the right child the main node
                node = node._right

            elif node._right is None:  # if the parent node doesn't have a right child, make the left child the main node
                node = node._left

            else:
                # find the minimum successor
                successor = self.find_min(node._right)
                node._key = successor.key  # replacing the the node key with the key of the sucessor
                
                # replacing the node value with the value of the sucessor
                node._value = successor.value
                node._right = self.delete_helper(
                    node._right, successor._key)  # delete the sucessor

        # update the height of our tree

        node.height = 1 + max(node._left._height if node._left else 0,
                          node._right._height if node._right else 0) - 1

        # check the tree to see if its unbalanced

        # checking to see if its balanced, and if the heights are greater than one
        if (node._left._height if node._left else 0) - (node._right._height if node._right else 0) > 1:
            left_child = node._left  # then label the children
            right_child = node._right

            # and if the height of the left child is greater than the rights, then we need to rotate
            if (left_child._left._height if left_child._left else 0) - (left_child._right._height if left_child._right else 0) >= 0:
                return self.rotate_right(node)
            else:  # if the right child is taller than the left, rotate
                node._left = self.rotate_left(left_child)
                return self.rotate_right(node)

        elif (node._left._height if node._left else 0) - (node._right._height if node._right else 0) < -1:
            left_child = node._left
            right_child = node._right

            # if the tree is unbalanced the other way, correct it!
            if (right_child._left._height if right_child._left else 0) - (right_child._right._height if right_child._right else 0) <= 0:
                return self.rotate_left(node)
            else:
                node._right = self.rotate_right(right_child)
                return self.rotate_left(node)

        return node

     # this SHOULD (emphasis on should) find the smallest key in the tree
#-----------------------------------------------------------------------------------------------------------------------
    def find_min(self, node: AVLNode) -> AVLNode:
        # go to the leftmost node (which if the tree is formatted correctly should be the smallest)
        while node._left is not None:
            node = node._left  # assign this leftmost node to the given node
        return node

     # this is AN attempt at traversing an AVL tree in order
#-----------------------------------------------------------------------------------------------------------------------
    def inorder(self, visit: Optional[Callable[[V], None]] = None) -> List[K]:
        keys = []  # this collects the keys for later reference
        self.inorder_helper(self._root, keys)
        return keys

     # the helper that does all the work, kind of
#-----------------------------------------------------------------------------------------------------------------------
    def inorder_helper(self, node: Optional[AVLNode], keys: List[K]) -> None:
        if node is None:  # base case, nothing exists
            return None

        # visit the left tree and put stuff there
        self.inorder_helper(node._left, keys)

        keys.append(node._key)  # go back to the given node

        # go down the right side and put nodes there
        self.inorder_helper(node._right, keys)
#-----------------------------------------------------------------------------------------------------------------------
# trying to preorder stuff like its limited edition

    def preorder(self, visit: Optional[Callable[[V], None]] = None) -> List[K]:
        keys = []  # collecting keys
        self.preorder_helper(self._root, keys)
        return keys

     # the helper that does all the work
#-----------------------------------------------------------------------------------------------------------------------
    def preorder_helper(self, node: Optional[AVLNode], keys: List[K]) -> None:
        if node is None:  # base case is that nothing is anywhere ever
            return None

        keys.append(node._key)  # go to the given node

        self.preorder_helper(node._left, keys)  # go down the left tree
        self.preorder_helper(node._right, keys)  # go down the right tree
#-----------------------------------------------------------------------------------------------------------------------
# post order stuff

    def postorder(self, visit: Optional[Callable[[V], None]] = None) -> List[K]:
        keys = []  # KEYS ARE MINE
        self.postorder_helper(self._root, keys)
        return keys
#-----------------------------------------------------------------------------------------------------------------------
# the post order helper

    def postorder_helper(self, node: Optional[AVLNode], keys: List[K]) -> None:
        if node is None:  # your classic base case
            return None

        # we literally just go the opposite way of the pre-order
        self.postorder_helper(node._left, keys)
        self.postorder_helper(node._right, keys)

        keys.append(node._key)
#-----------------------------------------------------------------------------------------------------------------------
# Breadth-first attempt

    def bforder(self, visit: Optional[Callable[[V], None]] = None) -> List[K]:
        keys = []  # a list for keys
        queue = []  # a queue
        self.bforder_helper(queue, self._root, keys)
        return keys
#-----------------------------------------------------------------------------------------------------------------------
# the helper helper helper helper , help helper and help aren't words anymore

    def bforder_helper(self, queue:  List[Optional[AVLNode]], node: Optional[AVLNode], keys: List[K]) -> None:
        if node is not None:  # if the node exists, append it to the list
            queue.append(node)
        
        while queue:  # while the list is a thing, run
            current = queue[0]  # take the first node
            keys.append(current._key)  # visit the current node
            queue = queue[1:]  # Remove the first node from the list
            
            if current._left is not None:  # put the left child, if it exists, into the list
                queue.append(current._left)
            if current._right is not None:  # put the right child, if it exists, into the list
                queue.append(current._right)

     # should return the size of the tree
#-----------------------------------------------------------------------------------------------------------------------
    def size(self) -> int:
        return self.size_helper(self.root)

     # helper function for size of tree
#-----------------------------------------------------------------------------------------------------------------------
    def size_helper(self, node: Optional[AVLNode]) -> int:
        if node is None:  # if nothing exists, return 0
            return 0

        # Count current node and children
        return 1 + self.size_helper(node._left) + self.size_helper(node._right)

    # LC: added to help with debugging
#-----------------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        def draw_tree(node: Optional[AVLNode], level: int = 0) -> None:
            if not node:
                return
            draw_tree(node._right, level + 1)
            level_outputs.append(f'{" " * 4 * level} -> {str(node._value)}')
            draw_tree(node._left, level + 1)
        level_outputs: List[str] = []
        draw_tree(self._root)
        return '\n'.join(level_outputs)
#-----------------------------------------------------------------------------------------------------------------------
    # LC: added to help with debugging
    def __repr__(self) -> str:
        descriptions = ['Breadth First: ',
                        'In-order: ', 'Pre-order: ', 'Post-order: ']
        traversals = [self.bforder(), self.inorder(),
                      self.preorder(), self.postorder()]
        return f'{"\n".join([f'{desc} {"".join(str(trav))}' for desc, trav in zip(descriptions, traversals)])}\n\n{str(self)}'
        