import network
import random

# http://people.uncw.edu/tagliarinig/Courses/380/F2017%20papers%20and%20presentations/The%20Amazing%20Maze--Lawrence,%20Neill,%20and%20Nobles/The%20Amazing%20Maze(1).pdf

maze = network.Maze()

n = 20
chance = 0.4

maze.generate(n)

# make sure the start and end are connected
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
            except network.LinkExists:
                pass

# maze.link(0, 1)

maze.create()
