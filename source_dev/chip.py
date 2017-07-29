import numpy as np
import gdsCAD as cad
import time

class Base_Chip():
	
    """
    This object represent a single chip and can be considered as the parentobject.
    The reference position is the center of the chip, that is (0,0)
    Reserved layers: 20, 21, 22, 23
    Options for wafer:
        False --> rectangular chip
        1 --> 1" wafer
        2 --> 2" wafer etc
    """

    def __init__(self, name, xdim=1000, ydim=1000, frame=True, wafer=False):

        self.name = name
        self.xdim = xdim
        self.ydim = ydim
        self.wafer = wafer
        wafer_d = [0, 25.4e3, 50.8e3, 76.2e3, 100e3, 125e3, 150e3]  # wafer diameters in um
        
        if xdim < 1001 and ydim < 1001:
            self.boxwidth = 10
        else:
            self.boxwidth = 100
        
            
        self.layer_label = 20
        self.layer_box = 21
        self.layer_alignment = 22
        self.layer_testpads = 23
        
        self.cell = cad.core.Cell(name)
        if frame==True:
            if wafer==False:
                self.make_layout()
            else:
                self.make_wafer(wafer_d[wafer]/2)


    def make_layout(self):
        '''
        Generate chip with dimensions xdim,ydim
        '''
        box=cad.shapes.Box((-self.xdim/2, -self.ydim/2), (self.xdim/2, self.ydim/2),
				         width=self.boxwidth, layer =self.layer_box)

        date = time.strftime("%d/%m/%Y")
        #The label is added 100 um on top of the main cell
        label_grid_chip = cad.shapes.LineLabel( self.name + "  " +\
								         date,50,(-200,self.ydim/2-500),
								         layer=self.layer_label)


        self.cell.add(box)
        self.cell.add(label_grid_chip)
        
        
    def make_wafer(self,wafer_r):
        '''
        Generate wafer with primary flat on the left. From https://coresix.com/products/wafers/ I estimated that the angle defining the wafer flat to arctan(flat/2 / radius)
        '''
        angled = 18
        angle = angled*np.pi/180
        circ = cad.shapes.Circle((0,0), wafer_r, width=self.boxwidth, initial_angle=180+angled, final_angle=360+180-angled, layer=self.layer_box)
        flat = cad.core.Path([(-wafer_r*np.cos(angle),wafer_r*np.sin(angle)),(-wafer_r*np.cos(angle),-wafer_r*np.sin(angle))], width=self.boxwidth, layer=self.layer_box)

        date = time.strftime("%d/%m/%Y")
        #The label is added 100 um on top of the main cell
        label_grid_chip = cad.shapes.LineLabel( self.name + "  " +\
								         date,500,(-2e3,wafer_r-1e3),
								         layer=self.layer_label)


        self.cell.add(circ)
        self.cell.add(flat)
        self.cell.add(label_grid_chip)


    def add_component(self,cell_obj, pos):
        """
        params cell_obj : cell object to add to maincell
        params pos : tuple of positions
        """
        if pos[0]> self.xdim/2 or pos[0]<-self.xdim/2:
            raise ValueError(" component lies out of layout") 

        if pos[1]> self.ydim/2 or pos[1]<-self.ydim/2:
            raise ValueError(" component lies out of layout") 

        self.cell.add(cell_obj,origin=pos)

    
    def add_ebpg_marker(self, pos=(-3310,-1560), size=20, spacing=200):
        '''
        4 ebeam marker each 20um rectangular and 200um spaced apart
        params pos : tuple of positions
        '''
        marker = [cad.core.Cell('EBEAM')] * 4
        x = [pos[0], pos[0] + spacing, pos[0] + spacing, pos[0]]
        y = [pos[1], pos[1], pos[1] + spacing, pos[1] + spacing]
        for i in range(4):
            box = cad.shapes.Rectangle((x[i]-size/2,y[i]-size/2),(x[i]+size/2,y[i]+size/2),
                                        layer = self.layer_alignment)
            marker[0].add(box)
        marker[1] = cad.core.CellReference(marker[0], origin=(-2*pos[0]-spacing,-2*pos[1]-spacing))
        marker[2] = cad.core.CellReference(marker[0], origin=(0,-2*pos[1]-spacing))
        marker[3] = cad.core.CellReference(marker[0], origin=(-2*pos[0]-spacing,0))
        self.cell.add(marker)


    def save_to_gds(self, loc = 'testing/', save = True, show = True):
        '''
        Save and show gds file
        Default location in testing/, can be adjusted via loc
        '''
        layout = cad.core.Layout('MAIN_CHIP')
        layout.add(self.cell)
        if save:
            layout.save(loc + self.name + '.gds')
        if show:
            layout.show()


    def add_bond_testpads(self, pos=(-2000,-2000), dim=(300,300), num=4):
        '''
        value(num) bonding pads with dimension dim (tuple) at position pos (tuple)
        '''
        pads = cad.core.Cell('TESTPADS')
        x = [pos[0], -pos[0], -pos[0], pos[0]]
        y = [pos[1], pos[1], -pos[1], -pos[1]]
        for i in range(num):
            box = cad.shapes.Rectangle((x[i]-dim[0]/2,y[i]-dim[1]/2),(x[i]+dim[0]/2,y[i]+dim[1]/2), layer = self.layer_testpads)
            pads.add(box)
        self.cell.add(pads)


    def add_photolitho_marker(self, pos=(0,0)):
        '''
        Add alignment marker for photolithography
        '''
        marker = cad.core.Cell('PHOTO')
        amarks0 = cad.templates.AlignmentMarks(('A','C'),(1,2))
        amarks = cad.core.CellReference(amarks0).translate(pos)
        marker.add(amarks)
        self.cell.add(amarks)
    
    
    def add_photolitho_vernier(self, pos=(-500,-500)):
        '''
        Add vernier structures for determining alignment precision
        '''
        verniers = cad.core.Cell('VERNIER')
        vmarks0 = cad.templates.Verniers(('A','B'),(1,2))
        vmarks = cad.core.CellReference(vmarks0).translate(pos)
        verniers.add(vmarks)
        self.cell.add(verniers)
        
        
    def add_dicing_marker(self, pos=(0,0), hor=True, vert=True):
        '''
        Add rectangular dicing marks across the entire chip/wafer
        '''
        marker = cad.core.Cell('DICING')
        hmarks0 = cad.shapes.Rectangle((-500,-125),(500,125))
        vmarks0 = cad.shapes.Rectangle((-125,-500),(125,500))
        for xx,yy in zip(np.arange(-self.xdim/4,self.xdim/4+1,1000),np.arange(-self.ydim/4,self.ydim/4+1,1000)):
            if hor==True:
                hmarks = cad.utils.translate(hmarks0, (2*xx+pos[0],pos[1]))
                marker.add(hmarks)
            if vert==True:
                vmarks = cad.utils.translate(vmarks0, (pos[0],2*yy+pos[1]))
                marker.add(vmarks)
        self.cell.add(marker)
                
    
    '''
    # Disabled for now since issue with dxfImport    
    def add_TUlogo(self, pos=(0,100)):
        # logo is added 100um below bottom edge of chip
        logo = cad.core.DxfImport('examples/TU_Delft_logo_Black.dxf',scale=1.0)
        logo.layer=self.layer_label
        self.cell.add(logo)
    '''
