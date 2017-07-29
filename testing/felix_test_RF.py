import numpy as np
import gdsCAD as cad
from source_dev.chip import Base_Chip
import source_dev.junction_ald_array as junction_array
import source_dev.squid_ald_array as squid_array
import source_dev.rfcavities_dcbias as cavities

dict_cavity = {'length': 6900,
            'centerwidth': 10,
            'gapwidth': 6.2,
            'shunts': 2,            # either 1 or 2. For future: extend to gap capacitors
            'leadlauncher': 100,    # should remain default like this
            'lead1': 1000,          # should remain default like this
            'holedim': (80,100),
            'holemarker': True}
                

name = 'testcavities'
testf = cavities.ShuntCavity(name,dict_cavity)
testf.gen_full()

chipsize = 10e3
chip = Base_Chip(name,chipsize,chipsize)
chip.add_component(testf.cell,(-5e3,-5e3))
chip.add_ebpg_marker((-3310,-1560))
#chip.add_dicing_marker(pos=(5000,5000))
#chip.add_TUlogo()
chip.save_to_gds(show = True, save = True)

