from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
from arithmetic import (
    generate_unique_expressions,
    write_exercises_and_answers,
    grade,
    expr_to_string,
    evaluate,
    format_fraction,
)

st.set_page_config(page_title="四则运算生成与判卷", page_icon="➗", layout="centered")

st.title("小学四则运算题目生成与判卷")

TAB_GEN, TAB_GRADE = st.tabs(["生成题目", "判卷统计"]) 

with TAB_GEN:
    st.subheader("生成 Exercises.txt 与 Answers.txt")
    r = st.number_input("数值范围 r (控制自然数与分母 < r)", min_value=1, value=10)
    n = st.number_input("题目数量 n", min_value=1, max_value=10000, value=10)
    max_ops = st.slider("每题最大运算符个数", 1, 3, 3)
    if st.button("开始生成"):
        t0 = time.time()
        exprs = generate_unique_expressions(n=int(n), r=int(r), max_ops=int(max_ops))
        t1 = time.time()
        out_dir = Path.cwd()
        ex_path = out_dir / 'Exercises.txt'
        ans_path = out_dir / 'Answers.txt'
        write_exercises_and_answers(exprs, str(ex_path), str(ans_path))
        st.success(f"已生成 {n} 道题目到 {ex_path}，答案写入 {ans_path}。用时 {(t1-t0):.3f}s")
        st.caption("预览前5题：")
        for e in exprs[:5]:
            st.code(f"{expr_to_string(e)} =\n答案：{format_fraction(evaluate(e))}")

with TAB_GRADE:
    st.subheader("读取题目与答案，输出 Grade.txt")
    e_file = st.text_input("题目文件路径 (Exercises.txt)", value=str(Path.cwd() / 'Exercises.txt'))
    a_file = st.text_input("答案文件路径 (Answers.txt)", value=str(Path.cwd() / 'Answers.txt'))
    if st.button("开始判卷"):
        grade_path = Path.cwd() / 'Grade.txt'
        correct, wrong = grade(e_file, a_file, str(grade_path))
        st.success(f"已输出 {grade_path}")
        st.write(f"Correct: {len(correct)} ({', '.join(map(str, correct))})")
        st.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})")