import numpy as np
import gdsCAD as cad

# This file only contains method. It shall be used to collect all methods for DC24pin samples to generate bonding pads.
# Maybe move bond testpads from basechip class to here?

def gen_full_array(padgroup):
    '''
    Multiply padgroup cell for ALD JJs and SQUIDs and arrange them along the four sides of a 6x6mm2 chip
    '''
    # Merge objects into cells
    bottom = [cad.core.Cell('BOTTOM LAYER')] * 4
    bottom[0].add(padgroup[0]) 
    bottom[1] = cad.core.CellReference(bottom[0], origin=(0,0),rotation=90)
    bottom[2] = cad.core.CellReference(bottom[0], origin=(0,0),rotation=180)
    bottom[3] = cad.core.CellReference(bottom[0], origin=(0,0),rotation=270)

    top = [cad.core.Cell('TOP LAYER')] * 4
    top[0].add(padgroup[1])
    top[1] = cad.core.CellReference(top[0], origin=(0,0),rotation=90)
    top[2] = cad.core.CellReference(top[0], origin=(0,0),rotation=180)
    top[3] = cad.core.CellReference(top[0], origin=(0,0),rotation=270)

    # Merge all cells
    maincell = cad.core.Cell('MAIN')
    maincell.add(bottom)
    maincell.add(top)


    # Create a layout and add the cell
    # Maybe this is the problem??
    layout = cad.core.Cell('GRID_CHIP')
    layout.add(maincell)
    return layout

