from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple, Union, Optional
import random

@dataclass(frozen=True)
class Number:
    value: Fraction

@dataclass(frozen=True)
class BinOp:
    op: str  
    left: Union[Number, 'BinOp']
    right: Union[Number, 'BinOp']

Expr = Union[Number, BinOp]

def format_fraction(fr: Fraction) -> str:
    
    if fr.denominator == 1:
        return str(fr.numerator)
    
    sign = '-' if fr < 0 else ''
    fr = abs(fr)
    integer = fr.numerator // fr.denominator
    remainder = Fraction(fr.numerator % fr.denominator, fr.denominator)
    if integer == 0:
        return f"{sign}{remainder.numerator}/{remainder.denominator}"
    else:
        return f"{sign}{integer}’{remainder.numerator}/{remainder.denominator}"

def expr_to_string(e: Expr) -> str:
    if isinstance(e, Number):
        return format_fraction(e.value)
    
    left = expr_to_string(e.left)
    right = expr_to_string(e.right)
    return f"({left} {e.op} {right})"

def canonical_sig(e: Expr) -> str:
    if isinstance(e, Number):
        return f"N:{e.value.numerator}/{e.value.denominator}"
    if e.op in ['+', '×']:
        a = canonical_sig(e.left)
        b = canonical_sig(e.right)
        s1, s2 = sorted([a, b])
        return f"({s1}{e.op}{s2})"
    else:
        return f"({canonical_sig(e.left)}{e.op}{canonical_sig(e.right)})"

def evaluate(e: Expr) -> Fraction:
    if isinstance(e, Number):
        return e.value
    l = evaluate(e.left)
    r = evaluate(e.right)
    if e.op == '+':
        return l + r
    if e.op == '-':
        return l - r
    if e.op == '×':
        return l * r
    if e.op == '÷':
        if r == 0:
            raise ZeroDivisionError("division by zero")
        return l / r
    raise ValueError("unknown operator")

def random_natural(r: int) -> Fraction:
    return Fraction(random.randint(0, max(0, r - 1)), 1)

def random_proper_fraction(r: int) -> Fraction:
    
    den = random.randint(2, max(2, r - 1))
    num = random.randint(1, den - 1)
    return Fraction(num, den)

def random_mixed_fraction(r: int) -> Fraction:
    
    integer = random.randint(1, max(1, r - 1))
    den = random.randint(2, max(2, r - 1))
    num = random.randint(1, den - 1)
    return Fraction(integer * den + num, den)

def random_value(r: int) -> Fraction:
    choice = random.random()
    if choice < 0.5:
        return random_natural(r)
    elif choice < 0.8:
        return random_proper_fraction(r)
    else:
        return random_mixed_fraction(r)

def random_leaf(r: int) -> Number:
    return Number(random_value(r))

def safe_sub(left: Expr, right: Expr) -> Optional[BinOp]:
    if evaluate(left) >= evaluate(right):
        return BinOp('-', left, right)
    return None

def safe_div(left: Expr, right: Expr) -> Optional[BinOp]:
    
    try:
        if evaluate(right) == 0:
            return None
        res = evaluate(left) / evaluate(right)
        if res > 0 and abs(res) < 1:
            return BinOp('÷', left, right)
    except ZeroDivisionError:
        return None
    return None

def random_binop(r: int, left: Expr, right: Expr) -> Optional[BinOp]:
    op = random.choice(['+', '-', '×', '÷'])
    if op == '+':
        return BinOp('+', left, right)
    if op == '×':
        return BinOp('×', left, right)
    if op == '-':
        return safe_sub(left, right)
    if op == '÷':
        return safe_div(left, right)
    return None

def build_random_expr(r: int, max_ops: int) -> Expr:
    
    current: Expr = random_leaf(r)
    ops = random.randint(1, max_ops)
    for _ in range(ops):
        
        attach_left = random.random() < 0.5
        new_leaf: Expr = random_leaf(r)
        if attach_left:
            cand = random_binop(r, new_leaf, current)
        else:
            cand = random_binop(r, current, new_leaf)
        
        retries = 0
        while cand is None and retries < 5:
            cand = random_binop(r, current if not attach_left else new_leaf,
                                new_leaf if not attach_left else current)
            retries += 1
        if cand is None:
            
            chosen = random.choice(['+', '×'])
            if attach_left:
                cand = BinOp(chosen, new_leaf, current)
            else:
                cand = BinOp(chosen, current, new_leaf)
        current = cand
    return current

