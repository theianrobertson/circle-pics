"""
Code for creating neato circle images

Made by Ian
"""

import math
import os
import datetime
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter

#Config in here, could be split out eventually
LINE_COLOUR = (0, 0, 0)
START_RADIUS = 60
STEP_DISTANCE_RATIO = 0.4
GROW_PER_LOOP = 30
IMAGE_SIZE = (3000, 3000)
STANDARD_WIDTH = 5
WIDTH_MULTIPLIER = 3
WIDTH_ADDER = 3

def centre_to_zeroes(cartesian_point, centre_point):
    """Converts centre-based coordinates to be in relation to the (0,0) point.

    PIL likes to do things based on (0,0), and in this project I'd like to keep
    the origin at the centre point.

    Parameters
    ----------
    cartesian_point : (numeric)
        x, y coordinates in terms of the centre
    centre_point : (numeric)
        x, y coordinates of the centre
    """
    x = cartesian_point[0] + centre_point[0]
    y = centre_point[1] - cartesian_point[1]
    return x, y


class Point(object):
    """Point object, with methods to change from polar to cartesian and back.

    When constructing, either provide radius & angle, or x & y (cartesian, with
    centre at the centre of the image)

    Parameters
    ----------
    radius : numeric
        The radius of the point in polar coordinates
    angle : numeric
        Angle of the point in polar coords, in radians (0 - 2π)
    x : numeric
        x coordinate in cartesian plane
    y : numeric
        y coordinate in cartesian plane
    """
    def __init__(self, radius=None, angle=None, x=None, y=None):
        self.radius = radius
        self.angle = angle
        if radius is not None and angle is not None:
            pass
        elif x is not None and y is not None:
            self.radius, self.angle = self.to_polar(x, y)
        else:
            raise ValueError('give me coords plz')

    def to_cartesian(self, to_int=False):
        """Convert polar coordinates to cartesian

        Parameters
        ----------
        to_int : bool
            Whether to round to closest integers

        Returns
        (numeric, numeric)
            The cartesian coordinates
        """
        x = self.radius * math.cos(self.angle)
        y = self.radius * math.sin(self.angle)
        if to_int:
            return (int(round(x, 0)), int(round(y, 0)))
        else:
            return (x, y)

    def to_polar(self, x=None, y=None):
        """Convert cartesian coordinates to polar, or just return the stored
        polar coordinates

        Parameters
        ----------
        x : numeric
            A numeric cartesian x-axis coordinate
        y : numeric
            Numeric cartesian y-axis coordinate

        Returns
        -------
        (numeric, numeric)
            The polar coordinates (angle in radians)
        """
        if self.radius is not None and self.angle is not None:
            return (self.radius, self.angle)
        radius = math.sqrt(x ** 2 + y ** 2)
        angle = math.atan2(y, x)
        return (radius, angle)


class Drawing(object):
    """The drawing is an instance of this class"""
    def __init__(self):
        self.image = None
        self.draw = None
        self.centre = None
        self.create_image()
        self.line_fill = LINE_COLOUR
        self.current_radius = START_RADIUS
        self.step_distance_ratio = STEP_DISTANCE_RATIO
        self.grow_per_loop = GROW_PER_LOOP
        self.prev_point = Point(START_RADIUS, 0)
        self.base_image = None

    def create_image(self):
        """Set up the blank slate - currently full of magic numbers."""
        self.image = PIL.Image.new('RGB', IMAGE_SIZE, 'white')
        self.draw = PIL.ImageDraw.Draw(self.image)
        self.centre = (int(self.image.size[0] / 2), int(self.image.size[1] / 2))

    def get_width(self, point):
        """Gets the width to use at a certain point in the picture.  Also has
        some magic numbers.

        Parameters
        ----------
        point : Point
            The point object

        Returns
        -------
        int
            Integer width of a line to use
        """
        if self.base_image is None:
            return 5
        else:
            pil_point = centre_to_zeroes(
                point.to_cartesian(to_int=True), self.centre)
            base_pixel = self.base_image.getpixel(pil_point)
            reversed_pixel = abs(base_pixel - 255)
            return int(reversed_pixel / 32) * WIDTH_MULTIPLIER + WIDTH_ADDER


    def add_base_image(self, filename):
        """Add in a base image to be mapped to the circles
        
        Parameters
        ----------
        filename : str
            Filename of the image file to use
        """
        img = PIL.Image.open(filename)
        scale_ratio = float(max(self.image.size)) / max(img.size)
        new_size = (
            int(scale_ratio * img.size[0]), int(scale_ratio * img.size[1]))
        scaled_img = img.resize(new_size, PIL.Image.ANTIALIAS)

        paste_x1 = int(self.image.size[0] / 2 - new_size[0] / 2)
        paste_y1 = int(self.image.size[1] / 2 - new_size[1] / 2)
        paste_x2 = int(paste_x1 + new_size[0])
        paste_y2 = int(paste_y1 + new_size[1])

        blank_image = PIL.Image.new('RGB', (self.image.size), 'white')
        blank_image.paste(
            scaled_img, (paste_x1, paste_y1, paste_x2, paste_y2))

        self.base_image = blank_image.convert('L')

    def run_loops(self, loop_count):
        """Run a bunch of loops

        Parameters
        ----------
        loop_count : int
            The number of loops to loop around before stopping
        """
        for _ in range(loop_count):
            self.loop()

    def loop(self):
        """Run one loop of the image drawing process"""
        steps = int(
            self.current_radius * math.pi * 2 * self.step_distance_ratio)
        angle_step = 2 * math.pi / steps
        radius_step = self.grow_per_loop / steps
        for i in range(steps):
            self.current_radius += radius_step
            this_point = Point(self.current_radius, i * angle_step)
            this_pil = centre_to_zeroes(
                this_point.to_cartesian(to_int=True), self.centre)
            prev_pil = centre_to_zeroes(
                self.prev_point.to_cartesian(to_int=True), self.centre)
            self.draw.line(
                [this_pil, prev_pil],
                fill=self.line_fill, width=self.get_width(this_point))
            self.prev_point = this_point

    def save(self, filename=None, resize=None, blur=None):
        """Save to a png file

        Parameters
        ----------
        filename : str
            Optional filename - will default to a date and file pattern.
        resize : (numeric, numeric)
            Optional size to resize to
        """
        if not filename:
            filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename += '_output.png'
            filename = os.path.join('test_outputs', filename)

        if blur:
            self.image = self.image.filter(
                PIL.ImageFilter.GaussianBlur(radius=blur))

        if resize:
            image_small = self.image.resize(resize, PIL.Image.ANTIALIAS)
            image_small.save(filename)
        else:
            self.image.save(filename)

def test_run():
    drawing = Drawing()
    drawing.add_base_image('inputs/audrey.png')
    drawing.run_loops(45)
    drawing.save(resize=(1000, 1000), blur=1)

if __name__ == '__main__':
    test_run()