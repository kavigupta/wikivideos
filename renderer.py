
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"

def fit_into(draw, message, width, height, testsize=10_000):
    font = ImageFont.truetype(FONT, size=testsize)
    x, y = draw.textsize(message, font=font)
    scale = min(width / x, height / y)
    font = ImageFont.truetype(FONT, size=int(testsize * scale))
    x, y = draw.textsize(message, font=font)
    return font, x, y

def title_slide(width, height, ratio, message):
    im = Image.new("RGB",(width, height),"black")
    draw = ImageDraw.Draw(im)
    font, x, y = fit_into(draw, message, width * ratio, height)
    draw.text([(width - x) / 2, (height - y) / 2], message, fill="white", font=font)
    return im
