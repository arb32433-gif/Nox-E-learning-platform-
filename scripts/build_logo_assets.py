import os
import base64
from PIL import Image

# 1. Load original image
src_path = 'Gemini_Generated_Image_uko070uko070uko0.jpg'
img = Image.open(src_path).convert('RGBA')

# 2. Find bounding box of emblem
gray = img.convert('L')
bw = gray.point(lambda p: 255 if p > 70 else 0)
bbox = bw.getbbox()
bx0, by0, bx1, by1 = bbox
bw_w = bx1 - bx0
bw_h = by1 - by0
max_dim = max(bw_w, bw_h)
pad = int(max_dim * 0.08)  # 8% clean visual padding
target_size = max_dim + pad * 2

cx = (bx0 + bx1) // 2
cy = (by0 + by1) // 2

crop_box = (
    cx - target_size // 2,
    cy - target_size // 2,
    cx + target_size // 2,
    cy + target_size // 2
)
cropped = img.crop(crop_box)

# 3. Soft alpha anti-aliasing
r, g, b, _ = cropped.split()
cgray = cropped.convert('L')

def map_alpha(p):
    if p <= 36:
        return 0
    elif p >= 160:
        return 255
    else:
        return int(255 * (p - 36) / (160 - 36))

alpha = cgray.point(map_alpha)

def clean_rgb(p):
    # Brighten slightly and preserve subtle bevel lighting
    return min(255, int(p * 1.05))

clean_r = r.point(clean_rgb)
clean_g = g.point(clean_rgb)
clean_b = b.point(clean_rgb)

logo_clean = Image.merge('RGBA', (clean_r, clean_g, clean_b, alpha))

os.makedirs('assets', exist_ok=True)

# Save variations
# Master transparent PNG
logo_clean.save('assets/nox-logo.png')
# High-res 512x512
logo_512 = logo_clean.resize((512, 512), Image.Resampling.LANCZOS)
logo_512.save('assets/nox-logo-512.png')
# UI sizes
logo_128 = logo_clean.resize((128, 128), Image.Resampling.LANCZOS)
logo_128.save('assets/nox-logo-128.png')
logo_32 = logo_clean.resize((32, 32), Image.Resampling.LANCZOS)
logo_32.save('assets/favicon.png')
logo_32.save('assets/favicon.ico', format='ICO')

# Dark-card preview variant
cropped_dark = img.crop(crop_box)
cropped_dark.resize((512, 512), Image.Resampling.LANCZOS).save('assets/nox-logo-card.png')

# SVG with embedded optimized PNG
with open('assets/nox-logo-512.png', 'rb') as f:
    b64_512 = base64.b64encode(f.read()).decode('utf-8')

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <image href="data:image/png;base64,{b64_512}" width="512" height="512" preserveAspectRatio="xMidYMid meet"/>
</svg>'''

with open('assets/nox-logo.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

print("Assets generated successfully:")
for name in os.listdir('assets'):
    size = os.path.getsize(os.path.join('assets', name))
    print(f" - assets/{name} ({size} bytes)")
