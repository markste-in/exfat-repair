import struct
import sys

def parse_exfat_boot_sector(filename):
    with open(filename, 'rb') as f:
        data = f.read(512)  # Read first sector
    
    # Parse the main fields
    jump_boot = data[0:3].hex()
    file_system_name = data[3:11].decode('ascii')
    must_be_zero = data[11:64]
    partition_offset = struct.unpack('<Q', data[64:72])[0]
    volume_length = struct.unpack('<Q', data[72:80])[0]
    fat_offset = struct.unpack('<I', data[80:84])[0]
    fat_length = struct.unpack('<I', data[84:88])[0]
    cluster_heap_offset = struct.unpack('<I', data[88:92])[0]
    cluster_count = struct.unpack('<I', data[92:96])[0]
    root_directory_cluster = struct.unpack('<I', data[96:100])[0]
    volume_serial_number = struct.unpack('<I', data[100:104])[0]
    fs_revision = struct.unpack('<H', data[104:106])[0]
    volume_flags = struct.unpack('<H', data[106:108])[0]
    bytes_per_sector_shift = data[108]
    sectors_per_cluster_shift = data[109]
    number_of_fats = data[110]
    
    # Calculate derived values
    bytes_per_sector = 2 ** bytes_per_sector_shift
    sectors_per_cluster = 2 ** sectors_per_cluster_shift
    
    # Decode volume flags
    active_fat = "Second FAT" if volume_flags & 1 else "First FAT"
    volume_dirty = "Dirty" if (volume_flags >> 1) & 1 else "Clean"
    media_failure = "Media failures detected" if (volume_flags >> 2) & 1 else "No media failures"
    
    # Print results
    print("=== exFAT Boot Sector Analysis ===")
    print(f"Jump Boot: {jump_boot}")
    print(f"File System Name: {file_system_name}")
    print(f"Partition Offset: {partition_offset} sectors")
    print(f"Volume Length: {volume_length} sectors")
    print(f"FAT Offset: {fat_offset} sectors from start of volume")
    print(f"FAT Length: {fat_length} sectors")
    print(f"Cluster Heap Offset: {cluster_heap_offset} sectors from start of volume")
    print(f"Cluster Count: {cluster_count} clusters")
    print(f"Root Directory First Cluster: {root_directory_cluster}")
    print(f"Volume Serial Number: {volume_serial_number:08X}h")
    print(f"FS Revision: {fs_revision >> 8}.{fs_revision & 0xFF}")
    print(f"Volume Flags: {volume_flags:04X}h")
    print(f"  - Active FAT: {active_fat}")
    print(f"  - Volume State: {volume_dirty}")
    print(f"  - Media Status: {media_failure}")
    print(f"Bytes Per Sector: {bytes_per_sector} bytes (2^{bytes_per_sector_shift})")
    print(f"Sectors Per Cluster: {sectors_per_cluster} sectors (2^{sectors_per_cluster_shift})")
    print(f"Number of FATs: {number_of_fats}")
    
    # Check if consistent with exFAT
    if file_system_name != "EXFAT   ":
        print("\nWARNING: This doesn't appear to be a valid exFAT filesystem!")
    
    # Check for potential corruption
    if any(b != 0 for b in must_be_zero):
        print("\nWARNING: Reserved area contains non-zero bytes - possible corruption!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_exfat.py <boot_sector_file>")
        sys.exit(1)
    
    parse_exfat_boot_sector(sys.argv[1])
