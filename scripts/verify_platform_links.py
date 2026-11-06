import os, re

comp = 'Components'
files = [f for f in os.listdir(comp) if f.endswith('.html')]

errors = []
for fname in files:
    fpath = os.path.join(comp, fname)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # check html hrefs
    hrefs = re.findall(r'href=[\'"]([^\'"]+\.html[^\'"]*)[\'"]', content)
    locs = re.findall(r'location\.href\s*=\s*[\'"]([^\'"]+\.html)[\'"]', content)
    app_urls = re.findall(r'APP_URL\s*=\s*[\'"]([^\'"]+\.html)[\'"]', content)
    portal_urls = re.findall(r'PORTAL_URL\s*=\s*[\'"]([^\'"]+\.html)[\'"]', content)

    for target in hrefs + locs + app_urls + portal_urls:
        # strip query or hash
        clean_target = target.split('#')[0].split('?')[0]
        if not clean_target:
            continue
        target_path = os.path.join(comp, clean_target)
        if not os.path.exists(target_path):
            errors.append(f"{fname} -> {target} (Target not found at {target_path})")

    # check src
    srcs = re.findall(r'src=[\'"]([^\'"]+)[\'"]', content)
    for s in srcs:
        if s.startswith('http') or s.startswith('data:'):
            continue
        clean_s = s.split('?')[0].split('#')[0]
        # check in Components
        in_comp = os.path.exists(os.path.join(comp, clean_s))
        in_root = os.path.exists(clean_s)
        if not in_comp and not in_root:
            errors.append(f"{fname} -> src {s} not found")

if errors:
    print("Found errors:")
    for e in errors:
        print("  ERROR:", e)
else:
    print("ALL LINKS AND ASSETS VERIFIED SUCCESSFULLY! NO 404s OR BROKEN REFERENCES.")
