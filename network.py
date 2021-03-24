import random
import string
import os
import glob
import json

class LinkExists(Exception):
    pass

def get_template(name):
    """Return the file path & name of an html template file."""
    with open(f"templates/{name}.html", "r") as f:
        return f.read()

class Page:
    """A page in the webmaze.
    
    Each page of the webmaze can be thought of as a node in a network graph,
    with many links to other pages in the network.

    Args:
        index (int): The index of the page and its (internal) identifier.
        code (str): A random string used as the page's filename.
        image (str): The name of the image used for the page.
        maze (Maze): A reference to the master maze object.
    
    Attributes:
        links (list[Page]): A list of all the page's links.
        index (int): The index of the page and its (internal) identifier.
        code (str): A random string used as the page's filename.
        image (str): The name of the image used for the page.
        maze (Maze): A reference to the master maze object.
        filename (str): The page's future filename, generated from it's code.
    """
    
    def __init__(self, index, code, image, maze):
        self.links = []
        self.index = index
        self.code = code
        self.image = image

        # Store a reference of the master maze object
        self.maze = maze

        # Figure out the filename of the page based on our code (set to `0.html` if this page is the first)
        if self.index == 0:
            self.filename = "0.html"
        else:
            self.filename = f"{self.code}.html"
    
    def print(self):
        print(f"Page #{self.index}")
        print(f"Links: {self.links}")
    
    def create(self):
        """Generate an HTML file for the page."""
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
    """Object representing the whole maze. 

    This handles everything to do with managing the network of pages (nodes).

    Attributes:
        size (int): Number of pages in the maze.
        pages (list[Page]): A list of all the pages in the network.
        image_names (list[str]): List of all available image names.
    """

    def __init__(self):
        self.pages = []
        self.size = 0

        # Only for reference, so a code or image is never repeated
        self._codes = []
        self._images = []

        with open('things.json', 'rb') as file:
            self.image_names = json.load(file)

            random.shuffle(self.image_names)

    def generate(self, n):
        """Generate n different pages.

        Here we handle things like making sure each page has a unique
        code and image assigned to them.
        """

        for _ in range(n):
            index = self.size
            code = self._generate_code()
            image = self._generate_image()

            page = Page(index, code, image, self)
            self.pages.append(page)
            self.size += 1
    
    def get_page(self, index):
        """Return the page at index."""
        return self.pages[index]

    def get_end(self):
        """Return the last node, i.e. the destination."""
        return self.get_page(-1)

    def link(self, ai, bi):
        """Link two differnet pages together.

        Each page gets a copy of the other in their links attributes.

        Args:
            ai (int): Index of the first node to link.
            bi (int): Index of the second node to link.

        Raises:
            LinkExists: A link already exists between pages a and b.
        """
        if ai == bi:
            raise ValueError("Cannot link a page to itself")
        a = self.pages[ai]
        b = self.pages[bi]
        if b not in a.links:
            a.links.append(b)
            b.links.append(a)
        else:
            raise LinkExists()
    
    def create(self):
        """Create the HTML maze.

        This method will delete all existing HTML files from `maze` and create a new maze
        based on the maze's pages and their links.
        """
        # First, delete any old HTML files from the maze
        files = glob.glob('maze/*.html')
        for f in files:
            os.remove(f)

        # Now tell each page to create their individual pages
        for page in self.pages:
            page.create()
    
    def _generate_image(self):
        """Return a random image name that hasn't been chosen till now.

        The image name will also be stored so that it never gets repeated. This
        method should only be called when creating a new page.
        
        Returns:
            A unique image name.
        """
        while True:
            image = random.choice(self.image_names)
            if image not in self._images:
                self._images.append(image)
                return image

    def _generate_code(self):
        """Return a randomized code that hasn't been chosen till now.

        The code is a random string consisting of letters and digits that are URL
        compatible. It will also be stored so that it never gets repeated. This
        method should only be called when creating a new page.

        Returns:
            A unique code.
        """
        while True:
            code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
            if code not in self._codes:
                self._codes.append(code)
                return code
