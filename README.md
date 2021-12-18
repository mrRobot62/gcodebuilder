# GCodeGenerator2 / GCode-Builder
 !!!!! under construction !!!!
 
 Initial version (V01) generate GCode for  
 * milling contour circels
 * milling contour circel arcs
 * milling rectangles
 
 # History
 | Date | Version | Info |
 | :-: | :-: | --- |
 |15 dec 2021| 0.1 | Initial upload |
 ||||
 ||||
 
 # Abstract
This web based tool suite create a couple of different gcode squences like
* Contour-Tools
    * Milling circles
    * Milling arcs 
    * Milling rectangles
    * Milling rounded rectangles
* Pockets
    * Milling circle pockets
    * Milling rectangle pockets
* Slots
    * Milling slots
* Surface
    * plan surface

## Quick Overview
some screenshots

[]<img width="1437" alt="overview1" src="https://user-images.githubusercontent.com/949032/146629773-8bb1376d-4f1f-4eed-8d5c-85e725da2468.png">


## Deepe Dive
see wiki


# Development
# Language translations

### Extract all texts for translations
Scan folder structur for files which contains messages to translate
Babel create a message.pot file. This file can be recompiled as often it's needed.
Exclude this file from versioning

`pybabel extract -F babel.cfg -o messages.pot .`

### Initialize language 
For every language we need a translation file. Parameter -l <language> indicates, which language file is created. It's an copy of message.pot and can be used for translations.
Babel create a new translation folder and insert a message.po file.

`pybabel init -i messages.pot -d app/translations -l de`

### Compile translations for using
If all translations done, compile them for the application. This binary file is a runtime version for text.

`pybabel compile -d app/translations`

