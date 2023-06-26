import argparse
from math import ceil
from PIL import Image

DEBUG = False
DPI = 300


def mm_to_px(mm, dpi=DPI):
    return int(mm * (dpi // 25.4))


# mm
a4_width = 210
a4_height = 297
bit_size = 3

# pixels
pixel_a4_width = mm_to_px(a4_width)
pixel_a4_height = mm_to_px(a4_height)
pixel_bit_size = mm_to_px(bit_size)

# bits
bits_width = pixel_a4_width // pixel_bit_size
bits_width_no_parity = bits_width - 1
bits_height = pixel_a4_height // pixel_bit_size

# colours
pixel_white = (255, 255, 255)
pixel_black = (0, 0, 0)
pixel_colours = [pixel_white, pixel_black]

# Debug parity
pixel_blue = (0, 0, 255)
pixel_red = (255, 0, 0)
pixel_parity = [pixel_blue, pixel_red]


def create_page(bits=None):
    if bits is None:
        bits = []
    if len(bits) < bits_width_no_parity * bits_height:
        bits = bits + [0] * (bits_width_no_parity * bits_height - len(bits))
    if len(bits) > bits_width_no_parity * bits_height:
        raise ValueError

    assert len(bits) == bits_width_no_parity * bits_height

    a4im = Image.new('RGB',
                     (bits_width, bits_height),
                     pixel_white)  # White

    cur_parity = 0
    for position, bit in enumerate(bits):
        x = position % bits_width_no_parity
        y = position // bits_width_no_parity
        a4im.putpixel((x, y), pixel_colours[bit])

        cur_parity ^= bit
        if 0 == (x + 2) % bits_width:
            a4im.putpixel((x + 1, y), pixel_parity[cur_parity] if DEBUG else pixel_colours[cur_parity])
            cur_parity = 0

    a4im = a4im.resize((pixel_a4_width, pixel_a4_height), Image.NEAREST)

    return a4im

    # a4im.save(filename, 'PDF', quality=100, dpi=(DPI, DPI))


def multi_pages(bits=None, filename=None):
    if bits is None:
        bits = []
    if filename is None:
        filename = "backup.pdf"

    bits = [bits[x:x + (bits_width_no_parity * bits_height)] for x in
            range(0, len(bits), (bits_width_no_parity * bits_height))]

    pdf = []
    for b in bits:
        pdf.append(create_page(b))

    if pdf:
        pdf[0].save(filename, 'PDF', save_all=True, append_images=pdf[1:], quality=100, dpi=(DPI, DPI))


def file_to_bits(file):
    with open(file, "rb") as f:
        data = f.read()
        return [1 if 2 ** i & byte else 0 for i in range(8) for byte in data]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("to_backup", help="File to backup")
    parser.add_argument("-o", "--output", action="store", dest="output")

    args = parser.parse_args()

    bits = file_to_bits(args.to_backup)
    multi_pages(bits, filename=args.output)
