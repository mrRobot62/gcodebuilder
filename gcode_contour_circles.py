from gcode import GCode, UnseenFormatter


class GCode_Contour_Circle(GCode):
    """ create a circle contour """
    def __init__ (self, cfg, version="GCode_Contour_Circle V0.1"):
        super().__init__(cfg, version)

    @staticmethod
    def helicalHole(self, x, y, i, j, r, td, f, dt, ds, contour='on', dir='CW'):
        """[create a helical hole ]

        Args:
            x ([float]): [center x]
            y ([float]): [center y]
            i ([float]): [i value]
            j ([float]): [j value]
            r ([float]): [radius]
            td ([float]): [tool diameter]
            f ([float]): [feed]
            dt ([float]): [depth total]
            ds ([float]): [depth step]
            contour (str, optional): [description]. Defaults to 'on'.
            dir (str, optional): [description]. Defaults to 'CW'.
        """
        """
        dr = np.arange(0.0, dt, ds)
        dd = dt - dr.max()
        # if max value of array is less than depth total, insert depth_total 
        if dd >= 0.0:
            dr = np.append(dr, (dt))
        # due to a helical circel it smoother to put max() value again to array
        # than during milling this last step is done twice
        dr = np.append(dr, (dt))
        """
        dr = self.getDepthStepRangeArray((dt, ds))

        comment = f"-- helical hole start --"
        last_z = 0
        self.addComment(comment, leadingBlank=True, endingBlank=True)  

        # calculate start position
        # x position + radius (set Cutter to right)
        # y position is not changed
        x += r 

        ic = i # tool compensation
        jc = j # tool compensation
        if contour == 'on':
            pass 
        elif contour == 'outside':
            ic += td / 2.0
            x += td / 2.0
        elif contour == 'inside':
            ic -= td / 2.0
            x -= td / 2.0
        #
        # go to start position
        # independend if CW or CCW, we start from x + radisu
        self.addGCode(self._cfg.GCODES['lin_move_xyf'], args={'x':x, 'y':y , 'feed':f })
        self.addGCode(self._cfg.GCODES['lin_move_zf'],  args={'z':0, 'feed':f })

        for z in dr:
            # first item in dr-array is allways 0. so first milling arc is at z0 and than we start to go deeper
            # last two items are allways at the same z position, this is to avoid an unsmooth end shape
            if dir == 'CW':
                # note if CW than I-Value is negativ
                self.addGCode(self._cfg.GCODES['arc_int_cw_ijz'],args={'i':-abs(ic), 'j':-abs(jc), 'z':-z}, indent=3 )
            else:
                # note if CCW than I-Value is positiv
                self.addGCode(self._cfg.GCODES['arc_int_ccw_ijz'],args={'i':-abs(ic), 'j':-abs(jc), 'z':-z}, indent=3)           
            last_z = z
            pass

        comment = f"-- helical hole end --"
        self.addComment(comment, leadingBlank=True, endingBlank=True)  
        pass


    def generateGcode(self, data):
        """
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
        'diameter' : '12'
        }

        Args:
            data ([type]): [description]
        """
        xy = [0,0]

        diameter    = float(data['diameter'])
        radius      = diameter / 2.0

        (xy, tool_comp, range) = self.addStandardGCodes(
            data,
            comments= {
                "intro" : {
                    "text" : 'GCode_Contour_Circle. Version {0} - {1}',
                    "args" : [
                        "V0.1", 
                        "12-2021"
                        ]
                },
                "c1" : {
                    "text" : 'Helical circle diameter {0}{1}, milling contour {2}, cutting direction {3}',
                    "args" : [
                        data['diameter'], 
                        data['unit'] , 
                        data['cutter_compensation'],
                        data['direction']
                        ]
                }
            }
        )

        comment = f"Start project milling"
        self.addComment(comment, leadingBlank=True, endingBlank=True)  
        #

        x = xy[0]
        y = xy[1]
        r = float(data['diameter']) / 2.0
        td = float(data['tool_dia'] )

        i = r 
        j = 0

        f = self.lin_move_xy 
        dt = self.depth_total
        ds = self.depth_step
        #
        # let's use the statci method
        self.helicalHole(self, x, y, i, j, r, td, f, dt, ds, self.contour, self.dir)
        self.finish(0,0)
        pass

