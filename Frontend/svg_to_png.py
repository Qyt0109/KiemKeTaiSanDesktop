import os
import cairosvg

def convert_svg_to_png_and_delete(src_folder, dest_folder):
    # Ensure the destination folder exists
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # List all SVG files in the source folder
    svg_files = [f for f in os.listdir(src_folder) if f.endswith(".svg")]

    for svg_file in svg_files:
        # Construct the full paths for the source and destination files
        svg_path = os.path.join(src_folder, svg_file)
        png_file = os.path.splitext(svg_file)[0] + ".png"
        png_path = os.path.join(dest_folder, png_file)

        # Convert the SVG to PNG using cairosvg
        try:
            cairosvg.svg2png(url=svg_path, write_to=png_path)

            print(f"Converted {svg_path} to {png_path}")

            # Delete the original SVG file
            os.remove(svg_path)
            print(f"Deleted {svg_path}")
        except:
            print("Error!")

if __name__ == "__main__":
    # Specify the source and destination folders
    source_folder = "/Applications/CODESTUFF/KiemKeTaiSan/Frontend/Resources"
    destination_folder = "/Applications/CODESTUFF/KiemKeTaiSan/Frontend/Resources"

    # Call the function to convert SVG to PNG and delete the original SVG files
    convert_svg_to_png_and_delete(source_folder, destination_folder)
