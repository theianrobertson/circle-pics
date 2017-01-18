# Circle Pictures
Recently I saw these images [here](https://i.redd.it/7knauidxy94y.jpg) and [here](http://i.imgur.com/FiXlS8F.jpg), which I thought were very cool-looking.  I thought maybe I could do similar myself, using naught but Python.  The latest iteration converts an image that looks like this:
![GuidoInput](inputs/guido_small.jpg?raw=true "Guido")

into this:
![GuidoOutput](test_outputs/guido.png?raw=true "Guido")

## To Use
(From virtual environment of some sort)
```
pip install -r requirements.txt
```

Then in Python:
```python
from circles import Drawing

drawing = Drawing()
drawing.add_base_image('inputs/guido.jpg')
drawing.run_loops(45)
drawing.save(resize=(1000, 1000), blur=1)
```

Right now the code needs some manual tweaks to make an image that's pleasing to the eye. The magic numbering has at least mostly been extracted to the top where it can be tweaked - that probably belongs in a config or something if you want to use this more widely.

## ToDo
- First loop, constantly increase radius with a jitter (+- x random length) to make it look more hand-drawn?
- Store a list of point objects which are radius, angle to get the previous radius at that angle
- For each loop (maybe including the first one?):
    - Find the closest angle from last loop, (or average of two?) and use that radius as input
    - Function(last radius, jitter, constant to add) to calculate a new radius
    - Stop after x loops, or when radius hits some limit
- Post processing
    - Paste onto something that looks like real paper (maybe?)
