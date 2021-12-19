from gcode import GCode, UnseenFormatter

import numpy as np

class GCode_Contour_Rectangle(GCode):
    """ create a sharp cornerd rectangle """
 
    def __init__ (self, cfg, version="GCode_Contour_Rectange V0.1"):
        super().__init__(cfg, version)

    @staticmethod
    def createRectangle(self, x, y, depth, w, h, f, indent=3, helical=True):
        """create a rectant from position x/y with width and height and a depth for z of f

        Args:
            x ([type]): [start postion]
            y ([type]): [start position]
            z ([array]): [start_depth, end_depth, depth_step]
            w ([type]): [width ]
            h ([type]): [height]
            f ([type]): [movement speed]
            indent (int, optional): [description]. Defaults to 3.
        """
        x = round(float(x),4)
        y = round(float(y),4)

        z_offset = [0,0,0,0]
        z = depth[0]
        if depth[1] - depth[0] <= 0.0:
            z_offset = [depth[1],depth[1],depth[1],depth[1]]
        elif helical and depth[1] > 0.0:
            o = (depth[1]-depth[0]) / 4.0
            z_offset = np.arange (start=depth[0]+o,stop=depth[1], step=o)
            z_offset = np.append(z_offset, depth[1])  
        
        self.addGCode(self._cfg.GCODES['lin_move_xyzf'], args={'x':f"{x:.4f}",  'y':f"{(y+h):.4f}", 'z':f"{-z_offset[0]:.4f}", 'feed': f}, indent=indent )
        self.addGCode(self._cfg.GCODES['lin_move_xyzf'], args={'x':f"{x+w:.4f}",'y':f"{(y+h):.4f}", 'z':f"{-z_offset[1]:.4f}", 'feed': f}, indent=indent )
        self.addGCode(self._cfg.GCODES['lin_move_xyzf'], args={'x':f"{x+w:.4f}",'y':f"{(y):.4f}",   'z':f"{-z_offset[2]:.4f}", 'feed': f}, indent=indent )
        self.addGCode(self._cfg.GCODES['lin_move_xyzf'], args={'x':f"{x:.4f}",  'y':f"{(y):.4f}",   'z':f"{-z_offset[3]:.4f}", 'feed': f}, indent=indent )

    @staticmethod
    def helicalRecHole(self, xy, ab, wh, td, f, depth, contour='on', dir='CW'):
        """
        cut a rectangle hole with a width(w) and height(h). XY is the lower left corner to start

        Args:
            xy (float tuple): (x,y)
            ab (float tuple): (distance from 0,0 to cp 2, only used if cp = 0)
            wh ([float tuple]): [(width, height)]
            td ([float]): [tool diameter]
            f ([int]): [feed/speed]
            cp ([int]):  [center point (0,1,2)]
            depth (float tuple) : (depth_total, depth_step)
            contour (str, optional): [description]. Defaults to 'on'.
            dir (str, optional): [description]. Defaults to 'CW'.
        """
        # Step 1: starting xy position is allways lower left corner
        #
        if self.cp == '0' :
            # cutter is on machines 0/0 position
            xy[0] += ab[0]
            xy[1] += ab[1]
        elif self.cp == '1':
            # center of rectangle
            xy[0] -= (wh[0] / 2)
            xy[1] -= (wh[1] / 2)

        dr = self.getDepthStepRangeArray(depth)

        comment = f"-- helical rectangle start --"
        last_z = 0
        self.addComment(comment, leadingBlank=True, endingBlank=True)  

        if contour == 'outside':
            xy[0] -= (td / 2.0)
            xy[1] -= (td / 2.0)
            wh[0] += td # if we cut outside, width of rectangle is tool_diameter wider
            wh[1] += td # if we cut outside, height of rectangle is tool_diameter wider            
            pass
        elif contour == 'inside':
            xy[0] += (td / 2.0) # move 
            xy[1] += (td / 2.0)
            wh[0] -= td # if we cut outside, width of rectangle is tool_diameter smaller
            wh[1] -= td # if we cut outside, height of rectangle is tool_diameter smaller
            pass
        else:
            # 'on'
            pass 

        pass

        #
        # (loop)
        self.addGCode(self._cfg.GCODES['spindle_cw'])
        self.addGCode(self._cfg.GCODES['spindle_speed'],args={'speed':self.speed })
        self.addGCode(self._cfg.GCODES['feed_change'],args={'feed':self.rapid_move_xy })

        comment = f"Start milling"
        self.addComment(comment, leadingBlank=True, endingBlank=True)  
        #
        # Go to start position 
        self.addGCode(self._cfg.GCODES['rapid_move_zf'], args={'z':self.z_safety, 'feed':self.rapid_move_z})
        self.addGCode(self._cfg.GCODES['rapid_move_xyf'],args={'x':xy[0],  'y':xy[1], 'feed':self.rapid_move_xy})
        #
        # Start milling
        self.addGCode(self._cfg.GCODES['lin_move_zf'],args={'z':abs(self.z_start), 'feed':self.lin_move_z})

        comment = f"-- loop --"
        self.addComment(comment, leadingBlank=True, endingBlank=True)  
        last_z = 0
        self.addGCode(self._cfg.GCODES['lin_move_xyzf'],args={'x':xy[0], 'y':xy[1], 'z':-0, 'feed': self.lin_move_xy}, indent=3 )
        for z in dr:
            comment = f"-- depth {z} --"
            self.addComment(comment, leadingBlank=True, endingBlank=True)  
            if self.dir == 'CW':
                self.createRectangle(self, x=xy[0], y=xy[1], depth=[last_z, z, self.depth_step], w=wh[0], h=wh[1], f=f, indent=3)
            last_z = z
            pass
        comment = f"-- endloop --"
        self.addComment(comment, leadingBlank=True, endingBlank=True)  
        #self.createRectangle(self, x=xy[0], y=xy[1], depth=[last_z,self.depth_total, self.depth_step], w=wh[0], h=wh[1], f=f, indent=3, helical=False)

    def generateGcode(self, data):
        """[summary]
        {'pre_gcode': 'G90 G64 G17 G40 G49', 'post_gcode': 'G00 Z10 F100 M2', 
        'center_point': '1', 
        'unit': 'mm', 'direction': 'CCW', 
        'cutter_compensation': 'on', 'depth_step': '0.5', 'depth_total': '33', 
        'feed_g00_xy': '600', 'feed_g00_z': '400', 'feed_g01_xy': '300', 'feed_g01_z': '15', 
        'z_start': '3.0', 'z_safety': '15.0', 
        'tool_dia':'3.0',
        'tool_id' : '1',
        'speed' : '20000',
        ---- specific from project -----
        'width' : '20',
        'height' : '10'
        }
        Args:
            data ([type]): [description]
        """

        width       = float(data['width'])
        height      = float(data['height'])

        xy = [0,0]
        (xy, tool_comp, range) = self.addStandardGCodes(
            data,
            comments= {
                "intro" : {
                    "text" : 'GCode_Contour_Rectangle. Version {0} - {1}',
                    "args" : [
                        "V0.1", 
                        "12-2021"
                        ]
                },
                "c1" : {
                    "text" : 'Rectangle with a width of {0} and a height of {2}{1}, milling contour {3}, cutting direction {3}',
                    "args" : [
                        width, 
                        data['unit'] , 
                        height,
                        data['cutter_compensation'],
                        data['direction']
                        ]
                }
            }
        )

        # call static method, note: it's important to send current object as well to method
        self.helicalRecHole( self,
            xy=xy, 
            ab=[self.center_offset_x, self.center_offset_y],
            wh=[width, height],
            td=self.tool_dia,
            f=self.lin_move_xy,
            depth=[self.depth_total, self.depth_step],
            contour=self.contour,
            dir=self.dir
        )
    pass
