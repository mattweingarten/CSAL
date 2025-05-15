import sys
import io

is_synced = False
eof = False

def read_bin_file():
    data = True
    while data and not eof:
        if not is_synced:
            data = not_sync()
        else:
            # process packet
            data = sync()
    print("done.")

def not_sync():
    global is_synced
    buffer = ""

    byte = file.read(1)
    while byte:
        buffer = byte.hex() + buffer
        if len(buffer) > 12:
            buffer = buffer[:12]

        # data all stored little endian
        if (buffer == "800000000000"):
            print("SYNC")
            is_synced = True
            break
        byte = file.read(1)
    return True

def sync():
    global eof, is_synced

    # Look ahead for sync mid-trace
    buffer = ""
    peek_bytes = file.peek(6) if hasattr(file, 'peek') else b""
    if len(peek_bytes) >= 6:
        buffer = peek_bytes[:6][::-1].hex()
        if (buffer == "800000000000"):
            print("SYNC mid-trace")
            file.read(6)  # consume sync bytes
            is_synced = True

    header = file.read(1)
    if not header:
        eof = True
        print("EOF")
        return False
    print(f"header: {header.hex()}")

    # process header
    header_bin = format(int(header.hex(), 16), 'b').zfill(8)
    if header.hex() == "70":
        print("OVERFLOW pkt")
    elif header.hex()[-1] == "0" and header_bin[1:4] != "000":
        print("TIMESTAMP pkt")
        process_timestamp(header_bin)
    elif header.hex()[-1] == "4":
        print("RESERVED pkt")
    elif header_bin[-3] == "0" and header_bin[-2:] != "00":
        print("SWIT pkt")
        process_swit(header_bin)
        # handle_data(int(header_bin[-2:], 2))
    else:
        print("UNKNOWN pkt: " + header.hex())
    return True

def process_swit(header_bin):
    print(f"  address: {header_bin[:5]}")
    if (header_bin[-2:] == "01"):
        handle_data(1)
    elif (header_bin[-2:] == "10"):
        handle_data(2)
    elif (header_bin[-2:] == "11"):
        handle_data(4)
    else:
        print("  invalid size")

def handle_data(size):
    byte = file.read(1)
    size -= 1
    data = byte.hex()
    while size:
        byte = file.read(1)
        data = byte.hex() + data
        size -= 1
    print(f"  data: {data}")

def process_timestamp(header_bin):
    timestamp = ""
    if (header_bin[0] == "1"):
        timestamp = handle_ts_data()
        print(f"timestamp: {timestamp}")

def handle_ts_data():
    byte_bin = format(int(file.read(1).hex(), 16), 'b')
    ts_bin = byte_bin[1:]
    while byte_bin[0] == "1":
        byte_bin = format(int(file.read(1).hex(), 16), 'b')
        ts_bin = byte_bin[1:] + ts_bin
    return int(ts_bin, 2)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_bin_file.py <path_to_bin_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        with open(file_path, "rb", buffering=0) as f_raw:
            file = io.BufferedReader(f_raw)
            read_bin_file()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except IOError:
        print(f"Error reading file: {file_path}")
