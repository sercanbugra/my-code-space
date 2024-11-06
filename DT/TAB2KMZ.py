import geopandas as gpd
import simplekml
import zipfile
import os

def tab_to_kmz(tab_file, kmz_file):
    # Read the TAB file using GeoPandas
    gdf = gpd.read_file(tab_file)

    # Create a KML object
    kml = simplekml.Kml()

    # Iterate through the GeoDataFrame and add points to the KML
    for _, row in gdf.iterrows():
        # Assuming the geometry is a Point, you may need to adjust this for other geometries
        if row.geometry.geom_type == 'Point':
            kml.newpoint(name=row.get('name', 'No Name'), coords=[(row.geometry.x, row.geometry.y)])
        # Add other geometry types if needed (e.g., LineString, Polygon)

    # Save the KML to a file
    kml_file = kmz_file.replace('.kmz', '.kml')
    kml.save(kml_file)

    # Create a KMZ file which is a ZIP archive containing the KML file
    with zipfile.ZipFile(kmz_file, 'w', zipfile.ZIP_DEFLATED) as kmz:
        kmz.write(kml_file, os.path.basename(kml_file))

    # Remove the temporary KML file
    os.remove(kml_file)

    print(f'Converted {tab_file} to {kmz_file}')

# Example usage
tab_file = 'Route.tab'  # Replace with your TAB file path
kmz_file = 'example2.kmz'  # Replace with your desired KMZ file path
tab_to_kmz(tab_file, kmz_file)
