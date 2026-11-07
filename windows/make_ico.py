from PIL import Image, ImageDraw, ImageFont

S = 1024
# Diagonal gradient (blue -> purple), same spirit as the macOS icon
top = (26, 89, 217)      # 0.10, 0.35, 0.85
bottom = (115, 51, 217)  # 0.45, 0.20, 0.85
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
px = img.load()
for y in range(S):
    for x in range(S):
        t = (x + y) / (2 * (S - 1))
        px[x, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)

# Rounded-square mask (inset 52, radius 200)
mask = Image.new("L", (S, S), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([52, 52, S - 52, S - 52], radius=200, fill=255)
out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
out.paste(img, (0, 0), mask)

d = ImageDraw.Draw(out)
# Isometric cube outline (white)
A = (512, 205); B = (698, 312); C = (698, 520); D = (512, 627); E = (326, 520); F = (326, 312)
O = (512, 416)
hexagon = [A, B, C, D, E, F]
d.line(hexagon + [A], fill=(255, 255, 255, 255), width=36, joint="curve")
for P in (B, D, F):
    d.line([O, P], fill=(255, 255, 255, 255), width=36)

# "NUP" text, heavy white, lower area
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 215)
text = "NUP"
bbox = d.textbbox((0, 0), text, font=font)
tw = bbox[2] - bbox[0]
d.text(((S - tw) / 2 - bbox[0], 715), text, font=font, fill=(255, 255, 255, 255))

out.save("/home/hatch/workspace/nup-win/app-icon-1024.png")
out.save("/home/hatch/workspace/nup-win/app.ico",
         sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("ICO_OK")
