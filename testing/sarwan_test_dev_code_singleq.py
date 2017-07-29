import numpy as np
from source_dev.chip import Base_Chip
import source_dev.transmon as transmon


dict_pads = {'width': 600,
			'height': 250,
			'lead_width': 3,
			'lead_height':5,
			'fork_depth': 0.5,
			'rounded_edges':True,
			'layer':1}



# adding 0.1 at the end of the equation makes sure that we have some extra room

# Note that overlap cannot be negative!!!!!
w_dolan_bridge = 0.12
appr_overlap = (2*(700 - 45)*np.tan(35*np.pi/180) - w_dolan_bridge*1e3)/1e3 + 0.1
dict_junctions = {'bjunction_width':2,
				'bjunction_height':4,
				'junction_width':0.1,
				'junction_height':1,
				'w_dolan_bridge':w_dolan_bridge,
				'appr_overlap':appr_overlap,
				'overl_junc_lead':1,
				'layer':3}


first_qubit = transmon.Singlejuction_transmon('test',dict_pads,
											dict_junctions,short = False)
first_qubit.gen_pattern()

chip = Base_Chip('test_single junction transmon_chip',9000,9000)
chip.add_component(first_qubit.cell,(1200,200))
chip.save_to_gds(False)


