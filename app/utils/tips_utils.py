import random

tips = [
    "In Python 3 there is no xrange. The range has default implementation of xrange",
    "In Python 3 you can write fstring like format like `f'messages is {self.message}'`",
    "`import math` is significantly slower than `from math import pi` cause there is no lookup",
    "instance methods can access class itself throught the self.__class__ attribute",
    "static method cannot modify class or instance, they are util methods, premarilly a way to namespace your methods",
    "Big O is called `order of magnitude`  and means approximation to the actual number of steps in the computation",
    "first-in-first-out data structure called a queue",
    "A balanced binary tree has roughly the same number of nodes in the left and right subtrees of the root",
    "Abstract method can be implemented in the abstract base class. But this is not good design"
]


def get_random_tip():
    rand = random.randint(0, len(tips) -1)
    return tips[rand]
