import numpy as np
from source_dev.chip import Base_Chip
from source_dev.junction_ald_array import Junctionchip
from source_dev.squid_ald_array import SQUIDchip

dict_pads = {'width': 200,
            'length': 300,
            'spacing': 300,
            'triheight': 100}

dict_junctions = {'width': 5,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1}

dict_squids = {'width': 5,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1}
                

name_jj = 'JJ test'
jjs = Junctionchip(name_jj,dict_pads,dict_junctions)
jjs.gen_junctions()
chipjj = Base_Chip(name_jj,xdim=6e3,ydim=6e3,frame=False)
chipjj.add_component(jjs.cell,(0,0))
chipjj.add_photolitho_marker()
chipjj.add_photolitho_vernier()
chipjj.add_bond_testpads()
chipjj.add_ebpg_marker()

name_squid = 'SQUID test'
squids = SQUIDchip(name_squid,dict_pads,dict_squids)
squids.gen_junctions(dim=(50,50))
chipsquid = Base_Chip(name_jj,xdim=6e3,ydim=6e3,frame=False)
chipsquid.add_component(squids.cell,(0,0))
chipsquid.add_photolitho_marker()
chipsquid.add_photolitho_vernier()
chipsquid.add_bond_testpads()
chipsquid.add_ebpg_marker()


chip = Base_Chip('testchip',xdim=25000,ydim=25000,wafer=2)
chip.add_component(chipjj.cell,(-6e3,-6e3))
chip.add_component(chipsquid.cell,(6e3,6e3))

chip.add_dicing_marker(pos=(0,0))
#chip.add_TUlogo()
chip.save_to_gds(show = True, save = True)
