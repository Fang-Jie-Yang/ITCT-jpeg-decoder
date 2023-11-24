import sys
from math import ceil
import numpy as np
from scipy.fft import idct
from bmp import *

m_SOI   = b'\xFF\xD8'
m_APP   = b'\xFF\xE0'
m_DQT   = b'\xFF\xDB'
m_SOF_0 = b'\xFF\xC0'
m_EOI   = b'\xFF\xD9'
m_DHT   = b'\xFF\xC4'
m_SOS   = b'\xFF\xDA'
m_DHP   = b'\xFF\xDE'

def perror(err):
    print(err)
    exit(-1)

def debug_print(msg):
    #if True:
    if False:
        print(msg, end="")

def pop_n(jpeg, n):
    words = jpeg[0:n]
    for _ in range(n):
        jpeg.pop(0)
    return bytes(words)

def bytes_to_int(b):
    return int.from_bytes(b, "big")

def split_byte(b):
    _bits = format(b, '08b')
    a = int(_bits[0:4], 2)
    b = int(_bits[4:8], 2)
    return a, b

def debug_print_table(t, n, m):
    debug_print("    Table:\n")
    for i in range(n):
        debug_print("      ")
        for j in range(m):
            debug_print(f"{t[i][j]:4d} ")
        debug_print("\n")

# Application
def handle_APP(jpeg):
    APP = {}
    La = bytes_to_int(pop_n(jpeg, 2))
    APP['La'] = La
    debug_print(f"  La: {La}\n")
    # we skip APP for now
    pop_n(jpeg, La - 2)
    return APP

