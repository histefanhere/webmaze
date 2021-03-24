import network
import random

# http://people.uncw.edu/tagliarinig/Courses/380/F2017%20papers%20and%20presentations/The%20Amazing%20Maze--Lawrence,%20Neill,%20and%20Nobles/The%20Amazing%20Maze(1).pdf

n = 20
chance = 0.4

# Firstly generate an n-sized maze of pages
maze = network.Maze()
maze.generate(n)

# This is an algorithm I came up with for generating a simple maze, purely for testing purposes.
# The first loop generates a path of links that's guaranteed to link the starting page to the ending one.
# The second loop then randomly creates links between all other pairs of pages, according to `chance`.
prev = 0
cur = 0
while cur < n - 1:
    cur = min(n - 1, cur + random.randint(1, 3))
    maze.link(prev, cur)
    prev = cur

for i in range(0, n - 2):
    for j in range(i + 1, n - 1):
        if random.random() < chance:
            try:
                maze.link(i, j)
            except network.LinkExistsError:
                pass

# Create the HTML pages
maze.create()
