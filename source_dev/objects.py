import numpy as np
from scipy.constants import epsilon_0
from stcad.source_dev.utilities import *
from stcad.source_dev.meandering_line import MeanderingLine
import gdsCAD as cad
import copy
import numpy as np
import copy

def sign(x):
  if x<0:
    return -1.
  if x==0:
    return 0.
  if x>0:
    return 1.

def angle(vec):
    return np.arctan2(vec[1],vec[0])*180./np.pi

def norm(vec):
    return np.sqrt(vec[0]**2+vec[1]**2)

class WaffleCapacitor(cad.core.Cell):
    """docstring for WaffleCapacitor"""
    def __init__(self,base_width, 
        base_lead_length, 
        base_line_width, 
        ground_length, 
        n_holes, 
        base_hole_diameter, 
        sacrificial_width_overlap, 
        side_support, 
        release_hole_diameter, 
        ground = True,
        base_layer =1, 
        base_hole_layer =4, 
        sacrificial_layer =2, 
        sacrificial_hole_layer =5, 
        top_layer =3, 
        top_hole_layer =6,
        name = ''):
        super(WaffleCapacitor, self).__init__(name)
        self.base_width = base_width
        self.base_lead_length = base_lead_length
        self.base_line_width = base_line_width
        self.ground_length = ground_length
        self.n_holes = n_holes
        self.base_hole_diameter = base_hole_diameter
        self.sacrificial_width_overlap = sacrificial_width_overlap
        self.side_support = side_support
        self.release_hole_diameter = release_hole_diameter
        self.base_layer = base_layer
        self.base_hole_layer = base_hole_layer
        self.sacrificial_layer = sacrificial_layer
        self.sacrificial_hole_layer = sacrificial_hole_layer
        self.top_layer = top_layer
        self.top_hole_layer = top_hole_layer

        # base layer
        base_hex = Hexagon(width = base_width,layer = base_layer)
        hex_width = base_width+base_lead_length*2.


        if ground:
            base_hex.add_leads_on_sides(base_lead_length,base_line_width)
            points = [[-hex_width/2.+base_lead_length*np.sin(np.pi/6),base_lead_length*np.cos(np.pi/6)],\
                        [-hex_width/4.,np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
                        [+hex_width/4.,np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
                        [+hex_width/2.,0],\
                        [+hex_width/4.,-np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
                        [-hex_width/4.,-np.sqrt(hex_width**2/4.-hex_width**2/16.)],
                        [-hex_width/2.+base_lead_length*np.sin(np.pi/6),-base_lead_length*np.cos(np.pi/6)],
                        [-hex_width/2.-ground_length,-base_lead_length*np.cos(np.pi/6)],
                        [-hex_width/2.-ground_length,-hex_width/2.-ground_length],
                        [+hex_width/2.+ground_length,-hex_width/2.-ground_length],
                        [+hex_width/2.+ground_length,+hex_width/2.+ground_length],
                        [-hex_width/2.-ground_length,+hex_width/2.+ground_length],
                        [-hex_width/2.-ground_length,+base_lead_length*np.cos(np.pi/6)],]
            self.add(cad.core.Boundary(points))
        else:
            base_hex.add_lead_on_1_side(base_lead_length,base_line_width)


        self.add(base_hex)

        # base holes
        base_margin = base_width/(n_holes)/np.sqrt(2)
        base_holes = hex_array_of_holes(base_margin,base_width,n_holes,base_hole_diameter,base_hole_layer)
        self.n_base_holes = base_holes.n
        self.add(base_holes)

        # sacrificial layer
        sacrificial_width = base_width+2*sacrificial_width_overlap
        sacrificial_hex = Hexagon(width = sacrificial_width,layer = sacrificial_layer)
        if ground:
            sacrificial_hex.add_leads_on_sides(base_lead_length,base_line_width+2*sacrificial_width_overlap)
        else:
            sacrificial_hex.add_lead_on_1_side(base_lead_length,base_line_width+2*sacrificial_width_overlap)
        self.add(sacrificial_hex)

        # sacrificial holes
        sacrificial_holes = hex_array_of_holes(base_margin,base_width,n_holes,base_hole_diameter-2*sacrificial_width_overlap,sacrificial_hole_layer)
        self.n_sacrificial_holes = sacrificial_holes.n
        self.add(sacrificial_holes)

        # top layer
        top_width =  sacrificial_width+2*side_support
        sacrificial_hex = Hexagon(width =top_width,layer = top_layer)
        self.add(sacrificial_hex)
        cad.core.default_layer=top_layer
        self.add(line_polygon([-top_width/2.+base_line_width,0], [-hex_width/2.-ground_length,0], base_line_width))

        # top holes
        top_holes = hex_array_of_holes(base_margin/2.,base_width,2*n_holes+1,release_hole_diameter,top_hole_layer, skip_some=True)
        self.n_top_holes = top_holes.n
        self.add(top_holes)

    def capacitance(self,gap):
        A = 3.*np.sqrt(3)/2.*float(self.base_width*1.e-6)**2
        A -=self.n_base_holes*np.pi*(float(self.base_hole_diameter*1.e-6)/2.)**2
        A -=self.n_top_holes*np.pi*(float(self.release_hole_diameter*1.e-6)/2.)**2

        return epsilon_0*A/gap

class hex_array_of_holes(cad.core.Cell):
    """docstring for ClassName"""
    def __init__(self, margin, base_width,n_holes, hole_diameter, layer, skip_some = False, name=''):
        super(hex_array_of_holes, self).__init__(name)

        self.n = 0

        if n_holes%2==0:
            raise ValueError("the width should contain an odd number of holes") 
        half_height = np.sqrt(base_width**2/4.-base_width**2/16.)-margin
        pitch_vertical = half_height/float((n_holes+1)/2-1)
        if skip_some == False:
            for i in range((n_holes+1)/2):
                y = i*pitch_vertical
                x_start = (base_width)/2.-margin*2./np.sqrt(3)-(y)/np.tan(np.pi/3.)
                x_array = np.linspace(-x_start,x_start,n_holes-i)
                for x in x_array:
                    self.add(cad.shapes.Disk((x,y), hole_diameter/2.,layer =layer))
                    self.n +=1
            for i in range(1,(n_holes+1)/2):
                y = -i*pitch_vertical
                x_start = (base_width)/2.-margin-(-y)/np.tan(np.pi/3.)
                x_array = np.linspace(-x_start,x_start,n_holes-i)
                for x in x_array:
                    self.add(cad.shapes.Disk((x,y), hole_diameter/2.,layer =layer))
                    self.n +=1
        else:
            for i in range((n_holes+1)/2):
                y = i*pitch_vertical
                x_start = (base_width)/2.-margin*2./np.sqrt(3)-(y)/np.tan(np.pi/3.)
                x_array = np.linspace(-x_start,x_start,n_holes-i)
                j = 0
                for x in x_array:
                    if i%2==0 and (j+1)%2==0:
                        pass
                    else:
                        self.add(cad.shapes.Disk((x,y), hole_diameter/2.,layer =layer))
                        self.n +=1
                    j+=1
            for i in range(1,(n_holes+1)/2):
                y = -i*pitch_vertical
                x_start = (base_width)/2.-margin-(-y)/np.tan(np.pi/3.)
                x_array = np.linspace(-x_start,x_start,n_holes-i)
                j = 0
                for x in x_array:
                    if i%2==0 and (j+1)%2==0:
                        pass
                    else:
                        self.add(cad.shapes.Disk((x,y), hole_diameter/2.,layer =layer))
                        self.n +=1
                    j+=1


class MeanderingLine(cad.core.Cell):
    """docstring for MeanderingLine"""
    def __init__(self, 
        points = [[-100,0],[-100,-50],[-50,-50],[-50,0],[50,0],[50,-50],[0,-50]],
        turn_radius = 16.,
        line_width = 10.,
        layer = None,
        path = False,
        name=''):   

        def sign(x):
          if x<0:
            return -1.
          if x==0:
            return 0.
          if x>0:
            return 1.

        super(MeanderingLine, self).__init__(name)
        if layer != None:
            cad.core.default_layer=layer

        if path == False:
            # i.e. make a boundary
            if len(points) == 2:
                line = line_polygon(points[0],points[1], line_width)
            else:
                n_last = len(points)-1
                sec = [points[0]]
                for i in range(1,n_last):
                    p = np.array(points[i])
                    p_before = np.array([points[i][0]+turn_radius*sign(points[i-1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i-1][1]-points[i][1])])
                    p_after = np.array([points[i][0]+turn_radius*sign(points[i+1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i+1][1]-points[i][1])])
                    curve_center = p_after + p_before - p
                    angle_i = angle(p_before - curve_center)
                    angle_delta = angle(p_after - curve_center)-angle_i
                    if angle_delta < -180.:
                        angle_delta+=360.
                    if angle_delta > 180.:
                        angle_delta-=360.
                    sec.append(p_before)
                    if i ==1:
                        line = line_polygon(sec[0],sec[1], line_width)
                    else:
                        line =join_polygons(line,line_polygon(sec[0],sec[1], line_width))
                    line = join_polygons(line,arc_polygon(curve_center, turn_radius, line_width,\
                                        initial_angle=angle_i, final_angle=angle_i+angle_delta, number_of_points = 199))
                    sec=[p_after]
                sec.append([points[n_last][0],points[n_last][1]])
                line = join_polygons(line,line_polygon(sec[0],sec[1], line_width))
            
            self.boundary = line
            self.add(line)


        if path == True:
            line  = cad.core.Elements()
            n_last = len(points)-1
            sec = [points[0]]
            for i in range(1,n_last):
                p = np.array(points[i])
                p_before = np.array([points[i][0]+turn_radius*sign(points[i-1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i-1][1]-points[i][1])])
                p_after = np.array([points[i][0]+turn_radius*sign(points[i+1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i+1][1]-points[i][1])])
                curve_center = p_after + p_before - p
                angle_i = angle(p_before - curve_center)
                angle_delta = angle(p_after - curve_center)-angle_i
                if angle_delta < -180.:
                    angle_delta+=360.
                if angle_delta > 180.:
                    angle_delta-=360.
                sec.append(p_before)
                line.add(cad.core.Path(sec, line_width))
                line.add(cad.shapes.Circle(curve_center, turn_radius, line_width,\
                    initial_angle=angle_i, final_angle=angle_i+angle_delta))
                sec=[p_after]
            sec.append([points[n_last][0],points[n_last][1]])
            line.add(cad.core.Path(sec, line_width))

            self.add([line])

class Hexagon(cad.core.Cell):
    """docstring for Hexagon"""
    def __init__(self, width, layer = cad.core.default_layer,name=''):
        super(Hexagon, self).__init__(name)
        self.width = width
        self.name = name
        self.layer = layer
        hex_width = width

        self.points = [[-hex_width/2.,0],\
            [-hex_width/4.,np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
            [+hex_width/4.,np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
            [+hex_width/2.,0],\
            [+hex_width/4.,-np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
            [-hex_width/4.,-np.sqrt(hex_width**2/4.-hex_width**2/16.)]]
        self.add(cad.core.Boundary(self.points,layer = self.layer))

    def add_leads_on_sides(self,lead_length,line_width):
        cad.core.default_layer = self.layer
        for i in range(-1,5):
            self.add(perpendicular_line(self.points[i],self.points[i+1],lead_length,line_width))

    def add_lead_on_1_side(self,lead_length,line_width):
        cad.core.default_layer = self.layer
        self.add(perpendicular_line(self.points[0],self.points[1],lead_length,line_width))


class Drum(cad.core.Cell):
    """docstring for Drum"""
    def __init__(self, base_layer = 1,
                    sacrificial_layer = 2 ,
                    top_layer = 3,
                    outer_radius = 9,
                    head_radius = 7,
                    electrode_radius = 6,
                    cable_width = 0.5,
                    sacrificial_tail_width = 3,
                    sacrificial_tail_length = 3,
                    opening_width = 4,
                    N_holes = 3,
                    hole_angle = 45,
                    hole_distance_to_center = 4.5,
                    hole_distance_to_edge = 0.5,
                    name = ''):
        super(Drum, self).__init__(name)
        hole_radius = (head_radius-hole_distance_to_edge-hole_distance_to_center)/2.
        opening_angle = np.arcsin(float(opening_width)/float(head_radius)/2.)*180/np.pi


        ##################################
        # Head (holey section)
        ##################################

        cad.core.default_layer=top_layer
        holy_section_of_head = cad.core.Elements()


        angle_start = 0
        angle_end = hole_angle
        section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
          initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
        hole_2_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_end/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_end/180.*np.pi)]
        hole_2 = cad.shapes.Disk(hole_2_position, hole_radius,layer=top_layer)
        section=xor_polygons(section,hole_2)
        holy_section_of_head.add(section)


        for i in range(N_holes-1):
          angle_start = hole_angle+i*(180-2*hole_angle)/(N_holes-1)
          angle_end = hole_angle+(i+1)*(180-2*hole_angle)/(N_holes-1)
          section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
            initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
          hole_1_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_start/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_start/180.*np.pi)]
          hole_1 = cad.shapes.Disk(hole_1_position, hole_radius,layer=top_layer)
          hole_2_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_end/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_end/180.*np.pi)]
          hole_2 = cad.shapes.Disk(hole_2_position, hole_radius,layer=top_layer)
          section=xor_polygons(section,hole_1)
          section=xor_polygons(section,hole_2)
          holy_section_of_head.add(section)


        angle_start = 180-hole_angle
        angle_end = 180
        section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
          initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
        hole_1_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_start/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_start/180.*np.pi)]
        hole_1 = cad.shapes.Disk(hole_1_position, hole_radius,layer=top_layer)
        section=xor_polygons(section,hole_1)
        holy_section_of_head.add(section)

        ##################################
        # Head (rest + supports)
        ##################################

        drum_head_outer = cad.shapes.Disk((0,0), head_radius, inner_radius = hole_distance_to_center+2*hole_radius, layer=top_layer) 
        drum_head_inner = cad.shapes.Disk((0,0), hole_distance_to_center, layer=top_layer) 


        support_top = cad.shapes.Disk((0,0), outer_radius, inner_radius = head_radius,\
          initial_angle=opening_angle, final_angle=180-opening_angle, layer=top_layer)
        support_bottom = cad.shapes.Disk((0,0), outer_radius, inner_radius = head_radius,\
          initial_angle=opening_angle, final_angle=180-opening_angle, layer=top_layer).copy().reflect('x')



        ##################################
        # Electrode
        ##################################

        electrode = cad.shapes.Disk((0,0), electrode_radius, layer=base_layer) 
        # electrode_tail = cad.core.Path([[-outer_radius,0],[outer_radius,0]], cable_width,layer = base_layer)



        ##################################
        # Sacrificial layer
        ##################################


        sacrificial_drum = cad.shapes.Disk((0,0), head_radius, layer=sacrificial_layer) 
        sacrificial_tail = cad.core.Path([[-head_radius-sacrificial_tail_length,0],[head_radius+sacrificial_tail_length,0]],\
         sacrificial_tail_width,layer = sacrificial_layer)


        ##################################
        # Add all components
        ##################################

        self.add([holy_section_of_head,holy_section_of_head.copy().reflect('x'), drum_head_inner,drum_head_outer,support_bottom,support_top])
        self.add([electrode])
        # self.add([electrode_tail])

        self.add([sacrificial_tail,sacrificial_drum])


