import zipfile
import os

def kml_to_kmz(kml_file, kmz_file):
    # Create a KMZ file which is a ZIP archive containing the KML file
    with zipfile.ZipFile(kmz_file, 'w', zipfile.ZIP_DEFLATED) as kmz:
        # Add the KML file to the KMZ archive
        kmz.write(kml_file, os.path.basename(kml_file))

    print(f'Converted {kml_file} to {kmz_file}')

# Example usage
kml_file = 'output_line.kml'  # Replace with your KML file path
kmz_file = 'example.kmz'  # Replace with your desired KMZ file path
kml_to_kmz(kml_file, kmz_file)
