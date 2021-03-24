import random
import string
import os
import glob
import json

class LinkExists(Exception):
    pass

def get_template(name):
    with open(f"templates/{name}.html", "r") as f:
        return f.read()

class Page:
    def __init__(self, index, code, image, maze):
        self.links = []
        self.index = index
        self.code = code
        self.image = image

        # Store a reference of the master maze object
        self.maze = maze

        if self.index == 0:
            self.filename = "0.html"
        else:
            self.filename = f"{self.code}.html"
    
    def print(self):
        print(f"Page #{self.index}")
        print(f"Links: {self.links}")
    
    def create(self):
        # Generate an html page and plop it into the maze
        if self.index == 0:
            template = get_template('start_page')
        elif self.index == self.maze.get_end().index:
            template = get_template('end_page')
        else:
            template = get_template('middle_page')
        
        template = template.replace("$ID", str(self.index))
        template = template.replace("$IMAGE", str(self.image))

        template = template.replace("$END", str(self.maze.get_end().image))

        random.shuffle(self.links)

        # Create the links list
        link_elements = []
        for link in self.links:
            element = f"<li class=\"link\"><a href=\"{link.filename}\"> <img src=\"things/{link.image}.jpg\"/> </a></li>"
            link_elements.append(element)

        template = template.replace("$LINKS", "\n".join(link_elements))

        with open(f"maze/{self.filename}", "w+") as file:
            file.write(template)

class Maze:
    def __init__(self):
        self.pages = []
        self.size = 0

        # Only for reference, so a code is never repeated
        self.codes = []
        self.images = []

        with open('things.json', 'rb') as file:
            self.image_names = json.load(file)

    def generate(self, n):
        # Generate n different pages
        for _ in range(n):
            self.add_page()

    def add_page(self):
        index = self.size
        code = self.generate_code()
        image = self.generate_image()

        page = Page(index, code, image, self)
        self.pages.append(page)
        self.size += 1
    
    def get_end(self):
        # Return the last node, i.e. the destination
        return self.pages[-1]

    def link(self, ai, bi):
        a = self.pages[ai]
        b = self.pages[bi]
        if b not in a.links:
            a.links.append(b)
            b.links.append(a)
        else:
            raise LinkExists()

    def get_page(self, index):
        return self.pages[index]
    
    def generate_image(self):
        while True:
            image = random.choice(self.image_names)
            if image not in self.images:
                self.images.append(image)
                return image

    def generate_code(self):
        while True:
            code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
            if code not in self.codes:
                self.codes.append(code)
                return code

    def create(self):
        # Delete all files in maze
        files = glob.glob('maze/*.html')
        for f in files:
            os.remove(f)

        for page in self.pages:
            page.create()