pass

class GCode_Contour_RoundedRectangle(GCode):
    """ create a sharp cornerd rectangle """
 
    def __init__ (self, cfg, version="GCode_Contour_Rectange V0.1"):
        super().__init__(cfg, version)

    @staticmethod
    def createRoundedRectangle(self, x, y, depth, w, h, r, f, indent=3, helical=True):
        """create a rectant from position x/y with width and height and a depth for z of f

        Args:
            x ([type]): [start postion]
            y ([type]): [start position]
            z ([array]): [start_depth, end_depth, depth_step]
            w ([type]): [width ]
            h ([type]): [height]
            f ([type]): [movement speed]
            indent (int, optional): [description]. Defaults to 3.
        """
        x = round(float(x),4)
        y = round(float(y),4)

        z_offset = [0,0,0,0,0,0,0,0]
        z = depth[0]
        if depth[1] - depth[0] <= 0.0:
            z_offset = [depth[1],depth[1],depth[1],depth[1],depth[1],depth[1],depth[1],depth[1]]
        elif helical and depth[1] > 0.0:
            o = (depth[1]-depth[0]) / 8.0
            z_offset = np.arange (start=depth[0]+o,stop=depth[1], step=o)
            z_offset = np.append(z_offset, depth[1])  
        
        # start point 
        
        self.addGCode(self._cfg.GCODES['lin_move_xyzf'],    args={'x':f"{x:.4f}",       'y':f"{y:.4f}", 
            'z':f"{-z_offset[0]:.4f}", 'feed': f}, indent=indent )
        # 1. edge lower left; positiv I<value>
        x = w / 2.0
        y = h / 2.0 - r
        self.addGCode(self._cfg.GCODES['arc_int_cw_xyjz'],  args={'x':f"{-x:.4f}",      'y':f"{-y:.4f}", 
            'j':f"{abs(r):.4f}", 'z':f"{-z_offset[0]:.4f}"}, indent=indent )
        # 2. G01
        self.addGCode(self._cfg.GCODES['lin_move_xyz'],     args={'x':f"{-x:.4f}",      'y':f"{abs(y):.4f}", 
            'z':f"{-z_offset[1]:.4f}"}, indent=indent )
        # 3. G02 edge upper left
        x = w / 2.0 - r 
        y = h / 2.0
        self.addGCode(self._cfg.GCODES['arc_int_cw_xyiz'],  args={'x':f"{-x:.4f}",      'y':f"{abs(y):.4f}", 
            'i':f"{abs(r):.4f}", 'z':f"{-z_offset[2]:.4f}"}, indent=indent )
        # 4. G01
        self.addGCode(self._cfg.GCODES['lin_move_xyz'],     args={'x':f"{abs(x):.4f}",  'y':f"{abs(y):.4f}", 
            'z':f"{-z_offset[3]:.4f}"}, indent=indent )
        # 5. G02 edge upper right
        x = w / 2.0
        y = h / 2.0 - r
        self.addGCode(self._cfg.GCODES['arc_int_cw_xyjz'],  args={'x':f"{x:.4f}",       'y':f"{y:.4f}", 
            'j':f"{-r:.4f}", 'z':f"{-z_offset[4]:.4f}"}, indent=indent )
        # 6. G01
        self.addGCode(self._cfg.GCODES['lin_move_xyz'],     args={'x':f"{abs(x):.4f}",  'y':f"{-y:.4f}", 
            'z':f"{-z_offset[5]:.4f}"}, indent=indent )
        # 7. G02 edge lower right
        x = w / 2 - r
        y = h / 2 
        self.addGCode(self._cfg.GCODES['arc_int_cw_xyiz'],  args={'x':f"{x:.4f}",       'y':f"{-y:.4f}", 
            'i':f"{-r:.4f}", 'z':f"{-z_offset[6]:.4f}"}, indent=indent )
        # 8. G01
        self.addGCode(self._cfg.GCODES['lin_move_xyz'],     args={'x':f"{-x:.4f}",      'y':f"{-y:.4f}", 
            'z':f"{-z_offset[7]:.4f}"}, indent=indent )


    @staticmethod
    def helicalRoundedRecHole(self, xy, ab, wh, td, r, f, depth, contour='on', dir='CW'):
        """
        cut a rectangle hole with a width(w) and height(h). XY is the lower left corner to start

        Args:
            xy (float tuple): (x,y)
            ab (float tuple): (distance from 0,0 to cp 2, only used if cp = 0)
            wh ([float tuple]): [(width, height)]
            td ([float]): [tool diameter]
            r ([float]): [edge radius]
            f ([int]): [feed/speed]
            cp ([int]):  [center point (0,1,2)]
            depth (float tuple) : (depth_total, depth_step)
            contour (str, optional): [description]. Defaults to 'on'.
            dir (str, optional): [description]. Defaults to 'CW'.
        """
        # Step 1: starting xy position is allways lower left corner
        #
        # Math
        # a = width, b=height, r=radius
        # Example a=10, b=6, r=2.8)
        # ( x= b/2-r  => x = 6 / 2 = 3 - 2.8 = 0.2 )
        # ( G01 X0.2 Y....)
        # ( y= a/2-r  => y = 10 / 2 = 5 - 2.8 = 2.2 )
        # G02 X0.2 Y2.2


        if self.cp == '0' :
            # cutter is on machines 0/0 position
            xy[0] += ab[0]
            xy[1] += ab[1]
        elif self.cp == '1':
            # center of rectangle
            xy[0] -= (wh[0] / 2) - r
            xy[1] -= (wh[1] / 2)


        dr = self.getDepthStepRangeArray(depth)

        comment = f"-- helical rounded rectangle start --"
        last_z = 0
        self.addComment(comment, leadingBlank=True, endingBlank=True)  

        if contour == 'outside':
            xy[0] -= (td / 2.0)
            xy[1] -= (td / 2.0)
            wh[0] += td # if we cut outside, width of rectangle is tool_diameter wider
            wh[1] += td # if we cut outside, height of rectangle is tool_diameter wider            
            pass
        elif contour == 'inside':
            xy[0] += (td / 2.0) # move 
            xy[1] += (td / 2.0)
            wh[0] -= td # if we cut outside, width of rectangle is tool_diameter smaller
            wh[1] -= td # if we cut outside, height of rectangle is tool_diameter smaller
            pass
        else:
            # 'on'
            pass 

        pass


        #
        # (loop)
        self.addGCode(self._cfg.GCODES['spindle_cw'])
        self.addGCode(self._cfg.GCODES['spindle_speed'],args={'speed':self.speed })
        self.addGCode(self._cfg.GCODES['feed_change'],args={'feed':self.rapid_move_xy })

        comment = f"Start milling"
        self.addComment(comment, leadingBlank=True, endingBlank=True)  
        #
        # Go to start position 


        self.addGCode(self._cfg.GCODES['rapid_move_zf'], args={'z':self.z_safety, 'feed':self.rapid_move_z})
        self.addGCode(self._cfg.GCODES['rapid_move_xyf'],args={'x':xy[0],  'y':xy[1], 'feed':self.rapid_move_xy})
        #
        # Start milling
        self.addGCode(self._cfg.GCODES['lin_move_zf'],args={'z':abs(self.z_start), 'feed':self.lin_move_z})

        comment = f"-- loop --"
        self.addComment(comment, leadingBlank=True, endingBlank=True)  

        last_z = 0
        for z in dr:
            comment = f"-- depth {z} --"
            self.addComment(comment, leadingBlank=True, endingBlank=True)  
            if self.dir == 'CW':
                self.createRoundedRectangle(self, x=xy[0], y=xy[1], depth=[last_z, z, self.depth_step], w=wh[0], h=wh[1], r=r, f=f, indent=3)
            last_z = z
            pass
        comment = f"-- endloop --"
        self.addComment(comment, leadingBlank=True, endingBlank=True)  
        #self.createRectangle(self, x=xy[0], y=xy[1], depth=[last_z,self.depth_total, self.depth_step], w=wh[0], h=wh[1], f=f, indent=3, helical=False)

    def generateGcode(self, data):
        """[summary]
        {'pre_gcode': 'G90 G64 G17 G40 G49', 'post_gcode': 'G00 Z10 F100 M2', 
        'center_point': '1', 
        'unit': 'mm', 'direction': 'CCW', 
        'cutter_compensation': 'on', 'depth_step': '0.5', 'depth_total': '33', 
        'feed_g00_xy': '600', 'feed_g00_z': '400', 'feed_g01_xy': '300', 'feed_g01_z': '15', 
        'z_start': '3.0', 'z_safety': '15.0', 
        'tool_dia':'3.0',
        'tool_id' : '1',
        'speed' : '20000',
        ---- specific from project -----
        'width' : '20',
        'height' : '10'
        }
        Args:
            data ([type]): [description]
        """

        width       = float(data['width'])
        height      = float(data['height'])
        radius      = float(data['radius'])

        xy = [0,0]
        (xy, tool_comp, range) = self.addStandardGCodes(
            data,
            comments= {
                "intro" : {
                    "text" : 'GCode_Contour_RoundedRectangle. Version {0} - {1}',
                    "args" : [
                        "V0.1", 
                        "12-2021"
                        ]
                },
                "c1" : {
                    "text" : 'Rounded rectangle with a width of {0} and a height of {2}{1} and edge radius {3}',
                    "args" : [
                        width, 
                        data['unit'] , 
                        height,
                        radius
                        ]
                }
            }
        )

        # call static method, note: it's important to send current object as well to method
        self.helicalRoundedRecHole( self,
            xy=xy, 
            ab=[self.center_offset_x, self.center_offset_y],
            wh=[width, height],
            td=self.tool_dia,
            r=radius,
            f=self.lin_move_xy,
            depth=[self.depth_total, self.depth_step],
            contour=self.contour,
            dir=self.dir
        )
    pass
pass

