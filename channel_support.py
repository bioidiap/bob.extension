#!/usr/bin/env python

import re
from conda.exports import get_index


def main(channel_url, name, version, py_ver, get_urls=False):
    # no dot in py_ver
    py_ver = py_ver.replace('.', '')
    # get the channel index
    index = get_index(channel_urls=[channel_url], prepend=False)
    # search if package with the same version exists
    build_number = 0
    urls = []
    for dist in index:
        if dist.name == name and dist.version == version:
            match = re.match('py[2-9][0-9]+', dist.build_string)
            if match and match.group() == 'py{}'.format(py_ver):
                build_number = max(build_number, dist.build_number + 1)
                urls.append(index[dist].url)
    return build_number, urls


if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser(
        description='Return the next build number for a package. Or get a list'
        ' of urls to the existing package.')
    parser.add_argument(
        'channel_url', help='The url or name of the channel.')
    parser.add_argument(
        'package_name', help='Name of the package.')
    parser.add_argument(
        'package_version', help='Version of the package.')
    parser.add_argument(
        'python_version', help='Version of the python.')
    parser.add_argument(
        '-u', '--package-urls', action='store_true',
        help='Optionally output a list of existing packages after the build'
        ' number.')
    parser.add_argument(
        '--log', default=sys.stdout, type=argparse.FileType('w'),
        help='the file where the build number should be written.')
    args = parser.parse_args()
    build_number, urls = main(args.channel_url,
                              args.package_name, args.package_version,
                              args.python_version, args.package_urls)
    args.log.write('{}\n'.format(build_number))
    if args.package_urls:
        args.log.write('\n'.join(urls))
    args.log.close()