class CPW(cad.core.Cell):
    """docstring for CPW"""
    def __init__(self, 
        points,
        turn_radius = 5.,
        pin = 4.,
        gap = 2.,
        layer = 1,
        name=''):   


        super(CPW, self).__init__(name)
        cad.core.default_layer=layer
        points = np.array(points)
        self.points = points
        self.length = 0.
        self.pin = pin
        self.gap = gap
        self.layer = layer
        if len(points) == 2:
            self.add(double_line_polygon(points[0],points[1],gap,pin))
            self.length += norm(points[1]-points[0])
        else:
            n_last = len(points)-1
            sec = [points[0]]
            for i in range(1,n_last):
                p = np.array(points[i])
                p_before = np.array([points[i][0]+turn_radius*sign(points[i-1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i-1][1]-points[i][1])])
                p_after = np.array([points[i][0]+turn_radius*sign(points[i+1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i+1][1]-points[i][1])])
                curve_center = p_after + p_before - p
                angle_i = angle(p_before - curve_center)
                angle_delta = angle(p_after - curve_center)-angle_i
                if angle_delta < -180.:
                    angle_delta+=360.
                if angle_delta > 180.:
                    angle_delta-=360.
                sec.append(p_before)
                self.add(double_line_polygon(sec[0],sec[1],gap,pin))
                self.length += norm(sec[1]-sec[0])
                self.add(double_arc_polygon(curve_center, turn_radius,gap,pin,\
                                    initial_angle=angle_i, final_angle=angle_i+angle_delta, number_of_points = 199))
                self.length += 2*np.pi*turn_radius*abs(angle_delta)/360.
                sec=[p_after]
            sec.append([points[n_last][0],points[n_last][1]])
            self.add(double_line_polygon(sec[0],sec[1],gap,pin))
            self.length += norm(sec[1]-sec[0])

    def add_launcher(self,pos,bonding_pad_length = 400,bonding_pad_gap = 200,bonding_pad_width =500,taper_length = 500,buffer_length = 100):
        if pos == 'beginning' or pos=='b':
            p_0 = self.points[0]
            p_1 = self.points[1]
        elif pos=='end' or pos=='e':
            p_0 = self.points[-1]
            p_1 = self.points[-2]
        else:
            raise ValueError("First argumnet should be either 'beginning' or 'b' or 'end' or 'e'")
        cad.core.default_layer=self.layer
        
        vec = p_1-p_0
        if vec[0] == 0:
            if vec[1] > 0:
                dir = 'up'
            else:
                dir = 'down'
        else:
            if vec[0] > 0:
                dir = 'right'
            else:
                dir = 'left'

        startpoint = 0
        transl = pos

        launchpoints_top = [[-buffer_length-taper_length-bonding_pad_length, 0 ],
                            [-buffer_length-taper_length-bonding_pad_length, bonding_pad_gap + bonding_pad_width/2. ],
                            [-buffer_length-taper_length-bonding_pad_length, bonding_pad_gap + bonding_pad_width/2. ],
                            [-taper_length, bonding_pad_gap + bonding_pad_width/2. ],
                            [0, self.gap + self.pin/2. ],
                            [0, self.pin/2. ],
                            [-taper_length, bonding_pad_width/2. ],
                            [-taper_length-bonding_pad_length, bonding_pad_width/2. ],
                            [-taper_length-bonding_pad_length,0. ]]

        launcher1 = cad.core.Boundary(launchpoints_top,layer = self.layer)
        launcher2 = cad.utils.reflect(launcher1, 'x')

        launcherlist = cad.core.Elements([launcher1, launcher2])

        if dir == 'left':
            launcherlist = cad.utils.reflect(launcherlist, 'y')
        elif dir == 'down':
            launcherlist = cad.utils.rotate(launcherlist, -90)
        elif dir == 'up':
            launcherlist = cad.utils.rotate(launcherlist, 90)
        elif dir == 'right':
            pass

        launcherlist = cad.utils.translate(launcherlist, p_0)
        self.add(launcherlist)

    def add_open(self,pos,length = 10):
        if pos == 'beginning' or pos=='b':
            p_0 = self.points[1]
            p_1 = self.points[0]
        elif pos=='end' or pos=='e':
            p_0 = self.points[-2]
            p_1 = self.points[-1]
        else:
            raise ValueError("First argumnet should be either 'beginning' or 'b' or 'end' or 'e'")
        cad.core.default_layer=self.layer
        # normalize vector
        vec = p_1-p_0
        vec = vec/norm(vec)
        vec*=length
        self.add(line_polygon(p_1,p_1+vec, self.gap*2.+self.pin))



