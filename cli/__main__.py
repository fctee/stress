# -*- coding: utf-8 -*-
from cli.parser import get_parser


def main(argv=None):
    ap = get_parser()
    args = ap.parse_args(argv)
    print(argv)
    print(args)
    if args.action == "info":
        from cli.info import get_script_info
        print(get_script_info(args.script))
    elif args.action == "report":
        from report.report import main as report_main
        report_main(args)
    elif args.action == "run":
        from cli.runner import run_script
        run_script(args)
    else:
        ap.print_help()


if __name__ == '__main__':
    main()
