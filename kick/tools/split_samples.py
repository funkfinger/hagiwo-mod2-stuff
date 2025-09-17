#!/usr/bin/env python3
# split_samples.py - Extract individual sample arrays into separate header files

import re
from pathlib import Path


def extract_samples(input_file: Path, output_dir: Path) -> None:
    """Extract each sample array into its own header file."""
    
    # Read the input file
    content = input_file.read_text()
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Pattern to match sample arrays
    pattern = r'const uint8_t (sample\d+)\[\] PROGMEM = \{([^}]+)\};'
    
    matches = re.findall(pattern, content, re.DOTALL)
    
    print(f"Found {len(matches)} sample arrays")
    
    valid_samples = []

    for sample_name, sample_data in matches:
        # Clean up the sample data (remove extra whitespace and comments)
        cleaned_data = re.sub(r'/\*[^*]*\*/', '', sample_data)  # Remove comments
        cleaned_data = re.sub(r'\s+', ' ', cleaned_data.strip())  # Normalize whitespace

        # Skip empty samples (placeholders)
        if not cleaned_data or cleaned_data.strip() == '' or 'placeholder' in cleaned_data.lower():
            print(f"Skipping empty sample: {sample_name}")
            continue

        valid_samples.append(sample_name)

        # Format the hex data with proper line breaks (16 bytes per line)
        hex_values = cleaned_data.split(', ')
        formatted_lines = []
        for i in range(0, len(hex_values), 16):
            line = ', '.join(hex_values[i:i+16])
            if i + 16 < len(hex_values):
                line += ','
            formatted_lines.append(f"    {line}")

        formatted_data = '\n'.join(formatted_lines)

        # Create header file content
        header_content = f"""#ifndef {sample_name.upper()}_H
#define {sample_name.upper()}_H

#include <pgmspace.h>

// Sample data for {sample_name}
const uint8_t {sample_name}[] PROGMEM = {{
{formatted_data}
}};

// Sample length in 16-bit units
#define {sample_name.upper()}_LEN ((uint32_t)(sizeof({sample_name}) / 2))

#endif // {sample_name.upper()}_H
"""

        # Write to individual header file
        output_file = output_dir / f"{sample_name}.h"
        output_file.write_text(header_content)

        print(f"Created: {output_file}")
    
    # Create a master include file
    # Create a master include file only for valid samples
    master_content = """#ifndef SAMPLES_H
#define SAMPLES_H

// Include all individual sample headers
"""

    for sample_name in valid_samples:
        master_content += f'#include "{sample_name}.h"\n'

    master_content += """
// Array of sample pointers for easy access
const uint8_t* const samples[] = {
"""

    for i, sample_name in enumerate(valid_samples):
        master_content += f"    {sample_name}{',' if i < len(valid_samples) - 1 else ''}\n"

    master_content += """};

// Array of sample lengths
const uint16_t sample_lengths[] = {
"""

    for i, sample_name in enumerate(valid_samples):
        master_content += f"    {sample_name.upper()}_LEN{',' if i < len(valid_samples) - 1 else ''}\n"

    master_content += """};

#define NUM_SAMPLES (sizeof(samples) / sizeof(samples[0]))

#endif // SAMPLES_H
"""
    
    master_file = output_dir / "samples.h"
    master_file.write_text(master_content)
    print(f"Created master include file: {master_file}")


def main():
    input_file = Path("src/sample.h")
    output_dir = Path("src/samples")
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        return
    
    extract_samples(input_file, output_dir)
    print("Sample extraction complete!")


if __name__ == "__main__":
    main()
