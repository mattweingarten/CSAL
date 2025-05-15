import os
import mmap
import struct
import time

MAP_MASK = mmap.PAGESIZE - 1

# steps to read from trace
# unlock itm with 0xF8805FB0 <- 0xC5ACCE55
# disable itm trace
# unlock etb with 0xF8801FB0 <- 0xC5ACCE55
# read from trace

def mmap_read(addr, size=4):
    f = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
    mem = mmap.mmap(f, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=addr & ~MAP_MASK)
    mem.seek(addr & MAP_MASK)

    data = mem.read(4)
    #val = 0x0
    #for i in range(4):
    #    val |= ord(mem.read_byte()) << (i * 8)
    
    mem.close()
    os.close(f)

    return struct.unpack("<I", data)[0]
    #return val

def mmap_write(addr, payload):
    f = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
    mem = mmap.mmap(f, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=addr & ~MAP_MASK)
    mem.seek(addr & MAP_MASK)
    mem.write(struct.pack("<I", payload))

    mem.close()
    os.close(f)


if __name__ == "__main__":
    #dr = mmap_read(0xF8801004)
    #print(dr)
    for i in range(4):
        mmap_write(0xF8805000, 0x12345678)
    #time.sleep(1)
    #dr = mmap_read(0xF8801004)
    #print(dr)
