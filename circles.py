"""
Code for creating circle images
"""

import math
import os
import datetime
import PIL.Image
import PIL.ImageDraw


class Point(object):
    """Point object, with methods to change from polar to cartesian and back"""
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
        round : bool
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
        """Convert cartesian coordinates to polar

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

def centre_to_zeroes(cartesian_point, centre_point):
    """Converts centre-based coordinates to be in relation to the (0,0) point

    Parameters
    ----------
    cartesian_point : (numeric)
        x, y coordinates in terms of the centre
    centre_point : (numeric)
        x, y coordinates of the centre"""
    x = cartesian_point[0] + centre_point[0]
    y = centre_point[1] - cartesian_point[1]
    return x, y


class Drawing(object):
    """The drawing is an instance of this class"""
    def __init__(self):
        self.image = None
        self.draw = None
        self.centre = None
        self.create_image()
        self.line_fill = (0, 0, 0)
        self.current_radius = 60
        self.step_distance_ratio = 0.4
        self.grow_per_loop = 14
        self.prev_point = Point(60, 0)

    def get_width(self, point):
        """Gets the width to use at a certain point in the picture

        Parameters
        ----------
        point : Point
            The point object

        Returns
        -------
        int
            Integer width of a line to use
        """
        return 5

    def run_loops(self, loop_count):
        """Run a bunch of loops"""
        for _ in range(loop_count):
            self.loop()

    def loop(self):
        """Run one loop"""
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

    def create_image(self):
        """Set up the blank slate"""
        self.image = PIL.Image.new('RGB', (3000, 3000), 'white')
        self.draw = PIL.ImageDraw.Draw(self.image)
        self.centre = (int(self.image.size[0] / 2), int(self.image.size[1] / 2))

    def save(self, filename=None, resize=None):
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
        if resize:
            self.image_small = self.image.resize(resize, PIL.Image.ANTIALIAS)
            self.image_small.save(filename)
        else:
            self.image.save(filename)

def run():
    drawing = Drawing()
    drawing.run_loops(60)
    drawing.save(resize=(1000, 1000))

if __name__ == '__main__':
    run()