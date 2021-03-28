#!/usr/bin/env python3

# This can be removed from python 3.10+
from __future__ import annotations

import random
import string
import os
import glob
import json

from typing import Any

class LinkExistsError(Exception):
    """Exception raised when a link is tried to be made between two pages who already have a link between them.

    Args:
        a (Page): first page.
        b (Page): second page.
    """

    def __init__(self, a: Page, b: Page):
        self.message = "A link already exists between pages {} and {}".format(
            a.index,
            b.index
        )
        super().__init__(self.message)

class Page:
    """A page in the webmaze.
    
    Each page of the webmaze can be thought of as a node in a network graph,
    with many links to other pages in the network.

    Args:
        index: The index of the page and its (internal) identifier.
        code: A random string used as the page's filename.
        image: The name of the image used for the page.
        maze (Maze): A reference to the master maze object.
    
    Attributes:
        links (list[Page]): A list of all the page's links.
        index (int): The index of the page and its (internal) identifier.
        code (str): A random string used as the page's filename.
        image (str): The name of the image used for the page.
        maze (Maze): A reference to the master maze object.
        filename (str): The page's future filename, generated from it's code.
    """
    
    def __init__(self, index: int, code: str, image: str, maze: Maze):
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
    
    def link(self, other: Page) -> None:
        """Link one page to another.

        This does some error checking to make sure it's a valid link,
        and if it is it updates each page's links accordingly.

        Args:
            other: The other page to link to.
        
        Raises:
            LinkExistsError: A link already exists between pages a and b.
        """
        if other is self:
            raise ValueError(f"Cannot link page {self.index} to itself")
        elif other in self.links:
            raise LinkExistsError(self, other)
        else:
            self.links.append(other)
            other.links.append(self)
    
    def create(self, position: str):
        """Generate an HTML file for the page."""
        random.shuffle(self.links)
        link_elements = []
        for link in self.links:
            element = self._get_template('link',
                filename=link.filename,
                image=link.image
            )
            link_elements.append(element)

        content = self._get_template(position + "_page",
            id=self.index,
            image=self.image,
            end=self.maze.get_end().image,
            links="\n".join(link_elements)
        )

        with open(f"maze/{self.filename}", "w+") as file:
            file.write(content)

    def _get_template(self, name: str, **kwargs: Any) -> str:
        """A utility function for automating the HTML template process.

        This function when given a name, will return the content from that template file.
        It will also fill the template variables from all key-value argument pairs passed to it.

        Args:
            name (str): name of template file
            **kwargs: key-value pairs of the substitutions that will be made.
        
        Returns:
            File content with substitutions made.
        """
        with open(f"templates/{name}.html", "r") as f:
            content = f.read()
        
        for key, value in kwargs.items():
            content = content.replace(f"${key.upper()}", str(value))
        
        return content


class Maze:
    """Object representing the whole maze. 

    This handles everything to do with managing the network of pages (nodes).

    Attributes:
        size (int): Number of pages in the maze.
        pages (list[Page]): A list of all the pages in the network.
        image_names (list[str]): List of all available image names.
    """

    def __init__(self, size: int):
        self.pages = []
        self.size = size

        # Only for reference, so a code or image is never repeated
        self._codes = []
        self._images = []

        with open('things.json', 'rb') as file:
            self.image_names = json.load(file)

            random.shuffle(self.image_names)
        
        self._generate()
    
    def get_page(self, index: int) -> Page:
        """Return the page at index."""
        return self.pages[index]

    def get_end(self) -> Page:
        """Return the last node, i.e. the destination."""
        return self.get_page(-1)

    def link(self, ai: int, bi: int) -> None:
        """Link two differnet pages together.

        Each page gets a copy of the other in their links attributes.

        Args:
            ai: Index of the first node to link.
            bi: Index of the second node to link.

        Raises:
            LinkExistsError: A link already exists between pages a and b.
        """
        self.pages[ai].link(self.pages[bi])
        
    def create(self) -> None:
        """Create the HTML maze.

        This method will delete all existing HTML files from `maze` and create a new maze
        based on the maze's pages and their links.
        """
        # First, delete any old HTML files from the maze
        files = glob.glob('maze/*.html')
        for f in files:
            os.remove(f)

        # Now tell each page to create their individual pages
        self.pages[0].create('start')
        for page in self.pages[1:-1]:
            page.create('middle')
        self.pages[-1].create('end')
    
    def _generate(self) -> None:
        """Generate n different pages.

        Here we handle things like making sure each page has a unique
        code and image assigned to them.
        """
        for i in range(self.size):
            code = self._generate_code()
            image = self._generate_image()

            page = Page(i, code, image, self)
            self.pages.append(page)
    
    def _generate_image(self) -> str:
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

    def _generate_code(self) -> str:
        """Return a randomized code that hasn't been chosen till now.

        The code is a random string consisting of letters and digits that are URL
        compatible. It will also be stored so that it never gets repeated. This
        method should only be called when creating a new page.

        Returns:
            A unique code.
        """
        code_length = 8
        while True:
            code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(code_length))
            if code not in self._codes:
                self._codes.append(code)
                return code
