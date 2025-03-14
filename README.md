# Repair a broken exfat system with a 'dirty' flag

#### Table of Contents  
- [Background and Troubleshooting](#Background-and-Troubleshooting)
- [Fix](#Fix-the-exfat-system)
- [FAQ](#FAQ) 

## Background and Troubleshooting
I had the issue that I was not able to mount my external ssd anymore. Neither on MacOS nor on Windows. The drive appeared in the Disk Utility on MacOS but it failed to mount. Running first aid resulted in a failed repair attempt

```log
Running First Aid on “X10 Pro” (disk4s2)

Checking file system and repairing if necessary and if possible.
Volume is already unmounted.
Performing fsck_exfat -y -x /dev/rdisk4s2
Checking volume.
Checking main boot region.
Checking system files.
Volume name is X10 Pro.
Checking uppercase translation table.
Checking file system hierarchy.
Checking active bitmap.
Rechecking main boot region.
Rechecking alternative boot region.
The volume X10 Pro could not be verified completely.
File system check exit code is 1.
Restoring the original state found as unmounted.
File system verify or repair failed. : (-69845)

Operation failed…
```

On Windows the Disk Manager crashed after execution.


My last hope remained on Linux.


Dmesg gave me some serious looking output and I almost gave up on recovering the disk
```log
[29284.944801] sd 6:0:0:0: [sdb] tag#7 FAILED Result: hostbyte=DID_OK driverbyte=DRIVER_OK cmd_age=0s
[29284.944806] sd 6:0:0:0: [sdb] tag#7 Sense Key : Hardware Error [current] 
[29284.944821] sd 6:0:0:0: [sdb] tag#7 Add. Sense: Logical unit communication CRC error (Ultra-DMA/32)
[29284.944824] sd 6:0:0:0: [sdb] tag#7 CDB: Read(16) 88 00 00 00 00 00 00 00 80 08 00 00 00 08 00 00
[29284.944826] critical target error, dev sdb, sector 32776 op 0x0:(READ) flags 0x0 phys_seg 1 prio class 2
[29284.944832] Buffer I/O error on dev sdb2, logical block 1, async page read
```


Linux has a tool called fsck.exfat with options to repair but no matter what I tried I always got the following output (Make sure you use the correct disk. It may not be sdb2 -> see FAQ)

```bash
sudo fsck.exfat -r /dev/sdb2   
exfatprogs version : 1.2.1
failed to read boot region
```

Trying to mount /dev/sdb2 worked suprisingly.

```bash
mkdir /tmp/recover
sudo mount -t exfat /dev/sdb2 /tmp/recover
ls -la /tmp/recover
```

I started to assumed that only the boot region got corrupted. 
So... lets backup the boot region and inspect it

```bash
sudo dd if=/dev/sdb2 of=boot_region_backup.bin bs=512 count=16
```

Using my little script 
```bash
python3 rescue.py boot_region_dirty_fixed.bin
```

I got the following output
```
=== exFAT Boot Sector Analysis ===
Jump Boot: eb7690
File System Name: EXFAT   
Partition Offset: 32768 sectors
Volume Length: 7814002688 sectors
FAT Offset: 2048 sectors from start of volume
FAT Length: 30720 sectors
Cluster Heap Offset: 32768 sectors from start of volume
Cluster Count: 3815415 clusters
Root Directory First Cluster: 4
Volume Serial Number: B8AB73FDh
FS Revision: 1.0
Volume Flags: 0002h
  - Active FAT: First FAT
  - Volume State: Dirty
  - Media Status: No media failures
Bytes Per Sector: 512 bytes (2^9)
Sectors Per Cluster: 2048 sectors (2^11)
Number of FATs: 1
```

The important point here is: **Volume State: Dirty**

This means the filesystem was not properly unmounted or was in the middle of operations when it was disconnected. 

## Fix the exfat system

So how do we fix that? The easy solution is to overwrite the dirty flag and set it back to zero. For that I wrote another small script that does it for you.

- Firstly write the boot region (if not done already) to a file and don't manipulate the disk directly

```bash
sudo dd if=/dev/sdb2 of=boot_region_backup.bin bs=512 count=16
```
- Secondly fix the dirty flag in the boot region
```bash
python3 fix_dirty_flag.py boot_region_backup.bin boot_region_dirty_fixed.bin 
```

- Lastely we just need to write back the boot region to the disk

```bash
sudo dd if=boot_region_dirty_fixed.bin of=/dev/sdb2 bs=512 count=1
```

Your disk should now work again and all your data should still be there!


## FAQ
### How do you I know my disk device on Linux?

I used lsblk. Just execute it before you connect the drive and after. The device that appears is your disk. You should see an output similar to yours.
Here sdb with sdb1 and sdb2 appears. The correct volumen is sdb2 in this case. You should check the size. Normally it is not the very small device (like sdb1 with 16M)

```bash
└─$ lsblk      
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sda      8:0    0   64G  0 disk 
├─sda1   8:1    0  512M  0 part /boot/efi
├─sda2   8:2    0 62.5G  0 part /
└─sda3   8:3    0  976M  0 part [SWAP]
sdb      8:16   0  3.6T  0 disk 
├─sdb1   8:17   0   16M  0 part 
└─sdb2   8:18   0  3.6T  0 part 
sr0     11:0    1 1024M  0 rom  
```

