'''
Copyright (c) 2001-2017 by SAP SE, Walldorf, Germany.
All rights reserved. Confidential and proprietary.
'''

import argparse
import datetime
import os
import sys
import utils

from os.path import join

pgp_default_key = '3ABCFE23'

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repository', help='specify the repository directory', metavar='DIR', required=True)
    parser.add_argument('-s', '--sign', help='PGP sign the repository', action='store_true', default=False)
    parser.add_argument('-k', '--key', help='The PGP key uid to use for signing', metavar='KEY', required=False)
    args = parser.parse_args()

    repository = args.repository
    pgp_sign = args.sign
    key = args.key

    if key is None:
        key = pgp_default_key

    utils.remove_if_exists(join(repository, 'Packages'))
    utils.remove_if_exists(join(repository, 'Packages.gz'))
    utils.remove_if_exists(join(repository, 'Release'))
    utils.remove_if_exists(join(repository, 'InRelease'))
    utils.remove_if_exists(join(repository, 'Release.gpg'))

    retcode, out, err = utils.run_cmd(['dpkg-scanpackages', '-m', '.', '/dev/null'], cwd=repository, std=True)

    with open(join(repository, 'Packages'), 'w+') as packages_file:
        packages_file.write(out)

    utils.make_gz_archive(join(repository, 'Packages'), join(repository, 'Packages.gz'))

    retcode, out, err = utils.run_cmd(['md5sum', 'Packages'], cwd=repository, std=True)
    packages_md5sum = out.split(' ')[0]
    retcode, out, err = utils.run_cmd(['sha1sum', 'Packages'], cwd=repository, std=True)
    packages_sha1sum = out.split(' ')[0]
    retcode, out, err = utils.run_cmd(['sha256sum', 'Packages'], cwd=repository, std=True)
    packages_sha256sum = out.split(' ')[0]
    retcode, out, err = utils.run_cmd(['sha512sum', 'Packages'], cwd=repository, std=True)
    packages_sha512sum = out.split(' ')[0]

    retcode, out, err = utils.run_cmd(['md5sum', 'Packages.gz'], cwd=repository, std=True)
    packages_gz_md5sum = out.split(' ')[0]
    retcode, out, err = utils.run_cmd(['sha1sum', 'Packages.gz'], cwd=repository, std=True)
    packages_gz_sha1sum = out.split(' ')[0]
    retcode, out, err = utils.run_cmd(['sha256sum', 'Packages.gz'], cwd=repository, std=True)
    packages_gz_sha256sum = out.split(' ')[0]
    retcode, out, err = utils.run_cmd(['sha512sum', 'Packages.gz'], cwd=repository, std=True)
    packages_gz_sha512sum = out.split(' ')[0]

    packages_size = os.path.getsize(join(repository, 'Packages'))
    packages_gz_size = os.path.getsize(join(repository, 'Packages.gz'))

    now = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

    with open(join(repository, 'Release'), 'w+') as release_file:
        release_file.write(str.format('Date: {0}\n', now))
        release_file.write('MD5Sum:\n')
        release_file.write(str.format(' {0} {1:>16s} Packages.gz\n', packages_gz_md5sum, str(packages_gz_size)))
        release_file.write(str.format(' {0} {1:>16s} Packages\n', packages_md5sum, str(packages_size)))
        release_file.write('SHA1:\n')
        release_file.write(str.format(' {0} {1:>16s} Packages.gz\n', packages_gz_sha1sum, str(packages_gz_size)))
        release_file.write(str.format(' {0} {1:>16s} Packages\n', packages_sha1sum, str(packages_size)))
        release_file.write('SHA256:\n')
        release_file.write(str.format(' {0} {1:>16s} Packages.gz\n', packages_gz_sha256sum, str(packages_gz_size)))
        release_file.write(str.format(' {0} {1:>16s} Packages\n', packages_sha256sum, str(packages_size)))
        release_file.write('SHA512:\n')
        release_file.write(str.format(' {0} {1:>16s} Packages.gz\n', packages_gz_sha512sum, str(packages_gz_size)))
        release_file.write(str.format(' {0} {1:>16s} Packages\n', packages_sha512sum, str(packages_size)))
        release_file.write('\n')

    if pgp_sign is True:
        utils.run_cmd(['gpg', '--default-key', key, '--clearsign', '--digest-algo', 'SHA512', '--no-tty', '-o', 'InRelease', 'Release'], cwd=repository)
        utils.run_cmd(['gpg', '--default-key', key, '-abs',        '--digest-algo', 'SHA512', '--no-tty', '-o', 'Release.gpg', 'Release'], cwd=repository)

    return 0

if __name__ == "__main__":
    sys.exit(main())
