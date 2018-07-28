import argparse
import logging
import sys

from .grepmx import PatternMatcher, MXResolver

def main():
    parser = argparse.ArgumentParser(description='Find emails and match their MX')
    parser.add_argument('files', nargs='*', help='files to grep from', type=argparse.FileType('r'), default=[sys.stdin])
    parser.add_argument('-m', '--mx', help='MX syntax to match, e.g. .yahoodns.? matches mx.yahoodns.net etc.', action='append', default=[])
    parser.add_argument('-s', '--skip', help='Skip lines with no emails found', action='store_true')
    parser.add_argument('-n', '--nameserver', help='Nameserver to use', nargs='*', default=['8.8.8.8', '8.8.4.4'])
    parser.add_argument('-d', '--debug', help='Enable debug logging', action='store_true')
    parser.add_argument('-v', '--invert-match', help='Reverse output regarding mxes', action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    pattern_matcher = PatternMatcher(args.mx)
    mx_resolver = MXResolver(args.nameserver)

    def flush_queue(empty=False):
        for mxes, line in mx_resolver.empty_queue(empty):
            if not args.skip and mxes is None:
                print(line)
            else:
                if pattern_matcher(mxes) != args.invert_match:
                    print(line)

    for f in args.files:
        for line in f:
            line = line.strip()
            mx_resolver.handle_line(line)
            flush_queue()

    flush_queue(True)

if __name__ == '__main__':
    main()