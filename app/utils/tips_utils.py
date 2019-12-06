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
    "Abstract method can be implemented in the abstract base class. But this is not good design",
    """Easy way to get few maximum or minimum elements from the list is to use heapq
        import heapq
        nums = [1, 8, 2, 23, 7, 10]
        heapq.nlargest(3, nums)
        heapq.nsmallest(3, nums)
    """,

    "When writing context manager, remember that __exit__ needs 4 arguments, __self__(self, exc_ty, exc_cal, tb)",
    """To read configuration files in .ini format, you don't need regex, simply use configparser module
        from configparser import ConfigParser
        cfg = ConfigParser()
        cfg.read('config.ini')
    """,

    """Async on generator could be implemented in the following way
    def out(num):
        while True:
            ou = (yield)
            if ou:                
                print(num**ou)  


    b = out(2) # we create generator, num = 2, we cannot use it 
    b.__next__() # now we can use generator, we  need second argument
    b.send(3)   # now we pass second argument and get result 2**3 = 8
    """,

    """Besides default split method, which works from left to right, maybe faster to search last element in string
    string = '127.0.0.1 - ... "GET /ply/ply.html HTTP/1.1" 200 97238'
    bytes = string.rsplit(None, 1)[1]
    """,

    """Easy regex to get list of hashtags from the string
    re.findall(r'\#\w+', hashtag_string)
    """,


]

print(len(tips))


def get_random_tip():
    rand = random.randint(0, len(tips) -1)
    return tips[rand]
