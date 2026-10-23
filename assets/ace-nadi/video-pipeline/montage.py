import sys, os
from PIL import Image
base = os.path.dirname(os.path.abspath(__file__))
ts = [float(x) for x in sys.argv[1:]]
ims = [Image.open(os.path.join(base, 'stills', f's_{t:05.1f}.jpg')) for t in ts]
o = Image.new('RGB', (1920, 540 * ((len(ims) + 1) // 2)), 'white')
for k, i in enumerate(ims):
    o.paste(i, ((k % 2) * 960, (k // 2) * 540))
o.save(os.path.join(base, 'montage.jpg'), quality=85)
