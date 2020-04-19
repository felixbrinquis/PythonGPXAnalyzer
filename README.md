# PythonGPXAnalyzer
This project was created as a set of Python scripts with the purpose of analyze my own running activities from different points of view.

# Libraries required to make this project work:
1. bokeh 2.0.0
2. datetime 4.3
3. dateutil 2.8.1
4. geopy 1.21.0
5. glob 0.7
6. lxml 4.5.0
7. numpy 1.18.2
8. pandas 1.0.3
9. pytz 2019.3
10. scipy 1.4.1
11. timezonefinder 4.2.0
12. reverse_geocoder 1.5.1

# How to launch the process:
1. The program that works as a master script is \source\main\LecturaDirectorio.py
2. To set up the environment is necessary to provide the following variables:
   A) DirectorioBase: base directory, where the project is located in the user's computer.
   B) fichero: input file, located in 'input' folder and with .gpx extension.
   C) LecturaIndividual: modifying it to 'N' all files in input folder can be read, but currently due to problems with Bokeh library it fails as second file is processed
3. If finished sucesfully, results will be placed in 'output' folder with same name as input file.
