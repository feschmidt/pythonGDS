import numpy as np
from source_dev.chip import Base_Chip
from source_dev.junction_ald_array import Junctionchip
from source_dev.squid_ald_array import SQUIDchip
from source_dev.rfcavities_dcbias import ShuntCavity

dict_pads = {'width': 200,
            'length': 300,
            'spacing': 300,
            'triheight': 100}

dict_junctions = [{'width': 5,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1},
                {'width': 5,
                'jjmin': 8,
                'jjmax': 14,
                'jjstep': 1}]

dict_squids = [{'width': 5,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1},
                {'width': 5,
                'jjmin': 8,
                'jjmax': 14,
                'jjstep': 1}]
                
dict_cavity = {'length': 6900,
            'centerwidth': 10,
            'gapwidth': 6.2,
            'shunts': 2,            # either 1 or 2. For future: extend to gap capacitors
            'leadlauncher': 100,    # should remain default like this
            'lead1': 1000,          # should remain default like this
            'holedim': (80,100),
            'holemarker': True}
                

name_jj = ['JJ test 1...7um', 'JJ test 8...15um']
jjs = [Junctionchip(name_jj[0],dict_pads,dict_junctions[0]), Junctionchip(name_jj[1],dict_pads,dict_junctions[1])]
[jjs[i].gen_junctions() for i in range(2)]
chipjj = [Base_Chip(name_jj[0],xdim=6e3,ydim=6e3,frame=True), Base_Chip(name_jj[1],xdim=6e3,ydim=6e3,frame=True)]

name_squid = ['JJ test 1...7um', 'JJ test 8...15um']
squids = [SQUIDchip(name_squid[0],dict_pads,dict_squids[0]), SQUIDchip(name_squid[1],dict_pads,dict_squids[1])]
[squids[i].gen_junctions() for i in range(2)]
chipsquid = [Base_Chip(name_squid[0],xdim=6e3,ydim=6e3,frame=True), Base_Chip(name_squid[1],xdim=6e3,ydim=6e3,frame=True)]

for i in range(2):
	for chipi,group in zip([chipjj[i],chipsquid[i]],[jjs[i],squids[i]]):
		chipi.add_component(group.cell,(0,0))
		chipi.add_bond_testpads(pos=(-2.1e3,-2.1e3))
		chipi.add_ebpg_marker((-2e3,-2e3))	
		chipi.add_photolitho_marker()
		chipi.add_photolitho_vernier()

name_cav = 'Shunt cavity'
cav = ShuntCavity(name_cav,dict_cavity)
cav.gen_full()
chipcav = Base_Chip(name_cav,xdim=10e3,ydim=10e3,frame=True)
chipcav.add_component(cav.cell,(-5e3,-5e3))
chipcav.add_ebpg_marker((-3310,-1560))
chipcav.add_photolitho_marker()
chipcav.add_photolitho_vernier()


# Add individual designs to big chip
chip = Base_Chip('full_wafer',xdim=25000,ydim=25000,wafer=False)
for chipi,pos in zip([chipjj[0], chipsquid[0], chipcav],[(-9e3,-3e3),(-9e3,3e3),(5e3,5e3)]):
    chip.add_component(chipi.cell,(pos[0]+1150,pos[1]))
for chipi,pos in zip([chipjj[1], chipsquid[1], chipcav],[(-3e3,-3e3),(-3e3,3e3),(5e3,-5e3)]):
    chip.add_component(chipi.cell,(pos[0]+1150,pos[1]))

#Dicing marker for RF
chip.add_dicing_marker(pos=(1150,0))
chip.add_dicing_marker(pos=(11150,0),hor=False)
chip.add_dicing_marker(pos=(0,10e3),vert=False)
chip.add_dicing_marker(pos=(0,-10e3),vert=False)
#Dicing marker for DC
chip.add_dicing_marker(pos=(-4850,0),hor=False)
chip.add_dicing_marker(pos=(-10850,0),hor=False)
#chip.add_TUlogo()
chip.save_to_gds(show = False, save = True)
