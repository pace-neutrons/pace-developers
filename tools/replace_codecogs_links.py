import re

CODECOGS_SVG_PATTERN=r'\[(.*)\](:|\()\s*(http://latex.codecogs.com/svg.latex\?[^\)\n]*)'

def sanitise(x, keep=['_','-','=']):
    s = "".join([c for c in x if c.isalnum() or c in keep]).rstrip()
    s = s.replace('math','_').replace('=','_eq_').replace('-','_mns_').replace('partial','d')
    return s

def linkname_url(lines):
    """ Extract the link names and URL targets from all lines

    Returns a dictionary with URL keys and link names
    """
    name_per_url = {}
    # Iterate over lines with codecogs URLS
    for line in filter(lambda x: re.search(CODECOGS_SVG_PATTERN, x), lines):
        r = re.search(CODECOGS_SVG_PATTERN, line)
        name_per_url[r.groups()[2]] = r.groups()[0]
    return name_per_url

def fetch_svg(url, linkname, outdir):
    """ Fetch a remote SVG image from the provided URL

    The linkname is sanitised to produce a viable filename which is returned.
    If the target filename already exists it is verified to represent the same
    URL.
    If the target filename does not exist the remote content is fetched and
    written followed by the generating URL.
    """
    import requests, pathlib
    name = sanitise(linkname)
    outPath = pathlib.Path('.','svg',name+'.svg')
    out = str(outPath)
    if outPath.exists():
        # verify that the existing file was generated from the same url
        with open(out,'r') as out_file:
            lines = out_file.readlines()
            # find the (hopefully) one line matching our [link]: url regex
            for line in filter(lambda x: re.search(CODECOGS_SVG_PATTERN, x), lines):
                r = re.search(CODECOGS_SVG_PATTERN, line)
                if linkname not in r.groups()[0] and url not in r.groups()[2]:
                    msg = 'The file {} exists for link {} instead of {}'
                    raise Exception(msg.format(out, r.groups()[0]), linkname)
    else:
        r = requests.get(url)
        if not r.ok:
            raise Exception("Fetching {} failed with reason {}".format(url, r.reason))
        with open(out,'wb') as out_file:
            out_file.write(r.content)
        # add the generating URL as a comment in the SVG file
        with open(out,'a') as out_file:
            comment = '\n<!-- Generated from\n[{}]: {}\n-->'.format(linkname,url)
            out_file.write(comment)
    return out.replace('\\','/') # always use unix-style path separators

def update_lines(lines, url_loc):
    ul = []
    for line in lines:
        r = re.search(CODECOGS_SVG_PATTERN, line)
        if r:
            url = r.groups()[2]
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
        lines = f.readlines()

    outdir = Path(fpath, 'svg')
    if not (outdir.exists() and outdir.is_dir()):
        outdir.mkdir()
    if backup_ext:
        ext = backup_ext if '.' in backup_ext else '.'+backup_ext
        with open(filename+ext, 'w') as f:
            for line in lines:
                f.write(line)
    with open(filename, 'w') as f:
        loc_per_url = {u: fetch_svg(u, n, outdir) for u, n in linkname_url(lines).items()}
        for line in update_lines(lines, loc_per_url):
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
