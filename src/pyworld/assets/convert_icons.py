import os
from pathlib import Path
from cairosvg import svg2png

def convert_icons():
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    
    # Create output directory if it doesn't exist
    output_dir = script_dir / 'icons_png'
    output_dir.mkdir(exist_ok=True)
    
    # Convert all SVG files in the icons directory
    icons_dir = script_dir / 'icons'
    for svg_file in icons_dir.glob('*.svg'):
        try:
            output_file = output_dir / f"{svg_file.stem}.png"
            
            # Convert SVG to PNG using CairoSVG
            with open(svg_file, 'rb') as svg_data:
                svg2png(
                    file_obj=svg_data,
                    write_to=str(output_file),
                    output_width=32,
                    output_height=32
                )
            print(f"Converted {svg_file.name} to {output_file.name}")
        
        except Exception as e:
            print(f"Error converting {svg_file.name}: {str(e)}")

if __name__ == '__main__':
    convert_icons() 