class SpiralInductor(cad.core.Cell):
    """docstring for SpiralInductor"""
    def __init__(self, 
        exterior = 55.,
        coil_number = 45,
        line_width = 0.25,
        spacing = 0.25,
        bridge_width = 2.,
        overlap_square_width = 3.,
        tail_length = 5.,
        base_layer = 1,
        sacrificial_layer = 2,
        top_layer = 3,
        name=''):   


        super(SpiralInductor, self).__init__(name)
        do = float(exterior)
        n = coil_number
        self.do = do
        self.n = n
        pitch = line_width+spacing
        self.di = do-2.*pitch*n


        ##################
        # Spiral
        ##################


        spiral = cad.core.Elements()
        points = [[0,0]]
        for i in range(n-1):
          points.append([i*pitch,-do+i*pitch])
          points.append([do-i*pitch,-do+i*pitch])
          points.append([do-i*pitch,-i*pitch])
          points.append([(i+1)*pitch,-i*pitch])
        points.append([(n-1)*pitch,-do+(n-1)*pitch])
        points.append([do-(n-1)*pitch,-do+(n-1)*pitch])
        points.append([do-(n-1)*pitch,-do/2.])
        points.append([do/2.,-do/2.])
        spiral.add(cad.core.Path(points, line_width,layer = top_layer))


      # ##################
      # # Base layer
      # ##################


        overlap_square = cad.shapes.Rectangle((do/2.-overlap_square_width/2.,-do/2.-overlap_square_width/2.),\
         (do/2.+overlap_square_width/2.,-do/2.+overlap_square_width/2.), layer = base_layer)
        tail = cad.shapes.Rectangle((-tail_length,-do/2.+line_width),\
         (do/2.,-do/2.-line_width), layer = base_layer)


      # ##################
      # # Sacrificial layer
      # ##################

        sacrificial = cad.shapes.Rectangle((-tail_length,-do/2.+bridge_width/2.),\
         (do/2.-overlap_square_width/2.,-do/2.-bridge_width/2.), layer = sacrificial_layer)



        self.add([spiral,overlap_square,tail,sacrificial])

    def inductance(self):

        k1 = 2.34
        k2 = 2.75
        rho = (self.do-self.di)/(self.do+self.di)
        da = 0.5*(self.do+self.di)
        mu_0 = 4.*np.pi*1.e-7
        L = k1*mu_0*float(self.n)**2*da*1.e-6/(1+k2*rho)
        C = self.do*6.7e-15/40.
        print "L = " +str(L*1.e9) +" nH"
        print "C = " +str(C*1.e15) +" fF"
        print "(self-resonance) f = " +str(1./np.sqrt(L*C)/2./np.pi/1e9) +" GHz"


    def resonance(self, C):

        k1 = 2.34
        k2 = 2.75
        rho = (self.do-self.di)/(self.do+self.di)
        da = 0.5*(self.do+self.di)
        mu_0 = 4.*np.pi*1.e-7
        L = k1*mu_0*float(self.n)**2*da*1.e-6/(1+k2*rho)
        C_self = self.do*6.7e-15/40.
        print "f = " +str(1./np.sqrt(L*(C+C_self))/2./np.pi/1e9) +" GHz"