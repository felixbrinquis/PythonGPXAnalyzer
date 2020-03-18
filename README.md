# PythonGPXAnalyzer
This project was created as a set of Python scripts with the purpose of analyze my own running activities from different points of view.

# Libraries required to make this project work:
1. bokeh
2. datetime
3. dateutil
4. geopy
5. glob
6. lxml
7. math
8. numpy
9. os
10. pandas
11. pytz
12. scipy
13. sys
14. timezonefinder

# How to launch the process:
1. The program that works as a master script is \source\main\LecturaDirectorio.py
2. To set up the environment is necessary to provide the following variables:
	2.1 DirectorioBase: base directory, where the project is located in the user's computer.
	2.2 fichero: input file, located in 'input' folder and with .gpx extension.
	2.3 LecturaIndividual: modifying it to 'N' all files in input folder can be read, but currently due to problems with Bokeh library it fails as second file is processed
3. If finished sucesfully, results will be placed in 'output' folder with same name as input file.
