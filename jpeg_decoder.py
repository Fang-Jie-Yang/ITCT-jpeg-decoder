import sys

SOI = bytes([0xFF, 0xD8])
EOI = bytes([0xFF, 0xD9])

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} input_jpg")
    exit(-1)

with open(sys.argv[1], 'rb') as f:
    jpeg = f.read()

if jpeg[0:2] != SOI or jpeg[-2:] != EOI:
    print("File format error")
    exit(-1)


