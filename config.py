class Config(object):
    VERSION = "GCode Generator LunaX V0.1 2021-2022"
    DEBUG = True
    LANGUAGES = ['en', 'de']
    LINEBREAK = {'ascii':'\n', 'html' :'<br>'}
    MAX_LINE_WIDTH = 80
    GCODES = {
            "arc_int_cw"        : "G2 X{x} Y{y} I{i} J{j}",
            "arc_int_cw_ijz"     : "G2 I{i} J{j} Z{z}",
            "arc_int_ccw_ijz"    : "G3 I{i} J{j} Z{z}",

            "comment"           : "( {comment} )",
            "cutter_comp_off"   : "G40",
            "cutter_comp_left"  : "G41", 
            "cutter_comp_right" : "G42", 
            "coolant_mist_on"   : "M7",
            "coolant_flood_on"  : "M8",
            "coolant_off"       : "M9",

            "feed_change"       : "F{feed}",

            "lin_move_xyf"       : "G1 X{x} Y{y} F{feed}",
            "lin_move_xyz"       : "G1 X{x} Y{y} Z{z}",
            "lin_move_xyzf"       : "G1 X{x} Y{y} Z{z} F{feed}",
            "lin_move_xy"       : "G1 X{x} Y{y}",
            "lin_move_zf"        : "G1 Z{z} F{feed}",
            "lin_move_z"        : "G1 Z{z}",

            "percent"           : "%",
            "program_end"       : "M2 (end)",

            "rapid_move_xyzf"     : "G0 X{x} Y{y} Z{z} F{feed}",
            "rapid_move_xyf"     : "G0 X{x} Y{y} F{feed}",
            "rapid_move_xy"     : "G0 X{x} Y{y}",
            "rapid_move_zf"      : "G0 Z{z} F{feed}",
            "rapid_move_z"      : "G0 Z{z}",

            "spindle_off"       : "M5 S0",
            "spindle_cw"        : "M3 (Spindle CW)",
            "spindle_ccw"       : "M4 (Spindle CCW)",
            "spindle_speed"     : "S{speed} (Spindle speed)",

            "tool_id"           : "T{0} (set tool)",

            "sub_call"          : "o{id} call",
            "sub_call_arg"      : "[{arg}] ",
            "sub_start"         : "o{id} sub",
            "sub_end"           : "o{id} endsub",
            "sub_cond_if"       : "o{id} if [{v1} {op} {v2}]",
            "sub_cond_else"     : "o{id} else",
            "sub_cond_elseif"   : "o{id} elseif [{v1} {op} {v2}]",
            "sub_cond_endif"    : "o{id} endif",
            "sub_repeat"        : "o{id} repeat [{v1}]",
            "sub_repeat_end"    : "o{id} endrepeat",
            "sub_do"            : "o{id} do",
            "sub_while"         : "o{id} while [{v1} {op} {v2}]",
            "sub_endwhile"      : "o{id} endwhile",
            "sub_op_AND"        : "AND",
            "sub_op_OR"         : "OR",
            "sub_op_XOR"        : "XOR",

            "sub_cond_EQ"       : "EQ",
            "sub_cond_NEQ"      : "NE",
            "sub_cond_GT"       : "GT",
            "sub_cond_GE"       : "GE",
            "sub_cond_LT"       : "LT",
            "sub_cond_LE"       : "LE",
            "sub_return"        :  "o{id} return",

            "tool_set"          : "T{id}"

        }

    GC_SNIPPETS = {
            "hole"    : """

    (Helix hole, with radius R and Z-Depth)
    o100 sub 
        (#1=CenterX, #2=CenterY, #3=StepSize, #4=Z-Depth, #5=Radius, #6=Speed)
        #99 = 0 (temp variable)
        G1 X[#1-#5] Y#2 Z0
        (loop until cutter is at Z-depth)
        o101 while [#99 LT #4]
            #99 = [#99+#3]
            G2 I#5 j#5 Z-#99
            (DEBUG, parameter 99 is [#99]
        o101 endwhile
        (do a plan round)
        G2 I#5 j#5 Z-#99
    o100 endsub 

            """
        }