def count_ops(e: Expr) -> int:
    if isinstance(e, Number):
        return 0
    return 1 + count_ops(e.left) + count_ops(e.right)

def generate_unique_expressions(n: int, r: int, max_ops: int = 3) -> List[Expr]:
    seen = set()
    result: List[Expr] = []
    attempts = 0
    limit = n * 50  
    while len(result) < n and attempts < limit:
        e = build_random_expr(r, max_ops)
        
        if count_ops(e) > max_ops:
            attempts += 1
            continue
        sig = canonical_sig(e)
        if sig in seen:
            attempts += 1
            continue
        
        seen.add(sig)
        result.append(e)
        attempts += 1
    if len(result) < n:
        raise RuntimeError("Unable to generate enough unique expressions under constraints")
    return result

token_types = {'+', '-', '×', '÷', '(', ')'}

def parse_fraction_token(tok: str) -> Fraction:
    
    if '’' in tok:
        integer_part, frac_part = tok.split('’')
        num_str, den_str = frac_part.split('/')
        integer = int(integer_part)
        num = int(num_str)
        den = int(den_str)
        return Fraction(integer * den + num, den)
    if '/' in tok:
        num_str, den_str = tok.split('/')
        return Fraction(int(num_str), int(den_str))
    return Fraction(int(tok), 1)

def tokenize(expr_line: str) -> List[str]:
    
    s = expr_line.strip()
    if s.endswith('='):
        s = s[:-1].strip()
    
    for ch in ['(', ')', '+', '-', '×', '÷']:
        s = s.replace(ch, f' {ch} ')
    parts = [p for p in s.split() if p]
    return parts

def parse_expr(tokens: List[str], idx: int = 0) -> Tuple[Expr, int]:
    
    def parse_atom(i: int) -> Tuple[Expr, int]:
        tok = tokens[i]
        if tok == '(':
            node, j = parse_expr(tokens, i + 1)
            if j >= len(tokens) or tokens[j] != ')':
                raise ValueError('missing closing )')
            return node, j + 1
        else:
            return Number(parse_fraction_token(tok)), i + 1

    left, i = parse_atom(idx)
    while i < len(tokens):
        op = tokens[i]
        if op not in ['+', '-', '×', '÷']:
            break
        right, i2 = parse_atom(i + 1)
        left = BinOp(op, left, right)
        i = i2
    return left, i

def parse_expression_line(line: str) -> Expr:
    tokens = tokenize(line)
    node, pos = parse_expr(tokens)
    if pos != len(tokens):
        raise ValueError('unexpected tokens at end')
    return node

def write_exercises_and_answers(expressions: List[Expr], exercises_path: str, answers_path: str) -> None:
    with open(exercises_path, 'w', encoding='utf-8') as fe, open(answers_path, 'w', encoding='utf-8') as fa:
        for e in expressions:
            fe.write(f"{expr_to_string(e)} =\n")
            fa.write(f"{format_fraction(evaluate(e))}\n")

def grade(exercises_path: str, answers_path: str, grade_path: str) -> Tuple[List[int], List[int]]:
    with open(exercises_path, 'r', encoding='utf-8') as fe:
        ex_lines = [line.strip() for line in fe if line.strip()]
    with open(answers_path, 'r', encoding='utf-8') as fa:
        ans_lines = [line.strip() for line in fa if line.strip()]
    if len(ex_lines) != len(ans_lines):
        raise ValueError('Exercises and Answers line count mismatch')
    correct: List[int] = []
    wrong: List[int] = []
    for idx, (eline, aline) in enumerate(zip(ex_lines, ans_lines), start=1):
        expr = parse_expression_line(eline)
        expected = evaluate(expr)
        given = parse_fraction_token(aline)
        if given == expected:
            correct.append(idx)
        else:
            wrong.append(idx)
    with open(grade_path, 'w', encoding='utf-8') as fg:
        fg.write(f"Correct: {len(correct)} ({', '.join(map(str, correct))})\n")
        fg.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})\n")
    return correct, wrong