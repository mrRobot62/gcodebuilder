# GCodeGenerator2 / GCode-Builder
 !!!!! under construction !!!!
 
 Initial version (V01) generate GCode for  
 * Language English/German
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

### Overview
[]<img width="1437" alt="overview1" src="https://user-images.githubusercontent.com/949032/146629773-8bb1376d-4f1f-4eed-8d5c-85e725da2468.png">

### Contour milling
<img width="1437" alt="overview_contour" src="https://user-images.githubusercontent.com/949032/146629823-0e739bea-b456-489a-9e13-7b5b233c4967.png">

### Contour Circles
<img width="1437" alt="overview_contour_circle" src="https://user-images.githubusercontent.com/949032/146629834-dcc60088-8a33-415e-a087-e34aa462993d.png">

<img width="1016" alt="overview_std_prepost" src="https://user-images.githubusercontent.com/949032/146629995-2e783041-9b4f-42e6-93c0-49f172c374d2.png">

<img width="1016" alt="overview_std_params" src="https://user-images.githubusercontent.com/949032/146630008-eb49183e-7db2-4f03-ba61-dce752138771.png">

<img width="1016" alt="overview_std_material" src="https://user-images.githubusercontent.com/949032/146630014-b0c6fed5-af6c-43f1-a153-d5b4bacd6179.png">

<img width="1016" alt="overview_std_specific_arc" src="https://user-images.githubusercontent.com/949032/146630016-948c0170-4952-4f5c-9f55-5b77a7a0f518.png">


### Generated GCode
<img width="1437" alt="overview_gcode" src="https://user-images.githubusercontent.com/949032/146629846-98f356c7-69ee-4a1c-8c75-ae19af0e32aa.png">


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

