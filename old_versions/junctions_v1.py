import os.path
from gdsCAD import *

# Create a Cell and add the box
maincell = core.Cell('MAIN')

cell=core.Cell('GUIDES')
# Layer 0: 6x6mm chip
l = 6000
box=shapes.Box((-l/2,-l/2), (l/2,l/2), width=50, layer=0)
cell.add(box)

dict_pads = {'width': 200,
			'length': 300,
			'spacing': 300,
			'triheight': 100}

dict_junctions = {'width': 20,
				'jjstep': 1}
padwidth = 200
padlength = 300
padspace = 300
x0 = -100
y0 = -2200
triheight = 100
tripeak = y0+padlength+triheight
w1=20
l1 = 100
tlength = 1600
jjstep = 1
padgroup = [core.Cell('bot')] * 2    #[0]: bottom, [1]: top
centerline = core.Path([[0,tripeak-10],[0,tripeak+l1+w1/2],[tlength,tripeak+l1+w1/2],[-tlength,tripeak+l1+w1/2]],w1,layer=1,pathtype=0)
padgroup[0].add(centerline)

for k,i in enumerate(range(-3,4)):
    l=1
    xs = (padwidth + padspace) * i
    junctionpoints = ([xs,tripeak-10],
    				[xs,tripeak+l1],
    				[xs,tripeak+l1+(k+1)*jjstep])
    junction = core.Path(junctionpoints,w1,layer=2)
    pad = shapes.Rectangle((x0+xs,y0),(x0+padwidth+xs,y0+padlength))
    tri = core.Boundary([[x0+xs,y0+padlength], [x0+padwidth/2.+xs,tripeak], [x0+padwidth+xs,y0+padlength]])
    if i==0:
        l=1
    else:
        l=2
    pad.layer = l
    tri.layer = l
    padgroup[l-1].add(pad)
    padgroup[l-1].add(tri)
    if i!=0:
        padgroup[l-1].add(junction)

# Merge objects into cells
bottom = [core.Cell('BOTTOM LAYER')] * 4
bottom[0].add(padgroup[0])
bottom[1] = core.CellReference(bottom[0], origin=(0,0),rotation=90)
bottom[2] = core.CellReference(bottom[0], origin=(0,0),rotation=180)
bottom[3] = core.CellReference(bottom[0], origin=(0,0),rotation=270)

top = [core.Cell('TOP LAYER')] * 4
top[0].add(padgroup[1])
top[1] = core.CellReference(top[0], origin=(0,0),rotation=90)
top[2] = core.CellReference(top[0], origin=(0,0),rotation=180)
top[3] = core.CellReference(top[0], origin=(0,0),rotation=270)

# Add alignment marks
amarks = templates.AlignmentMarks(('A','C'),(1,2))
vernier0 = templates.Verniers(('A','B'),(1,2))
vernier = core.CellReference(vernier0).translate([-500,-500])

# Merge all cells
maincell.add(cell)
maincell.add(bottom)
maincell.add(top)
maincell.add(amarks)
maincell.add(vernier)

#block = templates.Block('ARRAY', maincell, (25000, 25000))


# Create a layout and add the cell
layout = core.Layout('LIBRARY')
layout.add(maincell)

# Save the layout and then display it on screen
layout.save('junctions_v1.gds')
layout.show()
