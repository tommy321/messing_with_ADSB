from pykml.factory import write_python_script_for_kml_document
from pykml import parser


file = 'shortened.kml'
fileobject = open(file, 'r')
doc = parser.parse(fileobject).getroot()
script = write_python_script_for_kml_document(doc)
f = open('out.txt', 'w')
f.write(script)
