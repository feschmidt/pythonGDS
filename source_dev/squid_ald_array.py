import numpy as np
import gdsCAD as cad
import dc_24pin

class SQUIDchip():

    def __init__(self, name, dict_pads, dict_junctions, x0 = -100, y0 = -2200, 
        tlength = 1505):
        '''
        Class for ALD SQUIDs. These are based on vertical tunnel barriers with a two-step process.
        '''
 
        self.name = name
        self.dict_pads = dict_pads
        self.dict_junctions = dict_junctions
        self.x0 = x0
        self.y0 = y0
        self.tlength = tlength

        self.layer_bottom = 1
        self.layer_top = 2

    def gen_junctions(self, dim = (50,50)):
        '''
        Consists of a centerline that spreads out to 6 individual SQUIDs
        First creates bottom row of JJs, finally uses dc_24pin to generate the full 4x4 array
        '''
        
        padwidth = self.dict_pads['width']
        padlength = self.dict_pads['length']
        padspace = self.dict_pads['spacing']
        triheight = self.dict_pads['triheight']
        tripeak = self.y0 + padlength + triheight

        jjwidth = self.dict_junctions['width']
        jjmin = self.dict_junctions['jjmin']
        jjmax = self.dict_junctions['jjmax']
        jjstep = self.dict_junctions['jjstep']
    
        cwidth = 20
        centerpoints = [(0, tripeak - cwidth / 2),
                        (0, tripeak + 100 + cwidth / 2 +dim[1]),
                        (self.tlength-5, tripeak + 100 + cwidth / 2 +dim[1]),
                        (- self.tlength, tripeak + 100 + cwidth / 2 +dim[1])]
        centerline = cad.core.Path(centerpoints, cwidth, layer = self.layer_bottom)

        self.padgroup = [cad.core.Cell('padgroup')] * 2
        self.padgroup[0].add(centerline)

        for k,i in enumerate(range(-3, 4)):
            xs = (padwidth + padspace) * i
            squid_left = cad.core.Path([[xs,tripeak-jjwidth/2],
                                    [xs,tripeak+dim[1]],
                                    [xs-dim[0]/2,tripeak+dim[1]],
                                    [xs-dim[0]/2,tripeak+2*dim[1]+(k+1)*jjstep]],
                                    jjwidth,layer=self.layer_top)
            squid_right = cad.core.Path([[xs,tripeak-jjwidth/2],
                                    [xs,tripeak+dim[1]],
                                    [xs+dim[0]/2,tripeak+dim[1]],
                                    [xs+dim[0]/2,tripeak+2*dim[1]+(k+1)*jjstep]],
                                    jjwidth, layer=self.layer_top)
            pad = cad.shapes.Rectangle((self.x0 + xs,self.y0),(self.x0 + padwidth + xs,self.y0 + padlength))
            tripoints = [[self.x0 + xs,self.y0 + padlength],
                        [self.x0 + padwidth / 2. + xs,tripeak],
                        [self.x0 + padwidth + xs, self.y0 + padlength]]
            tri = cad.core.Boundary(tripoints)

            if i==0:
                ll = self.layer_bottom
            else:
                ll = self.layer_top
                squid_hor = cad.core.Path([[xs-0.6*dim[0],tripeak+2*dim[1]+cwidth/2],
                                    [xs+0.6*dim[0],tripeak+2*dim[1]+cwidth/2]],
                                    cwidth,layer=self.layer_bottom)
                squid_ver = cad.core.Path([[xs,tripeak+2*dim[1]+cwidth/2],
                                    [xs,tripeak+100+dim[1]+cwidth/2]],
                                    cwidth,layer=self.layer_bottom)
            for toadd in [pad, tri, squid_ver, squid_hor]:
                if toadd==pad or toadd==tri:
                    toadd.layer = ll
                self.padgroup[ll-1].add(toadd)

            if i!=0:
                self.padgroup[ll-1].add(squid_left)
                self.padgroup[ll-1].add(squid_right)

        # Create full array by inputting bottom junction row into dc_24pin method gen_full_array
        self.cell = dc_24pin.gen_full_array(padgroup = self.padgroup)




