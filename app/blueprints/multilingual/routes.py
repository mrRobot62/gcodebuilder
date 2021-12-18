from flask import (render_template, Blueprint, g, redirect, Response,
                   request, current_app, abort, url_for, jsonify)
from flask_babel import _
from marshmallow import Schema, fields, validates, ValidationError
from config import Config as cfg
from gcode_contour_circles import GCode_Contour_Circle 
from gcode_contour_circles import GCode_Contour_Arc
from gcode_contour_rectangles import GCode_Contour_Rectangle 
from gcode_contour_rectangles import GCode_Contour_RoundedRectangle 

from app import app
import json

# By adding a url_prefix to the blueprint, we can tell the route to expect a 
# language code in the first part of the URL.
multilingual = Blueprint('multilingual', __name__,
                         template_folder='templates', url_prefix='/<lang_code>')


buttons = ["btn_gen_gcode","btn_save_gcode","btn_close_gcode"]

def load_defaults():
    try:
        j = {}
        fname = './defaults.json'
        with open(fname ) as f:
            j = json.load(f)
    except Exception as err:
        print (f"Error: {fname} file not found")
        sys.exit(1)
    return j

def load_materials():
    try:
        j = {}
        fname = './materials.json'
        with open(fname ) as f:
            j = json.load(f)
    
    except Exception as err:
        print (f"Error: {fname} file not found")
        sys.exit(1)
    return j

def request2json(data):
    d = {}
    for k,v in data.items():
        d[k] = v

    return d

def returnButtonClicked(data):
    """return a tuple with button and boolean which button was clicked
    
    Args:
        data ([request.form]): [description]
    """
    for b in buttons:
        if b in data:
            return (b, True)
    return (None, None)



'''
The method add_language_code() is mainly responsible for providing a default 
language code for all url_for() calls in our application in case the language 
code is not specifically defined. This means that if we add a 
url_for('multilingual.contour') call in the template, and our current language 
is German, we will get the German version of the contour website and not the 
English one.
'''
@multilingual.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

'''
The second method pull_lang_code() takes the language code out of our request 
and into the g variable. Since our endpoints are not expecting any variables 
passed to them we just handle the URL prefix in this manner and now Babel 
can access the language and serve content respectively.
'''
@multilingual.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@multilingual.before_request
def before_request():
    if g.lang_code not in current_app.config['LANGUAGES']:
        adapter = app.url_map.bind('')
        try:
            endpoint, args = adapter.match(
                '/en' + request.full_path.rstrip('/ ?'))
            return redirect(url_for(endpoint, **args), 301)
        except:
            abort(404)

    dfl = request.url_rule.defaults
    if 'lang_code' in dfl:
        if dfl['lang_code'] != request.full_path.split('/')[1]:
            abort(404)


@multilingual.route('/')
@multilingual.route('/index')
def index():
    return render_template('multilingual/index.html', title=_('Home'))



#------- routes for contours

@multilingual.route('/contour', methods=['GET','POST'])
def contour():
    return render_template('multilingual/contour/contour.html', title=_('Contour'))

@multilingual.route('gcode_view.html', methods=['GET','POST'])
def gcode_editor():
    save_data = None
    if request.methode == 'POST':
            
            pass   

@multilingual.route('downloadGCode')
def downloadGCode():
    gcode = "M2"
    return Response(
        gcode,
        mimetype = "text/text",
        headers={"Content-disposition":
                 "attachment; filename=gcode.nc"}
        )



@multilingual.route('/contour/circle360', methods=['GET','POST'])
def circle360():
    defaults = load_defaults()
    defaults['usexy'] = True
    save_data = None
    if request.method == 'POST':
        data = request2json(request.form)
        (btn, clicked) = returnButtonClicked(request.form)
        if btn == "btn_gen_gcode":
            gcgen = GCode_Contour_Circle(cfg)
            data = gcgen.generateGcode(data)
            data = gcgen.getGcode('ascii')
            sava_data = data
            return render_template('multilingual/gcode_view.html', title=_('GCode Editor'), data=data)
        if btn == "btn_save_gcode":
            return render_template('multilingual/gcode_view.html', title=_('GCode Editor'), data=sava_data)
    else:
        return render_template('multilingual/contour/circle360.html', title=_('Circle 360'), data=defaults)

@multilingual.route('/contour/circlearc', methods=['GET','POST'])
def circlearc():
    defaults = load_defaults()
    # add other center points
    defaults['cp']['2'] = False
    if request.method == 'POST':
        data = request2json(request.form)
        (btn, clicked) = returnButtonClicked(request.form)
        if btn == "btn_gen_gcode":
            gcgen = GCode_Contour_Arc(cfg)
            data = gcgen.generateGcode(data)
            data = gcgen.getGcode('ascii')
            return render_template('multilingual/gcode_view.html', title=_('GCode Editor'), data=data)
    else:
        return render_template('multilingual/contour/circlearc.html', title=_('Circle arc'), data=defaults)

@multilingual.route('/contour/rectangle', methods=['GET','POST'])
def rectangle():
    defaults = load_defaults()
    # add other center points
    defaults['cp']['2'] = False
    save_data = None
    if request.method == 'POST':
        data = request2json(request.form)
        (btn, clicked) = returnButtonClicked(request.form)
        if btn == "btn_gen_gcode":
            gcgen = GCode_Contour_Rectangle(cfg)
            data = gcgen.generateGcode(data)
            data = gcgen.getGcode('ascii')
            save_data = data
            return render_template('multilingual/gcode_view.html', title=_('GCode Editor'), data=data)
    else:
        return render_template('multilingual/contour/rectangle.html', title=_('rectangle'), data=defaults)

@multilingual.route('/contour/rectanglerounded', methods=['GET','POST'])
def rectanglerounded():
    defaults = load_defaults()
    # add other center points
    defaults['cp']['2'] = False
    if request.method == 'POST':
        data = request2json(request.form)
        (btn, clicked) = returnButtonClicked(request.form)
        if btn == "btn_gen_gcode":
            gcgen = GCode_Contour_RoundedRectangle(cfg)
            data = gcgen.generateGcode(data)
            data = gcgen.getGcode('ascii')
            save_data = data
            return render_template('multilingual/gcode_view.html', title=_('GCode Editor'), data=data)

        pass
    else:
        return render_template('multilingual/contour/rectanglerounded.html', title=_('rectanglerounded'), data=defaults)

#------- routes for surfaces


@multilingual.route('/surface', methods=['GET','POST'])
def surface():
    return render_template('multilingual/surface/surface.html', title=_('Surface'))


#------- routes for pockets
@multilingual.route('/pocket', methods=['GET','POST'])
def pocket():
    return render_template('multilingual/pocket/pocket.html', title=_('Pocket'))

@multilingual.route('/drilling', methods=['GET','POST'])
def drilling():
    return render_template('multilingual/drilling/drilling.html', title=_('Drilling'))

#-------- Routes for calculations AJAX -------------
@multilingual.route('/addxy', methods=['GET','POST'])
def addxy():
    if request.method == "POST":
        pass
    return "addxy"