class GCode_Contour_Arc(GCode):
    """ create a sharp cornerd rectangle """
 
    def __init__ (self, cfg, version="GCode_Contour_Circle V0.1"):
        super().__init__(cfg, version)

    @staticmethod
    def generateArcGCode(self, xy, radius, start_end_angle, td, f, depth, contour='on', dir='CW'):
        """[summary]

        Args:
            xy ([array]): [x,y]
            radius ([type]): [radius of arc]
            start_end_angle ([array]): [[angle_left, angle_right]
            td ([type]): [tool diameter]
            f ([type]): [feed]
            depth ([type]): [depth_totoal, depth_step]
            contour (str, optional): ['on', 'outside', 'inside']. Defaults to 'on'.
            dir (str, optional): ['CW', 'CCW']. Defaults to 'CW'.
        """
        dr = self.getDepthStepRangeArray(depth)

        # p1 = start point (used with G00/G01)
        # p2 = end point (used with G02)

        if contour == "inside":
            radius -= float(td/2.0)
        elif contour == "outside":
            radius += float(td/2.0)
        
        p1_x = round(radius * math.cos(math.radians(start_end_angle[0])),5)
        p1_y = round(radius * math.sin(math.radians(start_end_angle[0])),5)
        p2_x = round(radius * math.cos(math.radians(start_end_angle[1])),5)
        p2_y = round(radius * math.sin(math.radians(start_end_angle[1])),5)

        comment = f"contour = {contour}, new radius = {radius} with calculated tool diameter {td}/2"
        last_z = 0
        self.addComment(comment, leadingBlank=True, endingBlank=True)  

        comment = f"-- create an arc --"
        last_z = 0
        self.addComment(comment, leadingBlank=True, endingBlank=True)  
        for z in dr:
            comment = f"-- z={z} --"
            self.addComment(comment, leadingBlank=True, endingBlank=True, indent=3)  
            # go to start position
            self.addGCode(
                self._cfg.GCODES['rapid_move_xyzf'],
                args={'x':p1_x, 'y':p1_y, 'z':self.z_start, 'feed':self.rapid_move_xy},
                indent=3
            )           
            self.addGCode(
                self._cfg.GCODES['lin_move_zf'],
                args={'z':-z, 'feed':self.lin_move_xy},
                indent=3
            )
            self.addGCode(
                self._cfg.GCODES['arc_int_cw'],
                args={'x':p2_x, 'y':p2_y, 'i':(p1_x * -1), 'j':(p1_y*-1), 'z':-z}, 
                indent=3
            )
            self.addGCode(
                self._cfg.GCODES['lin_move_zf'],
                args={'z':self.z_start, 'feed':self.rapid_move_z},
                indent=3
            )
            last_z = z
        pass  

    def generateGcode(self, data):

        radius = data['radius']
        angle_start = data['angle_start']
        angle_end = data['angle_end']

        self.setObjectData(data)

        xy = [0,0]
        (xy, tool_comp, range) = self.addStandardGCodes(
            data,
            comments= {
                "intro" : {
                    "text" : 'GCode_Contour_Arc. Version {0} - {1}',
                    "args" : [
                        "V0.1", 
                        "12-2021"
                        ]
                },
                "c1" : {
                    "text" : 'Start at angle w1 {0}° and end at angle {1}° and radius {2}',
                    "args" : [
                        angle_start, 
                        angle_end, 
                        radius
                        ]
                },
                "c2" : {
                    "text" : 'cutting depth {0} with step rate {1}, milling contour {2}, cutting direction {3}',
                    "args" : [
                        self.depth_total,
                        self.depth_step,
                        self.contour,
                        self.dir
                        ]
                }
            }
        )
        self.generateArcGCode(self, 
            xy=xy,
            radius=round(float(radius),4),
            start_end_angle=[float(angle_start), float(angle_end)],
            td=float(self.tool_dia),
            f=self.lin_move_xy,
            depth=[float(self.depth_total), float(self.depth_step)],
            contour=self.contour,
            dir=self.dir
        )
        self.finish(0,0)

        pass

    pass
pass

