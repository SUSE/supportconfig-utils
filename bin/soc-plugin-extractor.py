#!/usr/bin/env python
import argparse
import os
import StringIO
import sys


def parse_fname(line):
    line = line.rstrip()
    if line.endswith("Last 10000 Lines"):
        return line[2:-19]
    elif line.endswith("- File not found"):
        return None
    else:
        return line[2:]


def print_inner_files(sc_file, pattern):
    with open(sc_file) as f:
        while True:
            line = f.readline()
            if not line:
                break
            if line.startswith("# /"):
                fname = parse_fname(line)
                if not fname:
                    continue
                if pattern and pattern not in fname:
                    continue
                print(fname)


def write_file(base, fname, content):
    if os.path.isabs(fname):
        # strip leading '/' - is this needed for os.path.join?
        fname = fname[1:]
    path = os.path.join(base, fname)
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(path, 'w') as f:
        f.write(content)
    print("wrote: %s" % path)


def extract(sc_file, dest, pattern):
    fname, out_buf = None, None

    with open(sc_file) as f:
        while True:
            line = f.readline()
            if not line:
                # EOF
                if out_buf:
                    write_file(dest, fname, out_buf.getvalue())
                break
            elif line.startswith("# /"):
                fname = parse_fname(line)
                if fname is None:
                    continue
                if pattern and pattern not in fname:
                    continue
                out_buf = StringIO.StringIO()
            elif line.startswith("#==[") and out_buf:
                # write out the previous file
                write_file(dest, fname, out_buf.getvalue())
                out_buf = None
            elif out_buf:
                out_buf.write(line)


def grab_args():
    parser = argparse.ArgumentParser(
        description="Extract specific files from "
                    "plugin-suse_openstack_cloud.txt.")
    parser.add_argument(
        '--sc',
        help="Full path of plugin-suse_openstack_cloud.txt. "
             "Looks in current dir by default.",
        default="plugin-suse_openstack_cloud.txt")
    parser.add_argument(
        '--ls', '-l',
        help="Only list files, do not extract.",
        action="store_true")
    parser.add_argument(
        "--pattern", '-p',
        help="Filename pattern to extract or list, e.g. nova. "
             "Extracts or lists all files if none specified.")
    parser.add_argument(
        '--dest', '-d',
        help="Destination dir to extract files to, will create if needed. "
             "Defaults to $CWD/rootfs/",
        default="rootfs")

    args = parser.parse_args()
    if not os.path.exists(args.sc):
        parser.print_help()
        sys.exit()

    return args


def main():
    args = grab_args()
    if args.ls:
        print_inner_files(args.sc, args.pattern)
    else:
        extract(args.sc, args.dest, args.pattern)


if __name__ == "__main__":
    main()
