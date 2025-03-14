import struct
import sys

def fix_exfat_boot_sector(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read(512))
    
    # Clear the dirty bit (bit 1) in volume flags at offset 106
    current_flags = struct.unpack('<H', data[106:108])[0]
    new_flags = current_flags & ~(1 << 1)  # Clear bit 1
    data[106:108] = struct.pack('<H', new_flags)
    
    # Write the fixed boot sector
    with open(output_file, 'wb') as f:
        f.write(data)
    
    print(f"Fixed boot sector written to {output_file}")
    print(f"Current flags: 0x{current_flags:04X}, New flags: 0x{new_flags:04X}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fix_exfat.py <input_boot_sector> <output_boot_sector>")
        sys.exit(1)
    
    fix_exfat_boot_sector(sys.argv[1], sys.argv[2])
