'''
Copyright (c) 2019-2022 by SAP SE, Walldorf, Germany.
All rights reserved. Confidential and proprietary.
'''

import argparse
import os
import sys
import utils

from datetime import date
from versions import SapMachineTag

VERSION_DATE_ARG =          '--with-version-date={0}'
VERSION_BUILD_ARG =         '--with-version-build={0}'
VERSION_PRE_ARG =           '--with-version-pre={0}'
VERSION_OPT_ARG =           '--with-version-opt={0}'
VERSION_EXTRA1_ARG =        '--with-version-extra1={0}'
VENDOR_VERSION_STRING_ARG = '--with-vendor-version-string=SapMachine'
VENDOR_NAME_ARG =           '"--with-vendor-name=SAP SE"'
VENDOR_URL_ARG =            '--with-vendor-url=https://sapmachine.io/'
VENDOR_BUG_URL_ARG =        '--with-vendor-bug-url=https://github.com/SAP/SapMachine/issues/new'
VENDOR_VM_BUG_URL_ARG =     '--with-vendor-vm-bug-url=https://github.com/SAP/SapMachine/issues/new'
GTEST_OPT =                 '--with-gtest={0}'

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tag', help='the SapMachine git tag', metavar='TAG')
    parser.add_argument('-b', '--build', help='the build number, overrules any value from tag(s)', metavar='BUILD_NR')
    parser.add_argument('-r', '--release', help='set if this is a release build', action='store_true')
    args = parser.parse_args()

    configure_opts = []

    # initialize major
    major = None

    # initialize build number from args
    build_number = args.build
    if args.build is not None:
        print(str.format("Set build number from parameter: {0}", build_number), file=sys.stderr)

    # parse tag, if given
    tag = None
    if args.tag:
        tag = SapMachineTag.from_string(args.tag)
        if tag is None:
            print(str.format("Tag {0} not recognized as SapMachine tag", args.tag), file=sys.stderr)
            major = utils.calc_major([args.tag])
        else:
            major = tag.get_major()

            # determine build number from tag
            if build_number is None:
                build_number = tag.get_build_number()
                if build_number is not None:
                    print(str.format("Set build number from tag: {0}", build_number), file=sys.stderr)
                else:
                    latest_non_ga_tag = tag.get_latest_non_ga_tag()
                    if latest_non_ga_tag is not None:
                        build_number = latest_non_ga_tag.get_build_number()
                        if build_number is not None:
                            print(str.format("Tag seems to be a ga tag, using build number from latest non-ga tag {0}: {1}",
                                latest_non_ga_tag.as_string(), build_number), file=sys.stderr)

    # if major is still None, try to get it from GIT_REF
    if major is None and 'GIT_REF' in os.environ:
        major = utils.calc_major(filter(None, [os.environ['GIT_REF']]))

    # if major could not be determined, use default
    if major is None:
        major = utils.sapmachine_default_major()

    # set build number
    if build_number is not None:
        configure_opts.append(VERSION_BUILD_ARG.format(build_number))

    # set version date in snapshot builds. In release builds or builds of a certain tag, we rely on DEFAULT_VERSION_DATE in version-numbers.conf
    if not args.release and tag is None:
        release_date = date.today().strftime("%Y-%m-%d")
        print(str.format("Set release date to today: {0}", release_date), file=sys.stderr)
        configure_opts.append(VERSION_DATE_ARG.format(release_date))

    # set version pre
    version_pre = ''
    if not args.release:
        if tag is None:
            version_pre = 'snapshot'
        else:
            version_pre = 'ea'

    if utils.get_system(major) == 'linux' and os.path.isfile('/etc/alpine-release'):
        if not version_pre:
            version_pre = 'beta'
        else:
            version_pre += '-beta'

    configure_opts.append(VERSION_PRE_ARG.format(version_pre))

    # set version opt
    if tag is None:
        configure_opts.append(VERSION_OPT_ARG.format(release_date))
    else:
        if args.release and utils.sapmachine_is_lts(major):
            if major < 15:
                configure_opts.append(VERSION_OPT_ARG.format('LTS-sapmachine'))
            else:
                configure_opts.append(VERSION_OPT_ARG.format('LTS'))
        else:
            if major < 15:
                configure_opts.append(VERSION_OPT_ARG.format('sapmachine'))
            else:
                configure_opts.append(VERSION_OPT_ARG.format(''))

    # set version extra1 arg (= sap version)
    if tag is not None and tag.get_version_sap() is not None:
        configure_opts.append(VERSION_EXTRA1_ARG.format(tag.get_version_sap()))

    # set vendor version string
    if (tag is None or
        (major > 14) or
        (major == 14 and tag.get_update() > 1) or
        (major == 11 and tag.get_update() > 7)):
        configure_opts.append(VENDOR_VERSION_STRING_ARG)

    # set other vendor options
    configure_opts.append(VENDOR_NAME_ARG)
    configure_opts.append(VENDOR_URL_ARG)
    configure_opts.append(VENDOR_BUG_URL_ARG)
    configure_opts.append(VENDOR_VM_BUG_URL_ARG)

    # set gtest option
    if 'GTEST_DIR' in os.environ and major >= 15:
        configure_opts.append(GTEST_OPT.format(os.environ['GTEST_DIR']))

    print(' '.join(configure_opts))

    return 0

if __name__ == "__main__":
    sys.exit(main())
