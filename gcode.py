# https://linuxcnc.org/docs/html/gcode/g-code.html#gcode:g0

from abc import ABC, abstractmethod
from string import Formatter 
import numpy as np 
import math

class UnseenFormatter(Formatter):
    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            try:
                return kwds[key]
            except KeyError:
                return key
        else:
            return Formatter.get_value(key, args, kwds)

class GCode(ABC):
    def __init__(self, cfg, version):
        """Constructor


        Args:
            cfg ([type]): [description]
        """
        self._cfg = cfg

        # internally we store the gcodes inside an arry.
        self.gcode= []
        self.addGCode(self._cfg.GCODES["percent"])
        self.version = version
        self.fmt = UnseenFormatter()
        pass

    def getGCode(self):
        self.addGCode()

    def addPreamble(self, data=""):
        self.addComment(self._cfg.VERSION, leadingBlank=True, endingBlank=True)
        self.addComment("- PreAmble ----------------------")
        self.addGCode(data)
        self.addComment("---------------------------------")

    def addPostamble(self, data=""):
        self.addComment("- PostAmble ---------------------")
        self.addGCode(data)
        self.addComment("---------------------------------")
        self.addGCode(self._cfg.GCODES["percent"], indent=0)

    def setToolID(self, id=0):
        self.addComment("-Set Tool -----------------------")
        if (id <= 0) or (id > 99):
            id = 0
        self.addGCode(self._cfg.GCODES["tool_set"], args={"id":str(id)})
        self.addComment("---------------------------------")

    def getDepthStepRangeArray(self, depth):
        """create a numpy array based on depth_total and depth_step.

        Args:
            depth ([float tupel]): [(depth_total, depth_step)]

        Return:
            np.array
        """
        dr = np.arange(0.0, depth[0], depth[1])
        # insert a last cutting row, to avoid unsmooth last 
        dd = depth[0] - dr.max()
        # if max value of array is less than depth total, insert depth_total 
        if dd >= 0.0:
            dr = np.append(dr, depth[0])
        # due to a helical circel it smoother to put max() value again to array
        # than during milling this last step is done twice
        dr = np.append(dr, depth[0])
        return dr


    def addComment(self, comment, indent=0, leadingBlank=False, endingBlank=False):
        """create a comment line

        Args:
            comment ([type]): commend
            indent (int, optional): append spaces left side. Defaults to 0.
            leadingBlank ([Bool]): if true, than a blank is set before text
            endingBlank ([Bool]): if true, than a blank is set at the end of text

        """
        indent = 0 if indent <= 0 else indent
        space = "".ljust(indent, ' ')
        if leadingBlank:
            comment = comment.rjust(len(comment)+1,' ')
        if endingBlank:
            comment = comment.ljust(len(comment)+1,' ')

        data = f"({comment})"
        data = f"{space}{data}"
        self.gcode.append(f"{space}{data}")

    def addGCode(self, gcode, args=None, indent=0):
        """[add new data to current gcode]

        Args:
            args ([dict]) : dictionary contain paraemters for gcode e.g. {"x":10, "y":15} and gcode is "G0 X{x} Y{y}" will produce G0 X10 Y15
            gcode ([string]): [new gcode sequence, if args<>None, than gcode is a meta definition from config.py]
            indent (int, optional): [if set, add spaces left]. Defaults to 0.
        """
        indent = 0 if indent <= 0 else indent
        space = "".ljust(indent, ' ')
        if args is None:
            tmp = space + gcode
        else:
            tmp = space + self.fmt.format(gcode, **args)

        self.gcode.append(tmp)
       
    @abstractmethod
    def generateGcode(self, data):
        """ this method should be implemented inside subclass. Depending on subclass, this method create a gcode sequence 

        Args:
             data ([dict]): [contains request form data. Field name = key]
        """
        pass

    def setObjectData(self, data):
         # save data into variables which are mostly used in sub classes
        # below variables are standard variables in all milling projects
        self.center_offset_x = 0    #
        self.center_offset_y = 0    # only used, if user set center point to 0
        self.contour        = data['cutter_compensation']
        self.cp             = data['center_point']
        self.data           = data 
        self.depth_total    = float(data['depth_total'])
        self.depth_step     = float(data['depth_step'])
        self.dir            = data['direction']
        self.lin_move_xy    = float(data['feed_g01_xy'])
        self.lin_move_z     = float(data['feed_g01_z'])
        self.rapid_move_xy  = float(data['feed_g00_xy'])
        self.rapid_move_z   = float(data['feed_g01_z'])
        self.speed          = int(data['speed'])
        self.unit           = data['unit']
        self.tool_dia       = float(data['tool_dia'])
        self.tool_id        = int(data['tool_id'])
        self.z_safety       = float(data['z_safety'])
        self.z_start        = float(data['z_start'])
       

    def addStandardGCodes(self, data, comments=None):
        """ 
        create standard GCode squences which are used by most projects.
        Method create standard variables for projects based on form standard input fields

        {'pre_gcode': 'G90 G64 G17 G40 G49', 'post_gcode': 'G00 Z10 F100 M2', 
        'center_point': '1', 
            if center_point == 0, 'center_offset_x' : '0', 'center_offset_y':'0'
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
            data ([type]): [request.form data]
            comments (list, optional): [description]. Defaults to [].

        Return:
            xy (array): 0 = x, 1 = Y
            tool_comp (int): radius of tool_diameter
            range (array): list of z depth 
        """


        # save data into variables which are mostly used in sub classes
        # below variables are standard variables in all milling projects
        self.center_offset_x = 0    #
        self.center_offset_y = 0    # only used, if user set center point to 0
        self.contour        = data['cutter_compensation']
        self.cp             = data['center_point']
        self.data           = data 
        self.depth_total    = float(data['depth_total'])
        self.depth_step     = float(data['depth_step'])
        self.dir            = data['direction']
        self.lin_move_xy    = float(data['feed_g01_xy'])
        self.lin_move_z     = float(data['feed_g01_z'])
        self.rapid_move_xy  = float(data['feed_g00_xy'])
        self.rapid_move_z   = float(data['feed_g01_z'])
        self.speed          = int(data['speed'])
        self.unit           = data['unit']
        self.tool_dia       = float(data['tool_dia'])
        self.tool_id        = int(data['tool_id'])
        self.z_safety       = float(data['z_safety'])
        self.z_start        = float(data['z_start'])

        xy = [0,0]
        comment_width = self._cfg.MAX_LINE_WIDTH - 2
        self.addComment("".ljust(comment_width,'*'))
        if 'comments' !=  None:
            if 'intro' in comments:
                comment = comments['intro']['text']
                args = comments['intro']['args']
                msg = comment.format(*args)
                self.addComment(msg, leadingBlank=True, endingBlank=True)
                pass
            if 'c1' in comments:
                comment = comments['c1']['text']
                args = comments['c1']['args']
                msg = comment.format(*args)
                self.addComment(msg, leadingBlank=True, endingBlank=True)
                pass
            if 'c2' in comments:
                comment = comments['c2']['text']
                args = comments['c2']['args']
                msg = comment.format(*args)
                self.addComment(msg, leadingBlank=True, endingBlank=True)
                pass
            if 'c3' in comments:
                comment = comments['c3']['text']
                args = comments['c3']['args']
                msg = comment.format(*args)
                self.addComment(msg, leadingBlank=True, endingBlank=True)
                pass
            if 'c4' in comments:
                comment = comments['c4']['text']
                args = comments['c4']['args']
                msg = comment.format(*args)
                self.addComment(msg, leadingBlank=True, endingBlank=True)
                pass
            if 'c5' in comments:
                comment = comments['c5']['text']
                args = comments['c5']['args']
                msg = comment.format(*args)
                self.addComment(msg, leadingBlank=True, endingBlank=True)
                pass

        # default comment in all milling projects
        args = [self.contour, self.depth_total, self.depth_step]
        comment = 'Milling contour {0}, total depth {1} and a depth step {2}'
        msg = comment.format(*args)
        self.addComment(msg, leadingBlank=True, endingBlank=True)

        self.addComment("".ljust(comment_width,'*'))
        depth_range = np.arange(0.0, (self.depth_total + self.depth_step), self.depth_step)
        self.addPreamble(data['pre_gcode'])

        self.setToolID(self.tool_id)
 
        # rapid move to center position
        if data['center_point'] == '0':
            self.center_offset_x = float(data['center_offset_x'])
            self.center_offset_y = float(data['center_offset_y'])
            xy = [self.center_offset_x, self.center_offset_y]
            pass
        elif data['center_point'] == '1':
            # we assume, that 0,0 is the center of the object
            xy = [0,0]
            pass
        self.addGCode(self._cfg.GCODES['rapid_move_zf'],args={'z':self.z_safety, 'feed': self.rapid_move_z })
        self.addGCode(self._cfg.GCODES['rapid_move_xyf'],args={'x':xy[0], 'y':xy[1], 'feed': self.rapid_move_xy})

        # save xy into tool compensation
        xy_comp = xy.copy()
        #
        # for tool compensation we need the radius from tool_diameter
        tool_comp = 0
        if data['cutter_compensation'] == '':
            # on contour
            pass
        elif data['cutter_compensation'] == 'left':
            # left
            tool_comp = self.tool_dia / 2
            pass
        elif data['cutter_compensation'] == 'right':
            # inside (right)         
            tool_comp = self.tool_dia / 2
            pass
        
        
        return (xy, tool_comp, depth_range)

    def getGcode(self, linebreak):
        """return from internal gcode list a list of gcodes with linebreaks

        Args:
            linebreak ([string]): ['ascii' or 'html']
        """
        lb = ""
        if linebreak in self._cfg.LINEBREAK:
            lb = self._cfg.LINEBREAK[linebreak]
        return lb.join(self.gcode)

    def finish(self, x, y):
        """set finishing, move z-axis to safety hight and create post_gcode sequence
        """
        self.addComment('**** finish ****')

        self.addGCode(self._cfg.GCODES['rapid_move_zf'], args={'z':self.z_safety, 'feed':self.rapid_move_z })
        self.addGCode(self._cfg.GCODES['rapid_move_xyf'], args={'x':x, 'y':y, 'feed':self.rapid_move_xy })

        self.addPostamble(self.data['post_gcode'])


    def getSnippet(self, snippet):
        """return a snippet string.
        Read config.py, read dictionary "gcode_snippets" and return gcode_snippets[snippet]

        Args:
            sippet ([string]): [Name of snippet]
        """
        if snippet in self._cfg.GC_SNIPPETS:
            return self._cfg.GC_SNIPPETS[snippet]
        else:
            return None
