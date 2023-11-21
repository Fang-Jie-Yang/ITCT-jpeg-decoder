import sys

SOI = b'\xFF\xD8'
APP = b'\xFF\xE0'
DQT = b'\xFF\xDB'
DHP = b'\xFF\xC0'
EOI = b'\xFF\xD9'

def perror(err):
    print(err)
    exit(-1)

def debug_print(msg):
    if True:
        print(msg, end="")

def pop_n(jpeg, n):
    words = jpeg[0:n]
    for _ in range(n):
        jpeg.pop(0)
    return bytes(words)

def bytes_to_int(b):
    return int.from_bytes(b, "big")

def split_byte(b):
    bits = format(b, '08b')
    a = int(bits[0:4], 2)
    b = int(bits[4:8], 2)
    return a, b

def debug_print_table(indent, t, n, m):
    debug_print(indent + "Table:\n")
    for i in range(n):
        debug_print(indent + "  ")
        for j in range(m):
            debug_print(f"{t[i][j]:2d} ")
        debug_print("\n")

# Application0
def handle_APP(jpeg):
    La = bytes_to_int(pop_n(jpeg, 2))
    debug_print(f"  La: {La}\n")
    pop_n(jpeg, La - 2)
    # we skip APP for now
    return

zigzag_order = [(0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2), (2, 1), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (6, 0), (5, 1), (4, 2), (3, 3), (2, 4), (1, 5), (0, 6), (0, 7), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0), (7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6), (1, 7), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (7, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7), (4, 7), (5, 6), (6, 5), (7, 4), (7, 5), (6, 6), (5, 7), (6, 7), (7, 6), (7, 7)]
# Define Quatization Table
def handle_DQT(jpeg, DQTs):
    Lq = bytes_to_int(pop_n(jpeg, 2))
    debug_print(f"  Lq: {Lq}\n")
    n = 2
    while n != Lq:
        PqTq = bytes_to_int(pop_n(jpeg, 1))
        n += 1
        Pq, Tq = split_byte(PqTq)
        Qk = 8 if Pq == 0 else 16
        debug_print(f"  Pq: {Pq}\n")
        debug_print(f"  Tq: {Tq}\n")
        debug_print(f"  Qk: {Qk}\n")
        tmp = [[0 for _ in range(8)] for __ in range(8)]
        for z in range(64):
            i, j = zigzag_order[z]
            tmp[i][j] = (bytes_to_int(pop_n(jpeg, Qk//8)))
        debug_print_table("    ", tmp, 8, 8)
        DQTs[Tq] = tmp
        n += (Qk // 8) * 8 * 8
    return

def handle_DHP(jpeg, Components):
    Lf = bytes_to_int(pop_n(jpeg, 2))
    P  = bytes_to_int(pop_n(jpeg, 1))
    Y  = bytes_to_int(pop_n(jpeg, 2))
    X  = bytes_to_int(pop_n(jpeg, 2))
    Nf = bytes_to_int(pop_n(jpeg, 1))
    debug_print(f"  Lf: {Lf}\n")
    debug_print(f"  P: {P}\n")
    debug_print(f"  Y: {Y}\n")
    debug_print(f"  X: {X}\n")
    debug_print(f"  Nf: {Nf}\n")
    tmp = {}
    for _ in range(Nf):
        tmp['C'] = bytes_to_int(pop_n(jpeg, 1))
        tmp['H'], tmp['V'] = split_byte(bytes_to_int(pop_n(jpeg, 1)))
        tmp['Tq'] = bytes_to_int(pop_n(jpeg, 1))
        debug_print(f"  {tmp}\n")
        Components.append(tmp)
    return

if len(sys.argv) != 2:
    perror(f"Usage: {sys.argv[0]} input_jpg")
with open(sys.argv[1], 'rb') as f:
    jpeg = bytearray(f.read())

if pop_n(jpeg, 2) != SOI:
    perror("File format error")

DQTs = {}
Components = []
while True:
    wd = pop_n(jpeg, 2)
    if wd == APP:
        debug_print("APP\n")
        handle_APP(jpeg)
    elif wd == DQT:
        debug_print("DQT\n")
        handle_DQT(jpeg, DQTs)
    elif wd == DHP:
        debug_print("DHP\n")
        handle_DHP(jpeg, Components)
    else:
        print("X")
        break



