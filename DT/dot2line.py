import zipfile
from pykml import parser
from os import path
import shapefile
from fastkml import kml, geometry
from shapely.geometry import LineString

def extract_kml_from_kmz(kmz_file_path):
    with zipfile.ZipFile(kmz_file_path, 'r') as kmz:
        for file in kmz.namelist():
            if file.endswith('.kml'):
                with kmz.open(file, 'r') as kml_file:
                    return kml_file.read()
    return None

def parse_kml_points(kml_content):
    doc = parser.fromstring(kml_content)
    coordinates = []
    for placemark in doc.Document.Folder.Placemark:
        if hasattr(placemark, 'Point'):
            coord = placemark.Point.coordinates.text.strip()
            lon, lat, _ = map(float, coord.split(','))
            coordinates.append((lon, lat))
    return coordinates

def create_line_kml(output_kml_file, coordinates):
    k = kml.KML()
    doc = kml.Document()
    k.append(doc)
    
    linestring = LineString(coordinates)
    line_geom = geometry.Geometry(geometry=linestring)
    
    placemark = kml.Placemark()
    placemark.geometry = line_geom
    doc.append(placemark)
    
    with open(output_kml_file, 'w') as f:
        f.write(k.to_string())
    print(f"Line-based KML saved as {output_kml_file}")

def create_tab_file(output_tab_file, coordinates):
    with shapefile.Writer(output_tab_file, shapeType=shapefile.POLYLINE) as tab:
        tab.field('ID', 'N')
        tab.line([coordinates])
        tab.record(1)
    print(f"Line-based TAB saved as {output_tab_file}.shp")

# File paths
kmz_file_path = 'VoLTE_PCI.kmz'
output_kml_file = 'output_line.kml'
output_tab_file = 'output_line.tab'

# Step 1: Extract KML content from KMZ
kml_content = extract_kml_from_kmz(kmz_file_path)
if kml_content is None:
    print("No KML file found in the KMZ archive.")
else:
    # Step 2: Parse points from KML
    coordinates = parse_kml_points(kml_content)
    
    if len(coordinates) < 2:
        print("Insufficient points to create a line.")
    else:
        # Step 3: Create line-based KML
        create_line_kml(output_kml_file, coordinates)
        
        # Step 4: Create TAB file
        create_tab_file(output_tab_file, coordinates)
