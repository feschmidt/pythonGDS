import numpy as np
from source_dev.chip import Base_Chip
import source_dev.transmon as transmon


dict_pads = {'width': 60,
			'height': 60,
			'lead_width': 10,
			'lead_height':10,
			'fork_depth': 0.0,
			'rounded_edges':True,
			'layer':1}


w_dolan_bridge = 0.12
appr_overlap = (2*(700 - 45)*np.tan(11*np.pi/180) - w_dolan_bridge*1e3)/1e3 + 0.1
dict_junctions = {'bjunction_width':2,
				'bjunction_height':6,
				'junction_width':0.1,
				'junction_height':1,
				'w_dolan_bridge':w_dolan_bridge,
				'appr_overlap':appr_overlap,
				'overl_junc_lead':2.1,
				'layer':2}


first_qubit = transmon.Singlejuction_transmon('qubit_100nm',dict_pads,
											dict_junctions,short = False,
											junctiontest = True)
first_qubit.gen_pattern()
qubit_100nm = first_qubit.cell

first_qubit.name = 'qubit_910nm'
first_qubit.dict_junctions['junction_width'] = 0.91
first_qubit.gen_pattern()
qubit_910nm = first_qubit.cell


chip = Base_Chip('Dosetest Al coating chip',9000,9000)
chip.add_component(qubit_100nm,(600,8000))
chip.add_component(qubit_910nm,(730,8000))
chip.save_to_gds(show=True, save= True)
