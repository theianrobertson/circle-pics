"""
Code for creating neato circle images

Made by Ian
"""

import sys
import logging
import math
import os
import random
import datetime
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter

#Config in here, could be split out eventually
LINE_COLOUR = (0, 0, 51)
START_RADIUS = 60
#STEP_DISTANCE_RATIO = 0.4
STEP_DISTANCE_RATIO = 0.1
GROW_PER_LOOP = 35
IMAGE_SIZE = (3000, 3000)
STANDARD_WIDTH = 5
WIDTH_MULTIPLIER = 3
WIDTH_ADDER = 3
MAX_JITTER = 1

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


def jitter():
    """Adds some random jitters to a radius"""
    return random.choice(range(-MAX_JITTER, MAX_JITTER))


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
        self.point_array = []
        self.zero_radius = START_RADIUS

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
        previous_steps = 0
        for cnt in range(loop_count):
            print('Running loop ' + str(cnt))
            self.zero_radius = self.current_radius
            previous_steps = self.loop(previous_steps)

    def loop(self, previous_steps=0):
        """Run one loop of the image drawing process"""
        steps = int(
            self.current_radius * math.pi * 2 * self.step_distance_ratio)
        angle_step = 2 * math.pi / steps
        radius_step = self.grow_per_loop / steps
        for i in range(steps):
            #prev_radius = self.get_previous_radius(i * angle_step)
            if previous_steps > 0:
                to_subtract = i + int(previous_steps * (1 - (i / steps)))
                prev_radius = self.point_array[-to_subtract].radius
                #print(prev_radius)
                self.current_radius = prev_radius + self.grow_per_loop + jitter()
            else:
                self.current_radius += radius_step
            #if i == 0:
            #    self.current_radius = self.zero_radius + self.grow_per_loop
            this_point = Point(self.current_radius, i * angle_step)
            this_pil = centre_to_zeroes(
                this_point.to_cartesian(to_int=True), self.centre)
            prev_pil = centre_to_zeroes(
                self.prev_point.to_cartesian(to_int=True), self.centre)
            self.draw.line(
                [this_pil, prev_pil],
                fill=self.line_fill, width=self.get_width(this_point))
            self.prev_point = this_point
            self.point_array.append(this_point)
            #print(previous_steps, i, this_point.to_polar())
        return steps

    def get_previous_radius(self, angle):
        """Get the previous radius "close" to an angle"""
        prev_points = self.point_array.copy()
        prev_points_greater = [p for p in prev_points if p.angle > angle]
        if prev_points_greater:
            return prev_points_greater[-1].radius
        else:
            return None


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

def run(image, loops=None, output_size=None):
    """Run the generation process on an image
    
    Parameters
    ----------
    image : str
        Filename of the image file
    loops : int, optional
        How many loops in the output image
    output_size : tuple, optional
        Size to scale the output to
    """
    if loops is None:
        loops = 20
    if output_size is None:
        output_size = (1000, 1000)
    drawing = Drawing()
    drawing.add_base_image(image)
    drawing.run_loops(loops)
    drawing.save(resize=output_size, blur=1)

if __name__ == '__main__':
    image = sys.argv[1]
    loops = None
    output_size = None
    try:
        loops = int(sys.argv[2])
        output_size = (int(sys.argv[3]), int(sys.argv[4]))
    except IndexError:
        pass
    run(image, loops, output_size)
