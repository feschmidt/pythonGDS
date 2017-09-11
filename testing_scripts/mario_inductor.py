import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.spiral_inductor import SpiralInductor
import gdsCAD as cad

chipsize = 200
chip = Base_Chip('base', chipsize, chipsize,label=False)
inductor = SpiralInductor()
chip.add_component(inductor, (0,0))
chip.save_to_gds(show=True, save=False)