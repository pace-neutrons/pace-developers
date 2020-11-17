import re

PATURL = 'codecogs.com/svg'
PATIMG = r'\[(.*)\]:\s*(.*)'
PATINLINEIMG = r'\[(.*)\]\((.*)\)'

def sanitise(x, keep=[]):
    s = "".join([c for c in x if c.isalnum() or c in keep]).rstrip()
    return s if len(s)<20 else s[:20]

def get_names_urls(lines, parturl=PATURL, pat=PATIMG, pat_inline=PATINLINEIMG):
    nu = [l for l in lines if re.search(parturl, l)]
    d = {}
    for x in nu:
        r = re.search(pat, x)
        if r is None:
            r = re.search(pat_inline, x)
        if r is None:
            continue
        name = sanitise(r.groups()[0])
        url = r.groups()[1]
        d[name] = url
    return d

def fetch_svg(url, name, outdir):
    import requests, pathlib
    outPath = pathlib.Path('.','svg',name+'.svg')
    out = str(outPath)
    if not outPath.exists():
        r = requests.get(url)
        if not r.ok:
            raise Exception("Fetching {} failed with reason {}".format(url, r.reason))
        open(out, 'wb').write(r.content)
    return out.replace('\\','/') # always use unix-style path separators
    
def fetch_urls_locs(name_url, outdir):
    url_loc = {}
    for name, url in name_url.items():
        url_loc[url] = fetch_svg(url, name, outdir)
    return url_loc

def update_lines(lines, url_loc, parturl=PATURL, patimg=PATIMG, patimg_inline=PATINLINEIMG):
    ul = []
    for line in lines:
        if re.search(parturl, line):
            r = re.search(patimg, line)
            if not r:
                r = re.search(patimg_inline, line)
            if not r:
                print('Failing line:\n{}'.format(line))
            url = r.groups()[1]
            if url in url_loc.keys():
                line = line.replace(url, url_loc[url])
            else:
                print('Missed URL? {}'.format(line))
        ul.append(line)
    return ul
    
def replace_codecogs_links(filename, backup_ext=None):
    from pathlib import Path
    cwd = Path().cwd()
    fpath = Path(*Path(filename).absolute().parts[:-1])
    if not cwd.samefile(fpath):
        raise Exception('The current working directory and markdown file directory should be the same')
        
    with open(filename, 'r') as f:
        orig_lines = f.readlines()
    
    outdir = Path(fpath, 'svg')
    if not (outdir.exists() and outdir.is_dir()):
        outdir.mkdir()
    replaced_lines = update_lines(orig_lines, fetch_urls_locs(get_names_urls(orig_lines), outdir))
    if backup_ext:
        ext = backup_ext if '.' in backup_ext else '.'+backup_ext
        with open(filename+ext, 'w') as f:
            for line in orig_lines:
                f.write(line)
    with open(filename, 'w') as f:
        for line in replaced_lines:
            f.write(line)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Replace codecogs svg links with local svg images')
    parser.add_argument('filename', type=str, help='the markdown filename')
    parser.add_argument('-b', '--backup', type=str, help='backup the original file with the given extension')
    args = parser.parse_args()
    
    replace_codecogs_links(args.filename, args.backup)
    #print('replace_codecogs_links({},{})'.format(args.filename, args.backup))
    
# where the per-observation weights, ![w_i](https://latex.codecogs.com/svg.latex?w_i), could be constant or some function of the variance,