zigzag_order = [(0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2), (2, 1), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (6, 0), (5, 1), (4, 2), (3, 3), (2, 4), (1, 5), (0, 6), (0, 7), (1, 6), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 0), (7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6), (1, 7), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3), (7, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7), (4, 7), (5, 6), (6, 5), (7, 4), (7, 5), (6, 6), (5, 7), (6, 7), (7, 6), (7, 7)]
# Define Quatization Table
def handle_DQT(jpeg):
    DQT = {}
    Lq = bytes_to_int(pop_n(jpeg, 2))
    DQT['Lq'] = Lq
    debug_print(f"  Lq: {Lq}\n")
    n = 2
    Tables = []
    while n != Lq:
        table = {}
        Pq, Tq = split_byte(bytes_to_int(pop_n(jpeg, 1)))
        Qk = 8 if Pq == 0 else 16
        table['Pq'] = Pq
        table['Tq'] = Tq
        table['Qk'] = Qk
        debug_print(f"  Pq: {Pq}, Tq: {Tq}, Qk: {Qk}\n")
        n += 1
        tmp = [[0 for _ in range(8)] for __ in range(8)]
        for z in range(64):
            i, j = zigzag_order[z]
            tmp[i][j] = (bytes_to_int(pop_n(jpeg, Qk//8)))
        table['arr'] = tmp
        debug_print_table(tmp, 8, 8)
        Tables.append(table)
        n += (Qk // 8) * 8 * 8
    DQT['Tables'] = Tables
    return DQT

def handle_DHP(jpeg):
    DHP = {}

    Lf = bytes_to_int(pop_n(jpeg, 2))
    DHP['Lf'] = Lf
    debug_print(f"  Lf: {Lf}\n")

    P  = bytes_to_int(pop_n(jpeg, 1))
    DHP['P'] = P
    debug_print(f"  P: {P}\n")

    Y  = bytes_to_int(pop_n(jpeg, 2))
    DHP['Y'] = Y
    debug_print(f"  Y: {Y}\n")

    X  = bytes_to_int(pop_n(jpeg, 2))
    DHP['X'] = X
    debug_print(f"  X: {X}\n")

    Nf = bytes_to_int(pop_n(jpeg, 1))
    DHP['Nf'] = Nf
    debug_print(f"  Nf: {Nf}\n")

    Components = {}
    for _ in range(Nf):
        tmp = {}
        tmp['C'] = bytes_to_int(pop_n(jpeg, 1))
        tmp['H'], tmp['V'] = split_byte(bytes_to_int(pop_n(jpeg, 1)))
        tmp['Tq'] = bytes_to_int(pop_n(jpeg, 1))
        debug_print(f"  {tmp}\n")
        Components[tmp['C']] = tmp
    DHP['Components'] = Components
    return DHP

def handle_SOF_0(jpeg):
    return handle_DHP(jpeg)

def handle_DHT(jpeg):
    DHT = {}
    Lh = bytes_to_int(pop_n(jpeg, 2))
    DHT['Lh'] = Lh
    debug_print(f"  Lh: {Lh}\n")
    n = 2 

    Tables = []
    while n != Lh:
        table = {}
        Tc, Th = split_byte(bytes_to_int(pop_n(jpeg, 1)))
        table['Tc'] = Tc
        table['Th'] = Th
        debug_print(f"    Tc: {Tc}, Th: {Th}\n")
        n += 1

        L = []
        cnt = 0
        for _ in range(16):
            l = bytes_to_int(pop_n(jpeg, 1))
            cnt += l
            L.append(l)
        table['L'] = L
        debug_print(f"    Li: {L}\n")
        n += 16

        V = []
        for i in range(16):
            v = []
            for _ in range(L[i]):
                v.append(bytes_to_int(pop_n(jpeg, 1)))
            debug_print(f"    V{i + 1},k: {v}\n")
            V.append(v)
        table['V'] = V
        Tables.append(table)
        n += cnt
    DHT['Tables'] = Tables
    return DHT

def handle_SOS(jpeg):
    SOS = {}
    Ls = bytes_to_int(pop_n(jpeg, 2))
    SOS['Ls'] = Ls
    debug_print(f"  Ls: {Ls}\n")

    Ns = bytes_to_int(pop_n(jpeg, 1))
    SOS['Ns'] = Ns
    debug_print(f"  Ns: {Ns}\n")

    Scans = {}
    for _ in range(Ns):
        scan = {}
        Cs = bytes_to_int(pop_n(jpeg, 1))
        scan['Cs'] = Cs
        Td, Ta = split_byte(bytes_to_int(pop_n(jpeg, 1)))
        scan['Td'] = Td
        scan['Ta'] = Ta
        debug_print(f"    Cs: {Cs}, Td: {Td}, Ta: {Ta}\n")
        Scans[Cs] = scan
    SOS['Scans'] = Scans

    Ss = bytes_to_int(pop_n(jpeg, 1))
    SOS['Ss'] = Ss
    debug_print(f"  Ss: {Ss}\n")
    Se = bytes_to_int(pop_n(jpeg, 1))
    SOS['Se'] = Se
    debug_print(f"  Se: {Se}\n")
    Ah, Al = split_byte(bytes_to_int(pop_n(jpeg, 1)))
    SOS['Ah'] = Ah
    SOS['Al'] = Al
    debug_print(f"  Ah: {Ah}, Al: {Al}\n")
    return SOS

# return remaining bitstream, value
def decode_dc(bits, dcht):
    read_len = -1
    start = -1
    for i in range(1, 17):
        if bits[:i] in dcht:
            code = bits[:i]
            bits = bits[i:]
            debug_print("dc: {code}")
            read_len = dcht[code]
            debug_print(f"{read_len=}")
            if read_len == 0:
                return bits, 0
            code = bits[:read_len]
            bits = bits[read_len:]
            debug_print("dc: {code}")
            if code[0] == '0':
                return bits, -((2**read_len - 1) - int(code, 2))
            else:
                return bits, int(code, 2)
    perror("DC decode failed")

# return remaining bitstream, value, # of zeros
def decode_ac(bits, acht):
    for i in range(1, 17):
        if bits[:i] in acht:
            code = bits[:i]
            bits = bits[i:]
            out = acht[code]
            debug_print(f"bits: {int(code, 2):010b}  RS: {out:#04x}  ")
            if out == 0x00:
                debug_print("\n")
                return bits, 0, 64
            if out == 0xF0:
                debug_print("\n")
                return bits, 0, 15
            #print(f"{out=}")
            nz, read_len = split_byte(out)
            debug_print(f"RRRR: {nz:2d}  SSSS: {read_len:2d}  ")
            code = bits[:read_len]
            bits = bits[read_len:]
            #print("ac:", code)
            if code[0] == '0':
                val = -((2**read_len - 1) - int(code, 2))
            else:
                val = int(code, 2)
            debug_print(f"ZZ(K): {int(code, 2):2d} val: {val:3d}\n")
            return bits, val, nz
    perror("AC decode failed")

def idct2(block):
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

last_dc = {1: 0, 2: 0, 3: 0}
def handle_block(bits, C, dcht, acht, qt):
    global last_dc
    block = [[0 for _ in range(8)] for _ in range(8)]
    serial = []
    i = 0
    while i < 64:
        if i == 0:
            bits, val = decode_dc(bits, dcht)
            debug_print(f"  last: {last_dc[C]}\n")
            val += last_dc[C]
            last_dc[C] = val
            #print("decode_dc:", val)
            serial.append(val)
            i += 1
        else:
            bits, val, nz = decode_ac(bits, acht)
            #print("decode_ac:", val)
            for _ in range(nz):
                serial.append(0)
                i += 1
                if i >= 63:
                    break
            serial.append(val)
            i += 1
    # de Zig-Zag
    for z in range(64):
        i, j = zigzag_order[z]
        block[i][j] = serial[z]
    debug_print_table(block, 8, 8)
    # de Quantization
    for i in range(8):
        for j in range(8):
            block[i][j] *= qt[i][j]
    debug_print_table(block, 8, 8)
    # IDCT
    block = idct2(np.array(block))
    for i in range(8):
        for j in range(8):
            block[i][j] = round(block[i][j])
    block = block.astype(np.int64)
    debug_print_table(block, 8, 8)
    # level shift
    for i in range(8):
        for j in range(8):
            block[i][j] += 128
    debug_print_table(block, 8, 8)
    return bits, block

def handle_MCU(bits):
    global last_dc
    Comps = SOF_0['Components']
    Y, Cb, Cr = 1, 2, 3
    Blocks = {}
    for C in [Y, Cb, Cr]:
        scan = SOS['Scans'][C]
        comp = SOF_0['Components'][C]
        Td = scan['Td']
        Ta = scan['Ta']
        v = comp['V']
        h = comp['H']
        dcht = Huffman_Tables[0][Td]
        acht = Huffman_Tables[1][Ta]
        qt   = Quantization_Tables[comp['Tq']]
        Blocks[C] = [[0 for _ in range(h)] for __ in range(v)]
        for i in range(v):
            for j in range(h):
                bits, b = handle_block(bits, C, dcht, acht, qt)
                Blocks[C][i][j] = b
    # up sample 
    max_v = max(Comps[Y]['V'], Comps[Cb]['V'], Comps[Cr]['V'])
    max_h = max(Comps[Y]['H'], Comps[Cb]['H'], Comps[Cr]['H'])
    mcu_v = 8 * max_v
    mcu_h = 8 * max_h
    MCU = [[[0, 0 ,0] for _ in range(mcu_h)] for __ in range(mcu_v)]
    for C in [Y, Cb, Cr]:
        comp = SOF_0['Components'][C]
        v = comp['V']
        h = comp['H']
        cb = Blocks[C]
        for i in range(mcu_v):
            for j in range(mcu_h):
                ii = i * v // max_v
                jj = i * h // max_h
                MCU[i][j][C-1] = cb[ii // 8][jj // 8][ii % 8][jj % 8]
    # map to RGB
    def bound(x):
        if x > 255:
            return 255
        elif x < 0:
            return 0
        else:
            return round(x)
    rgb = [[[0, 0, 0] for _ in range(mcu_h)] for __ in range(mcu_v)]
    for i in range(mcu_v):
        for j in range(mcu_h):
            y, cb, cr = MCU[i][j]
            rgb[i][j][0] = bound(y + 1.402*cr + 128)
            rgb[i][j][1] = bound(y - 0.34414*cb - 0.71414*cr + 128)
            rgb[i][j][2] = bound(y + 1.772*cb + 128)
    return bits, rgb

def handle_data(jpeg):


    #bits = ''.join(format(byte, '08b') for byte in jpeg)
    bits = ""
    for i in range(len(jpeg)):
        if jpeg[i] == 0x00 and jpeg[i - 1] == 0xFF:
            continue
        bits += format(jpeg[i], '08b')

    #bits, rgb = handle_MCU(bits)
    #print("="*100)
    #bits, rgb = handle_MCU(bits)
    #print("="*100)
    #bits, rgb = handle_MCU(bits)
    #print("="*100)
    #print("="*100)
    #bits, rgb = handle_MCU(bits)
    #perror("temp")

    Comps = SOF_0['Components']
    Y, Cb, Cr = 1, 2, 3
    v = 8 * max(Comps[Y]['V'], Comps[Cb]['V'], Comps[Cr]['V'])
    h = 8 * max(Comps[Y]['H'], Comps[Cb]['H'], Comps[Cr]['H'])
    x = SOF_0['X']
    y = SOF_0['Y']
    pixels = [[0 for _ in range(x)] for __ in range(y)]
    print(ceil(y/v))
    print(ceil(x/v))
    for i in range(ceil(y / v)):
        for j in range(ceil(x / h)):
            bits, rgb = handle_MCU(bits)
            mcu_v = len(rgb)
            mcu_h = len(rgb[0])
            for ii in range(mcu_v):
                if i * mcu_v + ii >= y:
                    break
                for jj in range(mcu_h):
                    if j * mcu_h + jj >= x:
                        break
                    rgb888 = rgb[ii][jj][0] << 16 + rgb[ii][jj][1] << 8 + rgb[ii][jj][2]
                    pixels[i * mcu_v + ii][j * mcu_h + jj] = rgb888
    return pixels

def contruct_huffman_table(Tables, dht):
    for table in dht['Tables']:
        result_map = {}
        V = table['V']
        code_len = -1
        key = 0
        for l in range(16):
            for val in V[l]:
                result_map[format(key, f'0{l + 1}b')] = val
                key += 1
            key *= 2
        Tables[table['Tc']][table['Th']] = result_map

def contruct_quantization_table(Quantization_Tables, dqt):
    for table in dqt['Tables']:
        Quantization_Tables[table['Tq']] = table['arr']

if len(sys.argv) != 2:
    perror(f"Usage: {sys.argv[0]} input_jpg")
with open(sys.argv[1], 'rb') as f:
    jpeg = bytearray(f.read())

if pop_n(jpeg, 2) != m_SOI:
    perror("File format error")

APPs = []
DQTs = []
DHTs = []
SOFs = []
# DC, AC
Huffman_Tables = [{}, {}]
Quantization_Tables = {}
while True:
    wd = pop_n(jpeg, 2)
    if wd == m_APP:
        debug_print("APP\n")
        APP = handle_APP(jpeg)
        #print(APP)
        APPs.append(APP)
    elif wd == m_DQT:
        debug_print("DQT\n")
        DQT = handle_DQT(jpeg)
        #print(DQT)
        contruct_quantization_table(Quantization_Tables, DQT)
        DQTs.append(DQT)
    elif wd == m_DHP:
        debug_print("DHP\n")
        DHP = handle_DHP(jpeg)
        #print(DHP)
    elif wd == m_DHT:
        debug_print("DHT\n")
        DHT = handle_DHT(jpeg)
        #print(DHT)
        DHTs.append(DHT)
        contruct_huffman_table(Huffman_Tables, DHT)
        #print(Huffman_Tables)
    elif wd == m_SOS:
        debug_print("SOS\n")
        SOS = handle_SOS(jpeg)
        pixels = handle_data(jpeg)
        image = bmp(SOF_0['X'], SOF_0['Y'])
        image.gen_bmp_header()
        image.fill_image(pixels)
        image.save_image("save1.bmp")


    # Note we only handle SOF_0
    elif wd == m_SOF_0:
        debug_print("SOF_0\n")
        SOF_0 = handle_SOF_0(jpeg)
        #print(SOF_0)
    else:
        print(wd)
        print("X")
        break



