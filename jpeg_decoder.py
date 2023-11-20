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
        print(msg)

def pop_n(jpeg, n):
    words = jpeg[0:n]
    for _ in range(n):
        jpeg.pop(0)
    return bytes(words)

def bytes_to_int(b):
    return int.from_bytes(b, "big")

# Application0
def handle_APP(jpeg):
    La = bytes_to_int(pop_n(jpeg, 2))
    debug_print(f"  La: {La}")
    pop_n(jpeg, La - 2)
    # we skip APP for now
    return

# Define Quatization Table
zigzag_order = [(0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2), (2, 1), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (6, 0), (5, 1), (4, 2), (3, 3), (2, 4), (1, 5), (0, 6), (0, 7), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0), (7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6), (1, 7), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (7, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7), (4, 7), (5, 6), (6, 5), (7, 4), (7, 5), (6, 6), (5, 7), (6, 7), (7, 6), (7, 7)]
def handle_DQT(jpeg, DQTs):
    Lq = bytes_to_int(pop_n(jpeg, 2))
    debug_print(f"  Lq: {Lq}")
    n = 2
    while n != Lq:
        PqTq = bytes_to_int(pop_n(jpeg, 1))
        n += 1
        bits = format(PqTq, '08b')
        Pq = int(bits[0:4], 2)
        Tq = int(bits[4:8], 2)
        Qk = 8 if Pq == 0 else 16
        debug_print(f"  Pq: {Pq}")
        debug_print(f"  Tq: {Tq}")
        debug_print(f"  Qk: {Qk}")
        tmp = [[0 for _ in range(8)] for __ in range(8)]
        for z in range(64):
            i, j = zigzag_order[z]
            tmp[i][j] = (bytes_to_int(pop_n(jpeg, Qk//8)))
        debug_print(f"  In zigzag: {tmp}")
        DQTs[Tq] = tmp
        n += (Qk // 8) * 8 * 8
    return

def handle_DHP(jpeg):
    Lf = bytes_to_int(pop_n(jpeg, 2))
    P = bytes_to_int(pop_n(jpeg, 1))
    Y = bytes_to_int(pop_n(jpeg, 2))
    X = bytes_to_int(pop_n(jpeg, 2))
    Nf = bytes_to_int(pop_n(jpeg, 1))
    debug_print(f"  Lf: {Lf}")
    debug_print(f"  P: {P}")
    debug_print(f"  Y: {Y}")
    debug_print(f"  X: {X}")
    debug_print(f"  Nf: {Nf}")
    return

if len(sys.argv) != 2:
    perror(f"Usage: {sys.argv[0]} input_jpg")
with open(sys.argv[1], 'rb') as f:
    jpeg = bytearray(f.read())

if pop_n(jpeg, 2) != SOI:
    perror("File format error")

DQTs = {}
while True:
    wd = pop_n(jpeg, 2)
    if wd == APP:
        debug_print("APP")
        handle_APP(jpeg)
    elif wd == DQT:
        debug_print("DQT")
        handle_DQT(jpeg, DQTs)
    elif wd == DHP:
        debug_print("DHP")
        handle_DHP(jpeg)
    else:
        print("X")
        break



