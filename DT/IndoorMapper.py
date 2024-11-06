from PIL import Image
import uuid

def create_tab_map_ind_id_files(image_path, tab_output_path, map_output_path, ind_output_path, id_output_path, corners):
    """
    Create .tab, .map, .ind, and .id files for a JPEG image given its corner coordinates.

    Args:
        image_path (str): Path to the JPEG image.
        tab_output_path (str): Path where the .tab file will be saved.
        map_output_path (str): Path where the .map file will be saved.
        ind_output_path (str): Path where the .ind file will be saved.
        id_output_path (str): Path where the .id file will be saved.
        corners (list): List of corner coordinates [top_left, top_right, bottom_right, bottom_left].
                        Each coordinate is a tuple (latitude, longitude).
    """
    # Extract corner coordinates
    top_left, top_right, bottom_right, bottom_left = corners
    
    # Load the image to get its size
    img = Image.open(image_path)
    width, height = img.size

    # Write to the .tab file
    with open(tab_output_path, 'w') as f:
        f.write("!table\n")
        f.write("!version 300\n")
        f.write("!charset WindowsTurkish\n\n")
        f.write("Definition Table\n")
        f.write(f'  File "{image_path}"\n')
        f.write("  Type \"RASTER\"\n")
        
        # Corner points with pixel positions
        f.write(f"  ({top_left[1]},{top_left[0]}) (0,0) Label \"Pt 1\",\n")
        f.write(f"  ({top_right[1]},{top_right[0]}) ({width - 1},0) Label \"Pt 2\",\n")
        f.write(f"  ({bottom_right[1]},{bottom_right[0]}) ({width - 1},{height - 1}) Label \"Pt 3\",\n")
        f.write(f"  ({bottom_left[1]},{bottom_left[0]}) (0,{height - 1}) Label \"Pt 4\"\n")
        
        # Coordinate system and metadata
        f.write("  CoordSys Earth Projection 1, 104\n")
        f.write("  Units \"degree\"\n")
        f.write("begin_metadata\n")
        f.write("\"\\IsReadOnly\" = \"FALSE\"\n")
        f.write("\"\\MapInfo\" = \"\"\n")
        f.write("\"\\MapInfo\\TableID\" = \"aee192dd-19d7-4959-8815-8dce67aeef53\"\n")
        f.write("end_metadata\n")
    print(f"Tab file created successfully at {tab_output_path}")

    # Write to the .map file
    with open(map_output_path, 'w') as f:
        f.write("!map\n")
        f.write("!version 300\n")
        f.write("!charset WindowsTurkish\n\n")
        f.write("Definition Map\n")
        f.write(f'  File "{image_path}"\n')
        f.write("  Type \"RASTER\"\n")
        f.write(f"  ImageWidth {width}\n")
        f.write(f"  ImageHeight {height}\n")
        f.write("  CoordSys Earth Projection 1, 104\n")
        f.write("  Units \"degree\"\n")
        
        # Image corners metadata
        f.write("begin_metadata\n")
        f.write("\"\\ImageCorners\" = \"Top Left: ({0},{1}), Top Right: ({2},{3}), "
                "Bottom Right: ({4},{5}), Bottom Left: ({6},{7})\"\n".format(
                    top_left[1], top_left[0], top_right[1], top_right[0],
                    bottom_right[1], bottom_right[0], bottom_left[1], bottom_left[0]
                ))
        f.write("end_metadata\n")
    print(f"Map file created successfully at {map_output_path}")

    # Write to the .ind file
    with open(ind_output_path, 'w') as f:
        f.write("!index\n")
        f.write("!version 300\n")
        f.write("!charset WindowsTurkish\n\n")
        f.write("Definition Index\n")
        f.write(f'  File "{image_path}"\n')
        f.write("  Type \"RASTER\"\n")
        f.write("  IndexType \"Spatial\"\n")
        
        # Placeholder bounding box using corner coordinates
        f.write("  BoundingBox\n")
        f.write(f"    TopLeft: ({top_left[1]}, {top_left[0]})\n")
        f.write(f"    TopRight: ({top_right[1]}, {top_right[0]})\n")
        f.write(f"    BottomRight: ({bottom_right[1]}, {bottom_right[0]})\n")
        f.write(f"    BottomLeft: ({bottom_left[1]}, {bottom_left[0]})\n")
        f.write("  EndBoundingBox\n")
        
        # Optional metadata
        f.write("begin_metadata\n")
        f.write("\"\\IndexID\" = \"generated-index-id\"\n")
        f.write("\"\\IsIndexed\" = \"TRUE\"\n")
        f.write("end_metadata\n")
    print(f"Ind file created successfully at {ind_output_path}")

    # Write to the .id file
    with open(id_output_path, 'w') as f:
        unique_id = str(uuid.uuid4())  # Generate a unique ID
        f.write("!id\n")
        f.write("!version 300\n")
        f.write("!charset WindowsTurkish\n\n")
        f.write("Definition ID\n")
        f.write(f"  UniqueID \"{unique_id}\"\n")
        f.write(f'  File "{image_path}"\n')
        f.write("  Type \"RASTER\"\n")
        
        # Optional metadata
        f.write("begin_metadata\n")
        f.write("\"\\CreationDate\" = \"2024-11-05\"\n")
        f.write("\"\\ImageSource\" = \"User-generated raster\"\n")
        f.write("\"\\CoordinateSystem\" = \"Earth Projection 1, 104\"\n")
        f.write("end_metadata\n")
    print(f"ID file created successfully at {id_output_path}")

def get_corners():
    """
    Prompt the user for corner coordinates in latitude,longitude format.

    Returns:
        list: List of corner coordinates as tuples [(lat, lon), (lat, lon), (lat, lon), (lat, lon)]
    """
    user_input = input("Enter the corner coordinates in the format 'lat1,lon1;lat2,lon2;lat3,lon3;lat4,lon4': ")
    corners = []
    
    # Split input by semicolons to get each corner
    for corner_str in user_input.split(';'):
        lat, lon = map(float, corner_str.split(','))
        corners.append((lat, lon))
    
    return corners

# Example usage
image_path = 'stad.jpg'  # Path to your JPEG image
tab_output_path = 'output_file.tab'  # Path where you want to save the .tab file
map_output_path = 'output_file.map'  # Path where you want to save the .map file
ind_output_path = 'output_file.ind'  # Path where you want to save the .ind file
id_output_path = 'output_file.id'  # Path where you want to save the .id file
corners = get_corners()  # Get corner coordinates from user

create_tab_map_ind_id_files(image_path, tab_output_path, map_output_path, ind_output_path, id_output_path, corners)
