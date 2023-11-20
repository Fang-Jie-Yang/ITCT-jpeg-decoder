import sys

SOI = b'\xFF\xD8'
APP = b'\xFF\xE0'
DQT = b'\xFF\xDB'
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
def handle_DQT(jpeg):
    Lq = bytes_to_int(pop_n(jpeg, 2))
    debug_print(f"  Lq: {Lq}")
    n = 2
    while n != Lq:
        PqTq = bytes_to_int(pop_n(jpeg, 1))
        n += 1
        bits = format(PqTq, '08b')
        Pq = int(bits[4:8], 2)
        Tq = int(bits[0:4], 2)
        Qk = 8 if Pq == 0 else 16
        debug_print(f"  Pq: {Pq}")
        debug_print(f"  Tq: {Tq}")
        debug_print(f"  Qk: {Qk}")
        n += (Qk // 8) * 8 * 8
    return

if len(sys.argv) != 2:
    perror(f"Usage: {sys.argv[0]} input_jpg")
with open(sys.argv[1], 'rb') as f:
    jpeg = bytearray(f.read())

if pop_n(jpeg, 2) != SOI:
    perror("File format error")
while True:
    wd = pop_n(jpeg, 2)
    if wd == APP:
        print("APP")
        handle_APP(jpeg)
    elif wd == DQT:
        print("DQT")
        handle_DQT(jpeg)
    else:
        print("X")
        break



