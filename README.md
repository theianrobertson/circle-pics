# Circle Pictures
Check out [here](https://i.redd.it/7knauidxy94y.jpg) and [here](http://i.imgur.com/FiXlS8F.jpg) for samples of what I'm looking to build for myself, using naught but Python.

# Thoughts
- First loop, constantly increase radius with a jitter (+- x random length)
- Store a list of point objects which are radius, angle (switch to a class)
- For each loop (maybe including the first?):
    - Find the closest angle from last loop, (or average of two?) and use that radius as input
    - Function(last radius, jitter, constant to add) to calculate a new radius
    - Stop after x loops, or when radius hits some limit
    - Calculate the number of iterations as a function of starting radius and some constant
- Line width
    - Constant to start
    - I'd want to match the centre of a base image with the centre of the generated image
    - Convert base image to black and white
    - Then each line segment could sample at the same point in the base image as its looking in the generated. Maybe take the average of the pixel and the eight surrounding pixels, then convert range(0,255) to range(min width, max width)
- Post processing
    - Paste onto something that looks like real paper (maybe)
    - Gaussian blur a little bit
    - Resize
    - Make something like those arts that are in Richmond