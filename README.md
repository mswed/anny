# Anny - A slightly better RV annotation tool 
Anny is a ShotGrid RV annotation tool with better tools and, hopefully, better user experience than the builtin tool. 

## What Anny can do 

### Draw freehand 
- Smooth the line so drawing with the mouse looks better 

### Draw straight lines
- Put an arrow, a circle or a measurement tick at the end and/or start of a line 
- Add some text to the middle of a line 

### Draw shapes
- Draw rectangles with separate settings for stroke and fill 
- Draw circles/ellipses 

### Draw text 
- Drag to set a text container 
- The container extends vertically as you type so you don't lose any text 
- Text can be edited

### Edit annotations 
- All annotations can be moved around 
- Straight lines and shapes start and end points can be moved independantly to edit the shape 
- Single annotations can be deleted from the frame 
- All annotations can be deleted from the frame 

### Export annotations 
- Export a single annotation as jpg or png 
- Export all annotations to a user specified folder 

## What Anny will do later

## Undo strokes 
Add an undo/redo queue and hopefully bind it to ctrl + z

### Upload notes to ShotGrid
The default SG RV integration note upload is dependant on RV paint nodes and a separate rendering process that Anny can not replicate. 
So an additional system will be added to upload notes directly to SG  

### Save user preferences 
Add the ability to set default color, width caps and text to all annotations 


## What Anny will likely never do
### Work in RV sync 
RV sync uses RV paint nodes to draw and serialize strokes. Anny stroke system is not competable with this workflow. 
### Fix the creeping sense that the VFX industry is doomed 

## Installation 
Anny is installed like any RV package. 
1. Download the rvpkg file 
2. In RV go to RV -> Preferences -> Packages 
3. Click Add package 
4. Navigate to where you downloaded the package and select it 
5. Checkmark installed and load 
6. Relaunch RV 
7. You should now have an Anny menu
 

## Development 
The setup a development en
