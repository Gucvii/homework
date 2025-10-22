from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from arithmetic import (
    generate_unique_expressions,
    write_exercises_and_answers,
    grade,
)

DEFAULT_MAX_OPS = 3


def cmd_generate(args: argparse.Namespace) -> None:
    n: int = args.n if args.n is not None else 10
    r: int = args.r
    if r is None or r < 1:
        raise ValueError("-r 参数必须给定且为>=1的自然数")
    exprs = generate_unique_expressions(n=n, r=r, max_ops=DEFAULT_MAX_OPS)
    cwd = Path.cwd()
    exercises = cwd / 'Exercises.txt'
    answers = cwd / 'Answers.txt'
    write_exercises_and_answers(exprs, str(exercises), str(answers))
    print(f"已生成 {n} 道题目到 {exercises}")
    print(f"答案已写入 {answers}")


def cmd_grade(args: argparse.Namespace) -> None:
    efile: Optional[str] = args.e
    afile: Optional[str] = args.a
    if not efile or not afile:
        raise ValueError("-e 与 -a 参数必须同时给定")
    epath = Path(efile)
    apath = Path(afile)
    if not epath.exists() or not apath.exists():
        raise FileNotFoundError("题目或答案文件不存在")
    grade_path = Path.cwd() / 'Grade.txt'
    correct, wrong = grade(str(epath), str(apath), str(grade_path))
    print(f"Correct: {len(correct)} ({', '.join(map(str, correct))})")
    print(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})")
    print(f"统计结果已写入 {grade_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='Myapp.exe',
        description='自动生成小学四则运算题目 与 判卷工具',
    )
    parser.add_argument('-n', type=int, help='生成题目数量，默认10')
    parser.add_argument('-r', type=int, help='数值范围，必填，控制自然数与分母 (<r)')
    parser.add_argument('-e', type=str, help='判卷模式：题目文件路径')
    parser.add_argument('-a', type=str, help='判卷模式：答案文件路径')
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.e or args.a:
        cmd_grade(args)
    else:
        if args.r is None:
            parser.error('-r 参数为必填，例如: python main.py -r 10 -n 10')
        cmd_generate(args)


if __name__ == '__main__':
    import cProfile, pstats, io

    pr = cProfile.Profile()
    pr.enable()

    main()

    pr.disable()
    pr.dump_stats("pipeline.prof")
    s = io.StringIO()
    sortby = "tottime"
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())