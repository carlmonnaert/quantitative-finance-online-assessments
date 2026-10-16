#!/usr/bin/env python3
"""
Generate 88 unique static and dynamically parameterized Quant OA questions across:
1. Linear Algebra & Calculus (22 unique questions: 14 MCQ, 8 Numeric)
2. Probability & Statistics (22 unique questions: 14 MCQ, 8 Numeric)
3. Coding & Algorithms (22 unique questions: 15 MCQ, 7 Numeric)
4. Machine Learning & Data Science (22 unique questions: 15 MCQ, 7 Numeric)

Every template produces at most ONE question per run so no question stem ever
repeats in a test session.
"""

from __future__ import annotations

import json
import math
import random
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_DIR = ROOT / "question-bank" / "questions"
MANIFEST_PATH = ROOT / "question-bank" / "manifest.json"


def make_mcq_options(
    correct_label: str, distractors: list[str]
) -> tuple[list[dict[str, str]], str]:
    """Shuffle correct label and 3 distinct distractors into A, B, C, D options."""
    def add_if_valid(value: str, current: list[str]) -> None:
        candidate = value.strip()
        if (
            candidate
            and candidate != correct_label
            and candidate not in current
        ):
            current.append(candidate)

    def generate_fallback_distractors(excluded: list[str], needed: int) -> list[str]:
        generated: list[str] = []
        target = correct_label.strip()

        if "/" in target:
            try:
                frac = Fraction(target)
                numerator, denominator = frac.numerator, frac.denominator
                fallback_values = [
                    Fraction(numerator + 1, denominator),
                    Fraction(numerator - 1, denominator),
                    Fraction(numerator, denominator + 1),
                    Fraction(numerator + denominator, denominator),
                ]
                for fallback in fallback_values:
                    add_if_valid(str(fallback), generated)
            except (ValueError, ZeroDivisionError):
                pass
        else:
            percent_mode = target.endswith("%")
            numeric_raw = target[:-1] if percent_mode else target
            try:
                numeric_value = float(numeric_raw)
                decimals = 0
                if "." in numeric_raw:
                    decimals = len(numeric_raw.split(".")[-1])
                step = 1.0 if decimals == 0 else 10 ** (-decimals)

                fallback_values = [
                    numeric_value + step,
                    numeric_value - step,
                    numeric_value + 2 * step,
                    numeric_value - 2 * step,
                    numeric_value * 2,
                ]

                for fallback in fallback_values:
                    if decimals == 0:
                        formatted = str(int(round(fallback)))
                    else:
                        formatted = f"{round(fallback, decimals):.{decimals}f}".rstrip("0").rstrip(".")
                    if percent_mode:
                        formatted = f"{formatted}%"
                    add_if_valid(formatted, generated)
            except ValueError:
                pass

        text_fallbacks = [
            "Cannot be determined from the given information",
            "Insufficient information",
            "None of the above",
            "All of the above",
        ]
        for fallback in text_fallbacks:
            add_if_valid(fallback, generated)

        dedup_excluded = set(excluded)
        return [item for item in generated if item not in dedup_excluded][:needed]

    unique_distractors: list[str] = []
    for d in distractors:
        if d != correct_label and d not in unique_distractors:
            unique_distractors.append(d)

    if len(unique_distractors) < 3:
        needed = 3 - len(unique_distractors)
        fallback_distractors = generate_fallback_distractors(unique_distractors, needed)
        unique_distractors.extend(fallback_distractors)

    if len(unique_distractors) < 3:
        raise ValueError(
            f"Unable to build unique distractors for correct option '{correct_label}'."
        )

    pool = [correct_label] + unique_distractors[:3]
    random.shuffle(pool)
    letters = ["A", "B", "C", "D"]
    options = [{"value": letters[i], "label": pool[i]} for i in range(4)]
    correct_value = letters[pool.index(correct_label)]
    return options, correct_value


# ============================================================================
# 1. LINEAR ALGEBRA & CALCULUS (14 MCQ, 8 Numeric = 22 Unique Questions)
# ============================================================================


def generate_linear_algebra_calculus() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []

    # --- 8 Unique Dynamic NUMERIC Questions ---

    # 1. Largest eigenvalue of a 2x2 matrix
    l1 = random.randint(-4, 4)
    l2 = random.randint(l1 + 2, 9)
    a = l1 + random.randint(1, 3)
    d = (l1 + l2) - a
    b, c = 1, a * d - (l1 * l2)
    questions.append({
        "id": "la-num-eigen-max",
        "type": "numeric",
        "title": "Largest Eigenvalue of a 2×2 Matrix",
        "prompt": f"Consider the 2×2 matrix A = [[{a}, {b}], [{c}, {d}]]. What is the larger eigenvalue of A?",
        "answer": str(l2),
        "explanation": f"tr(A) = {a+d}, det(A) = {l1*l2}. Solving λ² - ({a+d})λ + ({l1*l2}) = 0 gives λ = {l1}, {l2}.",
    })

    # 2. Trace of A^2
    a2, b2, c2, d2 = random.randint(1, 5), random.randint(-3, 4), random.randint(-3, 4), random.randint(1, 5)
    tr_a2 = a2 * a2 + d2 * d2 + 2 * b2 * c2
    questions.append({
        "id": "la-num-trace-sq",
        "type": "numeric",
        "title": "Trace of a Squared Matrix",
        "prompt": f"Let A = [[{a2}, {b2}], [{c2}, {d2}]]. Compute Tr(A²), the trace of A².",
        "answer": str(tr_a2),
        "explanation": f"Tr(A²) = a² + d² + 2bc = {a2**2} + {d2**2} + 2({b2})({c2}) = {tr_a2}.",
    })

    # 3. Sylvester's Criterion (Positive Definiteness threshold)
    a3 = random.randint(2, 5)
    b3 = a3 * random.randint(2, 4)
    min_k = (b3 * b3) // a3 + 1
    questions.append({
        "id": "la-num-pos-def",
        "type": "numeric",
        "title": "Strict Positive Definiteness Threshold",
        "prompt": (
            f"Let M = [[{a3}, {b3}], [{b3}, k]] be a symmetric 2×2 matrix. "
            f"What is the smallest INTEGER value of k such that M is strictly positive definite?"
        ),
        "answer": str(min_k),
        "explanation": f"det(M) = {a3}k - {b3}² > 0 ⇒ k > {b3*b3 // a3}, so the smallest integer is {min_k}.",
    })

    # 4. Orthogonal Projection Component in R^3
    v4 = random.choice([(1, 2, 2), (2, 1, 2), (1, 2, 3)])
    norm_sq = sum(x * x for x in v4)
    scale = random.randint(2, 5)
    w4 = (v4[1], -v4[0], 0)
    u4 = tuple(scale * v4[j] + w4[j] for j in range(3))
    proj_first = scale * v4[0]
    questions.append({
        "id": "la-num-ortho-proj",
        "type": "numeric",
        "title": "Orthogonal Projection Component",
        "prompt": (
            f"Let u = ({u4[0]}, {u4[1]}, {u4[2]}) and v = ({v4[0]}, {v4[1]}, {v4[2]}). "
            f"Find the first coordinate (x-component) of the orthogonal projection of u onto v."
        ),
        "answer": str(proj_first),
        "explanation": f"proj_v(u) = ((u·v)/||v||²)v = {scale}v, so its first coordinate is {scale}×{v4[0]} = {proj_first}.",
    })

    # 5. Gradient Norm (Maximum Rate of Change)
    gx, gy, norm5 = random.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)])
    c_xy = 2
    c_x2 = (gx - c_xy) // 2
    b_y = gy - c_xy
    questions.append({
        "id": "calc-num-grad-norm",
        "type": "numeric",
        "title": "Maximum Rate of Change (Gradient Norm)",
        "prompt": f"Let f(x, y) = {c_x2}x² + {c_xy}xy + {b_y}y. What is the maximum rate of change of f at (1, 1)?",
        "answer": str(norm5),
        "explanation": f"∇f(1, 1) = ({gx}, {gy}), so ||∇f(1, 1)|| = √({gx}² + {gy}²) = {norm5}.",
    })

    # 6. Constrained Optimization on a Circle (Lagrange Multipliers)
    a6, b6, norm6 = random.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13)])
    r6 = random.randint(2, 5)
    max_val6 = norm6 * r6
    questions.append({
        "id": "calc-num-lagrange-circle",
        "type": "numeric",
        "title": "Constrained Maximum on a Circle",
        "prompt": f"Find the maximum value of f(x, y) = {a6}x + {b6}y subject to x² + y² = {r6*r6}.",
        "answer": str(max_val6),
        "explanation": f"By Cauchy-Schwarz, max is √({a6}² + {b6}²) · √({r6*r6}) = {norm6} × {r6} = {max_val6}.",
    })

    # 7. Maclaurin Series Coefficient
    a7 = random.randint(1, 4)
    b7 = random.randint(1, 6)
    coeff7 = Fraction(a7 * a7, 2) + b7
    ans7 = str(float(coeff7)) if coeff7.denominator != 1 else str(coeff7.numerator)
    questions.append({
        "id": "calc-num-maclaurin-coeff",
        "type": "numeric",
        "title": "Maclaurin Series Quadratic Coefficient",
        "prompt": (
            f"Let f(x) = exp({a7}x) + {b7}x². In the Maclaurin series expansion of f(x) around x = 0, "
            f"what is the coefficient of x²? (Express as a decimal if non-integer)"
        ),
        "answer": ans7,
        "explanation": f"Coefficient of x² in exp({a7}x) is {a7}²/2 = {a7*a7/2}. Adding {b7} gives {ans7}.",
    })

    # 8. Leibniz Integral Rule
    x_val = random.randint(2, 4)
    c_int = random.randint(1, 5)
    leibniz_ans = (x_val * x_val + c_int) * (2 * x_val)
    questions.append({
        "id": "calc-num-leibniz-rule",
        "type": "numeric",
        "title": "Leibniz Integral Rule Derivative",
        "prompt": f"Let F(x) = ∫_{{0}}^{{x²}} (t + {c_int}) dt. Compute the derivative F'({x_val}).",
        "answer": str(leibniz_ans),
        "explanation": f"F'(x) = (x² + {c_int}) · 2x. At x = {x_val}, F'({x_val}) = ({x_val**2} + {c_int}) × {2*x_val} = {leibniz_ans}.",
    })

    # --- 14 Unique MCQ Questions (Dynamic + Curated) ---

    # 9. Determinant of Scaled Inverse Matrix (Dynamic MCQ)
    n_dim = random.choice([3, 4])
    scale_k = random.choice([2, 3])
    det_a = random.choice([2, 3, 4])
    num9 = scale_k**n_dim
    frac9 = Fraction(num9, det_a)
    ans9 = f"{frac9.numerator}/{frac9.denominator}" if frac9.denominator != 1 else str(frac9.numerator)
    dist9 = [
        str(scale_k * det_a),
        f"{scale_k}/{det_a}",
        str(num9 * det_a),
    ]
    opts9, letter9 = make_mcq_options(ans9, dist9)
    questions.append({
        "id": "la-mcq-det-inverse",
        "type": "mcq",
        "title": "Determinant of Scaled Inverse Matrix",
        "prompt": f"Let A be an invertible {n_dim}×{n_dim} matrix with det(A) = {det_a}. What is det({scale_k} A⁻¹)?",
        "options": opts9,
        "answer": letter9,
        "explanation": f"det({scale_k} A⁻¹) = {scale_k}^{n_dim} / det(A) = {num9} / {det_a} = {ans9}.",
    })

    # 10. Frobenius Norm from Singular Values (Dynamic MCQ)
    s1, s2, s3, frob = random.choice([(6, 3, 2, 7), (4, 4, 2, 6), (8, 4, 1, 9), (12, 4, 3, 13)])
    opts10, letter10 = make_mcq_options(str(frob), [str(s1), str(s1 + s2 + s3), str(frob * frob)])
    questions.append({
        "id": "la-mcq-frobenius-svd",
        "type": "mcq",
        "title": "Frobenius Norm from Singular Values",
        "prompt": f"A matrix A has non-zero singular values σ₁ = {s1}, σ₂ = {s2}, and σ₃ = {s3}. What is its Frobenius norm ||A||_F?",
        "options": opts10,
        "answer": letter10,
        "explanation": f"||A||_F = √(σ₁² + σ₂² + σ₃²) = √({s1**2} + {s2**2} + {s3**2}) = {frob}.",
    })

    # 11. PolynomialEigenvalue Transformation (Dynamic MCQ)
    ev = random.randint(2, 4)
    c_poly = random.randint(2, 5)
    poly_ev = ev**3 - c_poly * ev + 1
    opts11, letter11 = make_mcq_options(str(poly_ev), [str(ev**3), str(ev**2 - c_poly), str(poly_ev + c_poly)])
    questions.append({
        "id": "la-mcq-poly-eigen",
        "type": "mcq",
        "title": "Eigenvalue of a Matrix Polynomial",
        "prompt": f"If v is an eigenvector of matrix A corresponding to eigenvalue λ = {ev}, what is the eigenvalue of B = A³ - {c_poly}A + I corresponding to v?",
        "options": opts11,
        "answer": letter11,
        "explanation": f"Bv = (λ³ - {c_poly}λ + 1)v = ({ev}³ - {c_poly}×{ev} + 1)v = {poly_ev}v.",
    })

    # 12. Rank-Nullity Theorem (Dynamic MCQ)
    cols = random.randint(7, 12)
    rows = random.randint(5, 9)
    rank = random.randint(2, min(rows, cols) - 1)
    nullity = cols - rank
    opts12, letter12 = make_mcq_options(str(nullity), [str(rows - rank), str(cols + rows - rank), str(rank)])
    questions.append({
        "id": "la-mcq-rank-nullity",
        "type": "mcq",
        "title": "Dimension of the Null Space (Rank-Nullity)",
        "prompt": f"Let A be a {rows}×{cols} real matrix (with {rows} rows and {cols} columns) of rank {rank}. What is the dimension of the null space (kernel) of A?",
        "options": opts12,
        "answer": letter12,
        "explanation": f"By the Rank-Nullity Theorem, nullity(A) = n_cols - rank(A) = {cols} - {rank} = {nullity}.",
    })

    # 13-22. Curated Static MCQs
    static_mcqs = [
        {
            "id": "la-mcq-idempotent",
            "type": "mcq",
            "title": "Eigenvalues of a Projection Matrix",
            "prompt": "If P is a real n×n idempotent matrix (meaning P² = P), which of the following can be eigenvalues of P?",
            "options": [
                {"value": "A", "label": "Only 0 and 1"},
                {"value": "B", "label": "Only -1, 0, and 1"},
                {"value": "C", "label": "Any real number in [0, 1]"},
                {"value": "D", "label": "Only 1 and -1"},
            ],
            "answer": "A",
            "explanation": "Pv = λv ⇒ P²v = λ²v = λv ⇒ λ ∈ {0, 1}.",
        },
        {
            "id": "la-mcq-skew-sym",
            "type": "mcq",
            "title": "Determinant of Odd-Dimensional Skew-Symmetric Matrix",
            "prompt": "If A is a 5×5 real skew-symmetric matrix (Aᵀ = -A), what must be true about det(A)?",
            "options": [
                {"value": "A", "label": "det(A) = 0 always"},
                {"value": "B", "label": "det(A) = 1 or -1"},
                {"value": "C", "label": "det(A) is strictly positive"},
                {"value": "D", "label": "det(A) is purely imaginary and non-zero"},
            ],
            "answer": "A",
            "explanation": "det(A) = det(Aᵀ) = det(-A) = (-1)⁵ det(A) = -det(A) ⇒ det(A) = 0.",
        },
        {
            "id": "la-mcq-orthogonal-mat",
            "type": "mcq",
            "title": "Properties of Orthogonal Matrices",
            "prompt": "Let Q be an n×n real orthogonal matrix (QᵀQ = I). Which statement is always true?",
            "options": [
                {"value": "A", "label": "All eigenvalues of Q have complex modulus (absolute value) equal to 1"},
                {"value": "B", "label": "All eigenvalues of Q are real and equal to ±1"},
                {"value": "C", "label": "det(Q) is always equal to +1"},
                {"value": "D", "label": "Q is always symmetric"},
            ],
            "answer": "A",
            "explanation": "Orthogonal transformations preserve Euclidean norm: ||Qv|| = ||v|| ⇒ |λ| = 1.",
        },
        {
            "id": "la-mcq-cholesky",
            "type": "mcq",
            "title": "Requirement for Cholesky Decomposition",
            "prompt": "For a real matrix A to admit a unique Cholesky decomposition A = LLᵀ where L is lower triangular with strictly positive diagonal entries, A must be:",
            "options": [
                {"value": "A", "label": "Symmetric and strictly positive definite"},
                {"value": "B", "label": "Any invertible square matrix"},
                {"value": "C", "label": "Orthogonal and diagonalizable"},
                {"value": "D", "label": "Skew-symmetric and full rank"},
            ],
            "answer": "A",
            "explanation": "Cholesky factorization A = LLᵀ with L_ii > 0 exists uniquely iff A is symmetric positive definite.",
        },
        {
            "id": "la-mcq-gram-matrix",
            "type": "mcq",
            "title": "Rank of the Gram Matrix AᵀA",
            "prompt": "For any real m×n matrix A, how does the rank of AᵀA relate to the rank of A?",
            "options": [
                {"value": "A", "label": "rank(AᵀA) = rank(A) always"},
                {"value": "B", "label": "rank(AᵀA) = min(m, n)"},
                {"value": "C", "label": "rank(AᵀA) = (rank(A))²"},
                {"value": "D", "label": "rank(AᵀA) ≤ rank(A), with strict inequality when m < n"},
            ],
            "answer": "A",
            "explanation": "A and AᵀA share the exact same null space (Ax = 0 ⇔ AᵀAx = 0), so their ranks are identical.",
        },
        {
            "id": "calc-mcq-gaussian-int",
            "type": "mcq",
            "title": "Gaussian Integral Evaluation",
            "prompt": "What is the exact value of the improper integral ∫_{-∞}^{∞} exp(-3x²) dx?",
            "options": [
                {"value": "A", "label": "√(π / 3)"},
                {"value": "B", "label": "√(3π)"},
                {"value": "C", "label": "π / 3"},
                {"value": "D", "label": "√π / 3"},
            ],
            "answer": "A",
            "explanation": "∫_{-∞}^{∞} exp(-a x²) dx = √(π / a) = √(π / 3).",
        },
        {
            "id": "calc-mcq-hessian-class",
            "type": "mcq",
            "title": "Critical Point Classification via Hessian",
            "prompt": "Let f(x, y) = x³ - 3xy + y³. How are its critical points (0, 0) and (1, 1) classified?",
            "options": [
                {"value": "A", "label": "(0, 0) is a saddle point; (1, 1) is a local minimum"},
                {"value": "B", "label": "(0, 0) is a local maximum; (1, 1) is a local minimum"},
                {"value": "C", "label": "Both (0, 0) and (1, 1) are saddle points"},
                {"value": "D", "label": "(0, 0) is a saddle point; (1, 1) is a local maximum"},
            ],
            "answer": "A",
            "explanation": "H = [[6x, -3], [-3, 6y]]. det(H(0,0)) = -9 < 0 (saddle); det(H(1,1)) = 27 > 0, H₁₁ = 6 > 0 (local min).",
        },
        {
            "id": "calc-mcq-ito-lemma",
            "type": "mcq",
            "title": "Itô's Lemma / Stochastic Calculus Differential",
            "prompt": "Let W_t be a standard Brownian motion with (dW_t)² = dt. By Itô's Lemma, what is the stochastic differential d(W_t²)?",
            "options": [
                {"value": "A", "label": "2 W_t dW_t + dt"},
                {"value": "B", "label": "2 W_t dW_t"},
                {"value": "C", "label": "2 W_t dW_t + 2 dt"},
                {"value": "D", "label": "W_t dW_t + 0.5 dt"},
            ],
            "answer": "A",
            "explanation": "For f(x) = x², df(W_t) = f'(W_t) dW_t + 0.5 f''(W_t) (dW_t)² = 2 W_t dW_t + dt.",
        },
        {
            "id": "calc-mcq-gamma-half",
            "type": "mcq",
            "title": "Gamma Function at One-Half",
            "prompt": "Recall the Gamma function Γ(z) = ∫_{0}^{∞} t^{z-1} e^{-t} dt. What is the exact value of Γ(1/2)?",
            "options": [
                {"value": "A", "label": "√π"},
                {"value": "B", "label": "π / 2"},
                {"value": "C", "label": "2 √π"},
                {"value": "D", "label": "1 / √π"},
            ],
            "answer": "A",
            "explanation": "Substituting t = u² transforms Γ(1/2) into 2 ∫_{0}^{∞} e^{-u²} du = √π.",
        },
        {
            "id": "calc-mcq-harmonic-pseries",
            "type": "mcq",
            "title": "Convergence of p-Series and Alternating Series",
            "prompt": "Consider the series S₁ = ∑_{n=1}^{∞} 1 / n and S₂ = ∑_{n=1}^{∞} (-1)^{n+1} / n. Which statement is true?",
            "options": [
                {"value": "A", "label": "S₁ diverges, while S₂ converges conditionally to ln(2)"},
                {"value": "B", "label": "Both S₁ and S₂ converge to ln(2)"},
                {"value": "C", "label": "Both S₁ and S₂ diverge"},
                {"value": "D", "label": "S₁ diverges, while S₂ converges absolutely to π / 4"},
            ],
            "answer": "A",
            "explanation": "The harmonic series S₁ diverges; the alternating harmonic series S₂ converges conditionally to ln(2).",
        },
    ]

    questions.extend(static_mcqs)
    return questions


# ============================================================================
# 2. PROBABILITY & STATISTICS (14 MCQ, 8 Numeric = 22 Unique Questions)
# ============================================================================


def generate_probability_statistics() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []

    # --- 8 Unique Dynamic NUMERIC Questions ---

    # 1. Two-Asset Portfolio Variance
    s1 = random.choice([10, 20, 30])
    s2 = random.choice([20, 40])
    rho = random.choice([-0.5, 0.25, 0.5])
    var_p = 0.25 * (s1**2 + s2**2 + 2 * rho * s1 * s2)
    ans_var = str(int(var_p)) if var_p.is_integer() else str(var_p)
    questions.append({
        "id": "prob-num-port-var",
        "type": "numeric",
        "title": "Two-Asset Portfolio Variance",
        "prompt": (
            f"Asset X has return standard deviation σ_X = {s1} and Asset Y has σ_Y = {s2}, "
            f"with correlation ρ = {rho}. What is the variance of P = 0.5 X + 0.5 Y?"
        ),
        "answer": ans_var,
        "explanation": f"Var(0.5X + 0.5Y) = 0.25({s1**2} + {s2**2} + 2({rho})({s1})({s2})) = {ans_var}.",
    })

    # 2. Expected Maximum of i.i.d. Uniform(0, L)
    n_unif = random.randint(2, 5)
    length = (n_unif + 1) * random.randint(2, 6)
    exp_max = (n_unif * length) // (n_unif + 1)
    questions.append({
        "id": "prob-num-unif-max",
        "type": "numeric",
        "title": "Expected Maximum of Uniform Random Variables",
        "prompt": (
            f"Let U₁, ..., U_{n_unif} be {n_unif} i.i.d. Uniform(0, {length}) random variables. "
            f"What is E[max(U₁, ..., U_{n_unif})]?"
        ),
        "answer": str(exp_max),
        "explanation": f"E[max] = (n / (n + 1)) · L = ({n_unif}/{n_unif + 1}) × {length} = {exp_max}.",
    })

    # 3. Geometric Expected Waiting Time
    p_pct = random.choice([10, 20, 25, 50])
    wait_flips = 100 // p_pct
    questions.append({
        "id": "prob-num-geom-wait",
        "type": "numeric",
        "title": "Expected Trials Until First Success",
        "prompt": (
            f"A biased coin lands Heads with probability p = {p_pct}%. You flip it repeatedly until the first "
            f"Heads appears. What is the expected total number of flips?"
        ),
        "answer": str(wait_flips),
        "explanation": f"For Geometric(p), E[N] = 1 / p = 100 / {p_pct} = {wait_flips}.",
    })

    # 4. Optimal Weight for Combining Two Unbiased Estimators
    v1, v2 = random.choice([(1, 3), (3, 1), (1, 4), (4, 1), (2, 3), (3, 7)])
    w_opt = round(v2 / (v1 + v2), 2)
    questions.append({
        "id": "stat-num-opt-weight",
        "type": "numeric",
        "title": "Minimum-Variance Unbiased Linear Combination",
        "prompt": (
            f"Let θ̂₁ and θ̂₂ be independent unbiased estimators of θ with variances Var(θ̂₁) = {v1} "
            f"and Var(θ̂₂) = {v2}. What weight w ∈ [0, 1] minimizes Var(w θ̂₁ + (1 - w) θ̂₂)? (Give exact decimal)"
        ),
        "answer": str(w_opt),
        "explanation": f"w* = Var(θ̂₂) / (Var(θ̂₁) + Var(θ̂₂)) = {v2} / ({v1} + {v2}) = {w_opt}.",
    })

    # 5. Conditional Expectation of Independent Poissons
    lam1, lam2 = random.randint(2, 5), random.randint(2, 5)
    tot_n = (lam1 + lam2) * random.randint(2, 4)
    cond_exp = (lam1 * tot_n) // (lam1 + lam2)
    questions.append({
        "id": "prob-num-poisson-cond",
        "type": "numeric",
        "title": "Conditional Expectation of Independent Poissons",
        "prompt": (
            f"Let X ~ Poisson({lam1}) and Y ~ Poisson({lam2}) be independent. "
            f"Given X + Y = {tot_n}, what is E[X | X + Y = {tot_n}]?"
        ),
        "answer": str(cond_exp),
        "explanation": f"X | (X+Y={tot_n}) ~ Binomial({tot_n}, {lam1}/({lam1}+{lam2})), so E = {cond_exp}.",
    })

    # 6. Stationary Variance of an AR(1) Process
    phi, sig_sq, ar_var = random.choice([
        (0.6, 16, 25),
        (0.8, 9, 25),
        (0.5, 15, 20),
        (0.6, 32, 50),
    ])
    questions.append({
        "id": "stat-num-ar1-var",
        "type": "numeric",
        "title": "Stationary Variance of an AR(1) Process",
        "prompt": (
            f"Consider the stationary AR(1) process X_t = {phi} X_{{t-1}} + ε_t, where ε_t ~ iid(0, {sig_sq}). "
            f"What is the unconditional variance Var(X_t)?"
        ),
        "answer": str(ar_var),
        "explanation": f"Var(X_t) = σ_ε² / (1 - φ²) = {sig_sq} / (1 - {phi}²) = {ar_var}.",
    })

    # 7. Minimum of Two Independent Exponentials
    rate1, rate2 = random.choice([(2, 3), (1, 3), (3, 7), (1, 4)])
    min_exp = round(1.0 / (rate1 + rate2), 2)
    questions.append({
        "id": "prob-num-exp-min",
        "type": "numeric",
        "title": "Expected Minimum of Independent Exponentials",
        "prompt": (
            f"Let X ~ Exponential(λ₁ = {rate1}) and Y ~ Exponential(λ₂ = {rate2}) be independent. "
            f"What is E[min(X, Y)]? (Give exact decimal)"
        ),
        "answer": str(min_exp),
        "explanation": f"min(X, Y) ~ Exponential({rate1} + {rate2} = {rate1 + rate2}), so E[min] = 1/{rate1 + rate2} = {min_exp}.",
    })

    # 8. Simple Linear Regression R^2 from Correlation
    corr_r = random.choice([-0.9, -0.8, -0.7, 0.6, 0.8])
    r_sq = round(corr_r * corr_r, 2)
    questions.append({
        "id": "stat-num-ols-r2",
        "type": "numeric",
        "title": "OLS Coefficient of Determination (R²)",
        "prompt": (
            f"In a simple Ordinary Least Squares regression of Y on X (with intercept), the sample correlation "
            f"between X and Y is r = {corr_r}. What is the R² of the regression? (Give exact decimal)"
        ),
        "answer": str(r_sq),
        "explanation": f"In simple linear regression with intercept, R² = r² = ({corr_r})² = {r_sq}.",
    })

    # --- 14 Unique MCQ Questions (Dynamic + Curated) ---

    # 9. Bayes' Theorem Regime Alert (Dynamic MCQ)
    base_num = random.choice([1, 2, 5])
    sens = random.choice([80, 90, 95])
    fpr = random.choice([5, 10])
    num_b = base_num * sens
    den_b = num_b + (100 - base_num) * fpr
    frac_b = Fraction(num_b, den_b)
    ans_b = f"{frac_b.numerator}/{frac_b.denominator}"
    opts_b, let_b = make_mcq_options(
        ans_b,
        [f"{frac_b.numerator}/{frac_b.denominator + 5}", f"{sens}/100", f"{max(1, frac_b.numerator - 1)}/{frac_b.denominator}"],
    )
    questions.append({
        "id": "prob-mcq-bayes-regime",
        "type": "mcq",
        "title": "Bayesian Signal Updating",
        "prompt": (
            f"A market regime occurs on {base_num}% of trading days. An indicator triggers an alert with "
            f"{sens}% probability when the regime is active, and with {fpr}% probability when inactive. "
            f"Given that the alert triggered today, what is the probability that the regime is active?"
        ),
        "options": opts_b,
        "answer": let_b,
        "explanation": f"P(Active | Alert) = ({base_num}×{sens}) / ({base_num}×{sens} + {100-base_num}×{fpr}) = {ans_b}.",
    })

    # 10. Asymmetric Random Walk Barrier Hitting Probability (Dynamic MCQ)
    up_a = random.randint(2, 6)
    dn_b = random.randint(2, 6)
    tot_ab = up_a + dn_b
    g_ab = math.gcd(dn_b, tot_ab)
    ans_rw = f"{dn_b // g_ab}/{tot_ab // g_ab}"
    opts_rw, let_rw = make_mcq_options(
        ans_rw,
        [f"{up_a // math.gcd(up_a, tot_ab)}/{tot_ab // math.gcd(up_a, tot_ab)}", "1/2", f"{dn_b}/{tot_ab + 1}"],
    )
    questions.append({
        "id": "prob-mcq-rw-barrier",
        "type": "mcq",
        "title": "Symmetric Random Walk Hitting Probability",
        "prompt": (
            f"A symmetric simple random walk starts at X₀ = 0 and steps +1 or -1 with probability 1/2. "
            f"What is the probability that it reaches +{up_a} before reaching -{dn_b}?"
        ),
        "options": opts_rw,
        "answer": let_rw,
        "explanation": f"By the optional stopping theorem on martingale X_t, p = {dn_b} / ({up_a} + {dn_b}) = {ans_rw}.",
    })

    # 11. Expected Stopping Time of Random Walk on [-a, b] (Dynamic MCQ)
    bar_a = random.randint(2, 6)
    bar_b = random.randint(2, 6)
    exp_steps = bar_a * bar_b
    opts_st, let_st = make_mcq_options(
        str(exp_steps),
        [str(bar_a + bar_b), str((bar_a + bar_b) ** 2), str(2 * exp_steps)],
    )
    questions.append({
        "id": "prob-mcq-rw-stopping-time",
        "type": "mcq",
        "title": "Expected Exit Time of Symmetric Random Walk",
        "prompt": (
            f"A symmetric simple random walk starts at X₀ = 0 and steps ±1 with equal probability 1/2. "
            f"Let τ be the first time the walk hits either -{bar_a} or +{bar_b}. What is E[τ]?"
        ),
        "options": opts_st,
        "answer": let_st,
        "explanation": f"Using the martingale X_t² - t, E[τ] = a × b = {bar_a} × {bar_b} = {exp_steps}.",
    })

    # 12. Sharpe Ratio Annualization (Dynamic MCQ)
    daily_sr = random.choice(["0.10", "0.15", "0.20"])
    ann_sr = str(round(float(daily_sr) * 16, 2))
    opts_sr, let_sr = make_mcq_options(
        ann_sr,
        [str(round(float(daily_sr) * 256, 1)), daily_sr, str(round(float(daily_sr) * 4, 2))],
    )
    questions.append({
        "id": "stat-mcq-sharpe-ann",
        "type": "mcq",
        "title": "Annualizing Daily Sharpe Ratio",
        "prompt": (
            f"A strategy has i.i.d. daily excess returns with a daily Sharpe ratio of {daily_sr}. "
            f"Assuming 256 trading days per year, what is the annualized Sharpe ratio?"
        ),
        "options": opts_sr,
        "answer": let_sr,
        "explanation": f"SR_annual = √256 × SR_daily = 16 × {daily_sr} = {ann_sr}.",
    })

    # 13-22. Curated Static MCQs
    static_prob_mcqs = [
        {
            "id": "prob-mcq-hh-vs-ht",
            "type": "mcq",
            "title": "Expected Flips for HH vs. HT",
            "prompt": "A fair coin is flipped repeatedly. Let τ_HH be the number of flips until 'HH' first appears, and τ_HT be the number of flips until 'HT' first appears. What are E[τ_HH] and E[τ_HT]?",
            "options": [
                {"value": "A", "label": "E[τ_HH] = 6 and E[τ_HT] = 4"},
                {"value": "B", "label": "E[τ_HH] = 4 and E[τ_HT] = 4"},
                {"value": "C", "label": "E[τ_HH] = 6 and E[τ_HT] = 6"},
                {"value": "D", "label": "E[τ_HH] = 4 and E[τ_HT] = 6"},
            ],
            "answer": "A",
            "explanation": "Markov chain transition equations yield E[τ_HH] = 6 and E[τ_HT] = 4.",
        },
        {
            "id": "prob-mcq-broken-stick",
            "type": "mcq",
            "title": "Broken Stick Triangle Probability",
            "prompt": "A stick of length 1 is broken at two points chosen independently and uniformly at random along its length. What is the probability that the three pieces can form a triangle?",
            "options": [
                {"value": "A", "label": "1/4"},
                {"value": "B", "label": "1/3"},
                {"value": "C", "label": "1/2"},
                {"value": "D", "label": "1/8"},
            ],
            "answer": "A",
            "explanation": "Each piece must have length < 1/2; the valid region in the unit square has area 2 × (1/8) = 1/4.",
        },
        {
            "id": "prob-mcq-normal-moments",
            "type": "mcq",
            "title": "Moments and Covariance of Standard Normal",
            "prompt": "Let Z ~ N(0, 1) be a standard normal random variable. What are E[Z⁴] and Cov(Z, Z²)?",
            "options": [
                {"value": "A", "label": "E[Z⁴] = 3 and Cov(Z, Z²) = 0"},
                {"value": "B", "label": "E[Z⁴] = 3 and Cov(Z, Z²) = 1"},
                {"value": "C", "label": "E[Z⁴] = 1 and Cov(Z, Z²) = 0"},
                {"value": "D", "label": "E[Z⁴] = 4 and Cov(Z, Z²) = 2"},
            ],
            "answer": "A",
            "explanation": "For Z ~ N(0,1), the 4th moment is 3, and Cov(Z, Z²) = E[Z³] - E[Z]E[Z²] = 0 by odd symmetry.",
        },
        {
            "id": "prob-mcq-derangements",
            "type": "mcq",
            "title": "Asymptotic Probability of a Derangement",
            "prompt": "n letters are placed uniformly at random into n addressed envelopes. As n → ∞, what does the probability that NO letter ends up in its correct envelope converge to?",
            "options": [
                {"value": "A", "label": "1 / e"},
                {"value": "B", "label": "1 - 1 / e"},
                {"value": "C", "label": "0"},
                {"value": "D", "label": "1 / 2"},
            ],
            "answer": "A",
            "explanation": "By inclusion-exclusion, P(no fixed points) = ∑_{k=0}^n (-1)^k / k! → e^{-1} = 1/e.",
        },
        {
            "id": "prob-mcq-noodles",
            "type": "mcq",
            "title": "Expected Loops from Tying Noodle Ends",
            "prompt": "A bowl contains 2 noodles (4 free ends). You pick two ends uniformly at random, tie them together, and then tie the remaining two ends. What is the expected number of closed loops formed?",
            "options": [
                {"value": "A", "label": "4/3"},
                {"value": "B", "label": "3/2"},
                {"value": "C", "label": "1"},
                {"value": "D", "label": "5/3"},
            ],
            "answer": "A",
            "explanation": "For N noodles, E[loops] = ∑_{k=1}^N 1/(2k - 1). For N=2, 1/1 + 1/3 = 4/3.",
        },
        {
            "id": "prob-mcq-psd-corr",
            "type": "mcq",
            "title": "Equicorrelated Matrix Lower Bound",
            "prompt": "Three random variables X₁, X₂, X₃ each have unit variance and equal pairwise correlation Corr(X_i, X_j) = ρ for all i ≠ j. What is the minimum possible value of ρ?",
            "options": [
                {"value": "A", "label": "-1/2"},
                {"value": "B", "label": "-1"},
                {"value": "C", "label": "-1/3"},
                {"value": "D", "label": "0"},
            ],
            "answer": "A",
            "explanation": "Var(X₁ + X₂ + X₃) = 3 + 6ρ ≥ 0 ⇒ ρ ≥ -1/2 (in general, ρ ≥ -1/(n-1)).",
        },
        {
            "id": "stat-mcq-unif-mle",
            "type": "mcq",
            "title": "Maximum Likelihood Estimator of Uniform(0, θ)",
            "prompt": "Let X₁, ..., X_n be i.i.d. Uniform(0, θ). What is the Maximum Likelihood Estimator θ̂_MLE of θ, and is it unbiased?",
            "options": [
                {"value": "A", "label": "θ̂_MLE = max(X₁, ..., X_n), which is biased downward"},
                {"value": "B", "label": "θ̂_MLE = 2 X̄, which is unbiased"},
                {"value": "C", "label": "θ̂_MLE = max(X₁, ..., X_n), which is unbiased"},
                {"value": "D", "label": "θ̂_MLE = ((n+1)/n) max(X₁, ..., X_n), which is unbiased"},
            ],
            "answer": "A",
            "explanation": "The likelihood (1/θ)^n · I(max X_i ≤ θ) is maximized at θ̂ = max X_i, which has expectation (n/(n+1))θ < θ.",
        },
        {
            "id": "stat-mcq-pval-dist",
            "type": "mcq",
            "title": "Distribution of the p-value Under the Null Hypothesis",
            "prompt": "For a continuous test statistic, what is the probability distribution of the two-sided p-value when the null hypothesis H₀ is true?",
            "options": [
                {"value": "A", "label": "Uniform(0, 1)"},
                {"value": "B", "label": "Standard Normal N(0, 1)"},
                {"value": "C", "label": "Chi-squared with 1 degree of freedom"},
                {"value": "D", "label": "Exponential(1)"},
            ],
            "answer": "A",
            "explanation": "By the probability integral transform, F(T) ~ Uniform(0, 1) under H₀.",
        },
        {
            "id": "stat-mcq-clt-rate",
            "type": "mcq",
            "title": "Scaling of Standard Error of the Sample Mean",
            "prompt": "To reduce the standard error of the sample mean X̄ by a factor of 4 (for i.i.d. observations with finite variance σ²), by what factor must the sample size n be multiplied?",
            "options": [
                {"value": "A", "label": "16"},
                {"value": "B", "label": "4"},
                {"value": "C", "label": "2"},
                {"value": "D", "label": "8"},
            ],
            "answer": "A",
            "explanation": "SE(X̄) = σ / √n, so dividing SE by 4 requires multiplying n by 4² = 16.",
        },
        {
            "id": "prob-mcq-ants-triangle",
            "type": "mcq",
            "title": "Non-Colliding Ants on a Triangle",
            "prompt": "Three ants sit at the three corners of an equilateral triangle. Each ant independently picks one of the two adjacent edges at random and walks along it. What is the probability that no two ants collide?",
            "options": [
                {"value": "A", "label": "1/4"},
                {"value": "B", "label": "1/8"},
                {"value": "C", "label": "1/2"},
                {"value": "D", "label": "3/8"},
            ],
            "answer": "A",
            "explanation": "There are 2³ = 8 outcomes; only 2 avoid collision (all clockwise or all counter-clockwise), so 2/8 = 1/4.",
        },
    ]

    questions.extend(static_prob_mcqs)
    return questions


# ============================================================================
# 3. CODING & ALGORITHMS (15 MCQ, 7 Numeric = 22 Unique Questions)
# ============================================================================


def generate_coding_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []

    # --- 7 Unique Dynamic NUMERIC Questions ---

    # 1. Kadane's Maximum Subarray Sum
    arr1 = [
        random.randint(-5, -1),
        random.randint(3, 7),
        random.randint(-2, -1),
        random.randint(4, 8),
        random.randint(-6, -2),
        random.randint(1, 4),
    ]
    cur_s = max_s = arr1[0]
    for x in arr1[1:]:
        cur_s = max(x, cur_s + x)
        max_s = max(max_s, cur_s)
    questions.append({
        "id": "code-num-kadane",
        "type": "numeric",
        "title": "Maximum Contiguous Subarray Sum",
        "prompt": f"Given the integer array nums = {arr1}, what is the maximum sum of any non-empty contiguous subarray?",
        "answer": str(max_s),
        "explanation": f"Running Kadane's algorithm on {arr1} gives maximum subarray sum {max_s}.",
    })

    # 2. Single-Trade Maximum Stock Profit
    prices1 = [random.randint(5, 25) for _ in range(6)]
    min_p = prices1[0]
    max_prof1 = 0
    for p in prices1[1:]:
        max_prof1 = max(max_prof1, p - min_p)
        min_p = min(min_p, p)
    questions.append({
        "id": "code-num-stock-single",
        "type": "numeric",
        "title": "Maximum Single-Trade Profit",
        "prompt": (
            f"Given daily prices = {prices1}, what is the maximum profit achievable from at most one buy "
            f"followed by one sell? (Answer 0 if no profit is possible.)"
        ),
        "answer": str(max_prof1),
        "explanation": f"Tracking the running minimum and max difference over {prices1} yields {max_prof1}.",
    })

    # 3. Multi-Trade Maximum Stock Profit
    prices2 = [random.randint(10, 30) for _ in range(6)]
    tot_prof2 = sum(max(0, prices2[j] - prices2[j - 1]) for j in range(1, len(prices2)))
    questions.append({
        "id": "code-num-stock-multi",
        "type": "numeric",
        "title": "Maximum Multi-Trade Profit (Zero Transaction Cost)",
        "prompt": (
            f"Given daily prices = {prices2}, you may buy and sell as many times as you like "
            f"(holding at most 1 share at a time). What is the maximum total profit?"
        ),
        "answer": str(tot_prof2),
        "explanation": f"Sum all positive daily increments max(0, p[t] - p[t-1]) = {tot_prof2}.",
    })

    # 4. Brian Kernighan's Bit-Clearing Loop
    n_bits = random.choice([23, 27, 29, 39, 43, 51, 58])
    pop_cnt = bin(n_bits).count("1")
    questions.append({
        "id": "code-num-kernighan-bits",
        "type": "numeric",
        "title": "Brian Kernighan's Bit-Clearing Loop",
        "prompt": (
            f"Consider the loop:\n"
            f"  count = 0\n"
            f"  n = {n_bits}\n"
            f"  while n > 0:\n"
            f"      n = n & (n - 1)\n"
            f"      count += 1\n"
            f"What is the final value of `count`?"
        ),
        "answer": str(pop_cnt),
        "explanation": f"`n & (n - 1)` clears the lowest set bit each iteration; {n_bits} ({bin(n_bits)}) has {pop_cnt} set bits.",
    })

    # 5. Python Generator Comprehension Sum
    limit_k = random.choice([6, 8, 10])
    odd_sq_sum = sum(x * x for x in range(1, limit_k) if x % 2 == 1)
    questions.append({
        "id": "code-num-py-gen",
        "type": "numeric",
        "title": "Python Generator & Filter Evaluation",
        "prompt": f"What is the output of `sum(x * x for x in range(1, {limit_k}) if x % 2 == 1)` in Python?",
        "answer": str(odd_sq_sum),
        "explanation": f"Sum of squares of odd integers in range(1, {limit_k}) equals {odd_sq_sum}.",
    })

    # 6. Dynamic Programming: Climbing Stairs
    stairs_n = random.choice([5, 6, 7])
    fib = [1, 1]
    for _ in range(2, stairs_n + 1):
        fib.append(fib[-1] + fib[-2])
    questions.append({
        "id": "code-num-climb-stairs",
        "type": "numeric",
        "title": "Dynamic Programming: Climbing Stairs",
        "prompt": (
            f"You are climbing a staircase with {stairs_n} steps. Each step you can climb either 1 or 2 stairs. "
            f"How many distinct ways can you reach the top?"
        ),
        "answer": str(fib[stairs_n]),
        "explanation": f"Ways(n) follows the Fibonacci sequence: Ways({stairs_n}) = {fib[stairs_n]}.",
    })

    # 7. Edges in an Undirected Forest
    verts = random.randint(20, 35)
    comps = random.randint(3, 7)
    edges = verts - comps
    questions.append({
        "id": "code-num-forest-edges",
        "type": "numeric",
        "title": "Number of Edges in a Forest",
        "prompt": f"An undirected acyclic graph (forest) has {verts} vertices and {comps} connected components. How many edges does it have?",
        "answer": str(edges),
        "explanation": f"A forest with V vertices and C connected components has V - C = {verts} - {comps} = {edges} edges.",
    })

    # --- 15 Unique MCQ Questions (Dynamic + Curated) ---

    # 8. Master Theorem Recurrence (Dynamic MCQ)
    a_m, b_m, fn_m, ans_m, dist_m = random.choice([
        (4, 2, "n", "O(n²)", ["O(n log n)", "O(n² log n)", "O(n)"]),
        (2, 2, "n", "O(n log n)", ["O(n)", "O(n²)", "O(log n)"]),
        (8, 2, "n²", "O(n³)", ["O(n² log n)", "O(n²)", "O(n³ log n)"]),
    ])
    opts_m, let_m = make_mcq_options(ans_m, dist_m)
    questions.append({
        "id": "code-mcq-master-thm",
        "type": "mcq",
        "title": "Divide-and-Conquer Recurrence Complexity",
        "prompt": f"What is the tight asymptotic time complexity of T(n) = {a_m} T(n / {b_m}) + Θ({fn_m})?",
        "options": opts_m,
        "answer": let_m,
        "explanation": f"By the Master Theorem with a={a_m}, b={b_m}, f(n)=Θ({fn_m}), T(n) = {ans_m}.",
    })

    # 9. Binary Search Worst-Case Comparisons (Dynamic MCQ)
    arr_sz = random.choice([500, 1000, 2000, 4000])
    max_cmp = int(math.floor(math.log2(arr_sz))) + 1
    opts_bs, let_bs = make_mcq_options(
        str(max_cmp),
        [str(max_cmp - 2), str(max_cmp + 3), str(arr_sz // 2)],
    )
    questions.append({
        "id": "code-mcq-bsearch-cmp",
        "type": "mcq",
        "title": "Binary Search Worst-Case Comparisons",
        "prompt": f"What is the maximum number of element comparisons needed by binary search on a sorted array of {arr_sz} elements?",
        "options": opts_bs,
        "answer": let_bs,
        "explanation": f"⌊log₂({arr_sz})⌋ + 1 = {max_cmp}.",
    })

    # 10-22. Curated Static MCQs
    static_code_mcqs = [
        {
            "id": "code-mcq-heapify",
            "type": "mcq",
            "title": "Bottom-Up Binary Heap Construction Complexity",
            "prompt": "What is the worst-case time complexity of building a binary min-heap from an unsorted array of n elements using Floyd's bottom-up `heapify` algorithm?",
            "options": [
                {"value": "A", "label": "O(n)"},
                {"value": "B", "label": "O(n log n)"},
                {"value": "C", "label": "O(log n)"},
                {"value": "D", "label": "O(n²)"},
            ],
            "answer": "A",
            "explanation": "Sifting down from n/2 to 1 takes ∑ (n / 2^{h+1}) O(h) = O(n) linear time.",
        },
        {
            "id": "code-mcq-fenwick-lsb",
            "type": "mcq",
            "title": "Isolating the Lowest Set Bit (Fenwick Tree)",
            "prompt": "In two's complement arithmetic, which bitwise expression isolates the lowest set bit (least significant 1-bit) of a non-zero integer `x`?",
            "options": [
                {"value": "A", "label": "x & -x"},
                {"value": "B", "label": "x & (x - 1)"},
                {"value": "C", "label": "x ^ (x - 1)"},
                {"value": "D", "label": "x | -x"},
            ],
            "answer": "A",
            "explanation": "In two's complement, `-x == ~x + 1`, so `x & -x` leaves only the lowest set bit.",
        },
        {
            "id": "code-mcq-quicksort-worst",
            "type": "mcq",
            "title": "Quicksort Worst-Case Time Complexity",
            "prompt": "For an in-place Quicksort using deterministic last-element pivoting on an already sorted array of length n, what is the time complexity?",
            "options": [
                {"value": "A", "label": "O(n²)"},
                {"value": "B", "label": "O(n log n)"},
                {"value": "C", "label": "O(n)"},
                {"value": "D", "label": "O(n log² n)"},
            ],
            "answer": "A",
            "explanation": "Last-element pivot on a sorted array produces partitions of size n-1 and 0 at each step, taking O(n²) time.",
        },
        {
            "id": "code-mcq-lru-cache",
            "type": "mcq",
            "title": "Data Structures for O(1) LRU Cache",
            "prompt": "Which combination of data structures is standardly used to implement an LRU (Least Recently Used) cache with O(1) time for both `get` and `put`?",
            "options": [
                {"value": "A", "label": "Hash map + doubly linked list"},
                {"value": "B", "label": "Hash map + binary min-heap"},
                {"value": "C", "label": "Balanced BST + FIFO queue"},
                {"value": "D", "label": "Singly linked list + dynamic array"},
            ],
            "answer": "A",
            "explanation": "A hash map gives O(1) node lookup, and a doubly linked list gives O(1) node removal and insertion at the head.",
        },
        {
            "id": "code-mcq-kahan-sum",
            "type": "mcq",
            "title": "Floating-Point Summation Accuracy",
            "prompt": "Which O(n) algorithm minimizes floating-point rounding error when summing a large stream of IEEE 754 numbers by tracking a running compensation term?",
            "options": [
                {"value": "A", "label": "Kahan compensated summation"},
                {"value": "B", "label": "Naive left-to-right accumulation"},
                {"value": "C", "label": "Horner's method"},
                {"value": "D", "label": "Strassen's algorithm"},
            ],
            "answer": "A",
            "explanation": "Kahan summation keeps track of low-order bits lost during addition in a separate compensation variable.",
        },
        {
            "id": "code-mcq-bellman-ford",
            "type": "mcq",
            "title": "Shortest Paths with Negative Edge Weights",
            "prompt": "Which single-source shortest-path algorithm works on directed graphs with negative edge weights and can detect reachable negative-weight cycles?",
            "options": [
                {"value": "A", "label": "Bellman-Ford algorithm"},
                {"value": "B", "label": "Dijkstra's algorithm"},
                {"value": "C", "label": "Kruskal's algorithm"},
                {"value": "D", "label": "Breadth-First Search (BFS)"},
            ],
            "answer": "A",
            "explanation": "Bellman-Ford relaxes all edges V-1 times in O(VE) time and checks a V-th pass for negative cycles.",
        },
        {
            "id": "code-mcq-union-find",
            "type": "mcq",
            "title": "Disjoint Set Union (Union-Find) Complexity",
            "prompt": "With both path compression and union by rank/size enabled, what is the amortized time complexity per operation of m Disjoint Set Union (DSU) operations on n elements?",
            "options": [
                {"value": "A", "label": "O(α(n)), where α is the inverse Ackermann function"},
                {"value": "B", "label": "O(log n)"},
                {"value": "C", "label": "O(log* n) exact lower bound, Ω(log n) upper bound"},
                {"value": "D", "label": "O(√n)"},
            ],
            "answer": "A",
            "explanation": "Tarjan proved that path compression + union by rank achieves O(α(n)) amortized time per operation.",
        },
        {
            "id": "code-mcq-py-mutable-default",
            "type": "mcq",
            "title": "Python Mutable Default Argument Behavior",
            "prompt": "Consider `def f(x, acc=[]): acc.append(x); return acc`. What is returned by calling `f(1)` followed by `f(2)`?",
            "options": [
                {"value": "A", "label": "First call returns [1]; second call returns [1, 2]"},
                {"value": "B", "label": "First call returns [1]; second call returns [2]"},
                {"value": "C", "label": "Raises a TypeError at function definition time"},
                {"value": "D", "label": "Both calls return [2]"},
            ],
            "answer": "A",
            "explanation": "Default arguments in Python are evaluated once when `def` is executed, so `acc` persists across calls.",
        },
        {
            "id": "code-mcq-cpp-virtual-dtor",
            "type": "mcq",
            "title": "C++ Polymorphic Base Class Destructor",
            "prompt": "In C++, what happens if you `delete` a derived class object through a pointer to a base class that has a non-virtual destructor?",
            "options": [
                {"value": "A", "label": "Undefined behavior (typically the derived destructor is never called, causing resource leaks)"},
                {"value": "B", "label": "A compile-time syntax error"},
                {"value": "C", "label": "The runtime automatically dispatches the derived destructor via RTTI"},
                {"value": "D", "label": "A `std::bad_cast` exception is thrown"},
            ],
            "answer": "A",
            "explanation": "Deleting a derived object via a base pointer without a `virtual` base destructor is undefined behavior in C++.",
        },
        {
            "id": "code-mcq-quickselect",
            "type": "mcq",
            "title": "Finding the Median in Linear Expected Time",
            "prompt": "What are the expected and worst-case time complexities of randomized Quickselect for finding the k-th smallest element in an unsorted array of n elements?",
            "options": [
                {"value": "A", "label": "O(n) expected time, O(n²) worst-case time"},
                {"value": "B", "label": "O(n log n) expected time, O(n²) worst-case time"},
                {"value": "C", "label": "O(log n) expected time, O(n) worst-case time"},
                {"value": "D", "label": "O(n) expected time, O(n log n) worst-case time"},
            ],
            "answer": "A",
            "explanation": "Quickselect recurses on only one side of the partition, giving geometric work E[T(n)] = O(n), but bad pivots yield O(n²).",
        },
        {
            "id": "code-mcq-monotonic-stack",
            "type": "mcq",
            "title": "Next Greater Element Time Complexity",
            "prompt": "Using a monotonic stack to find the next greater element to the right for every element in an array of length n runs in what worst-case time complexity?",
            "options": [
                {"value": "A", "label": "O(n)"},
                {"value": "B", "label": "O(n log n)"},
                {"value": "C", "label": "O(n²)"},
                {"value": "D", "label": "O(n √n)"},
            ],
            "answer": "A",
            "explanation": "Each element is pushed onto and popped from the stack at most once, totaling at most 2n stack operations = O(n).",
        },
        {
            "id": "code-mcq-hash-worst",
            "type": "mcq",
            "title": "Hash Table Lookup Complexity Under Collisions",
            "prompt": "For a standard hash table of size n using separate chaining with linked lists, what are the average-case (uniform hashing) and worst-case lookup time complexities?",
            "options": [
                {"value": "A", "label": "O(1) average case, O(n) worst case"},
                {"value": "B", "label": "O(1) average case, O(log n) worst case"},
                {"value": "C", "label": "O(log n) average case, O(n) worst case"},
                {"value": "D", "label": "O(1) in both average and worst cases"},
            ],
            "answer": "A",
            "explanation": "If all n keys collide into the same bucket, traversing the linked list takes O(n) time.",
        },
        {
            "id": "code-mcq-dag-toposort",
            "type": "mcq",
            "title": "Existence of a Topological Ordering",
            "prompt": "A directed graph G = (V, E) admits a valid topological ordering of its vertices if and only if:",
            "options": [
                {"value": "A", "label": "G is a Directed Acyclic Graph (contains no directed cycles)"},
                {"value": "B", "label": "G is strongly connected"},
                {"value": "C", "label": "G is bipartite"},
                {"value": "D", "label": "Every vertex in G has equal in-degree and out-degree"},
            ],
            "answer": "A",
            "explanation": "A topological sort exists iff the directed graph has no directed cycles (is a DAG).",
        },
    ]

    questions.extend(static_code_mcqs)
    return questions


# ============================================================================
# 4. MACHINE LEARNING & DATA SCIENCE (15 MCQ, 7 Numeric = 22 Unique Questions)
# ============================================================================


def generate_machine_learning() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []

    # --- 7 Unique Dynamic NUMERIC Questions ---

    # 1. F1 Score from Confusion Matrix
    tp, fp, fn = random.choice([(30, 10, 10), (80, 10, 30), (35, 15, 15), (45, 5, 25)])
    f1 = round((2 * tp) / (2 * tp + fp + fn), 2)
    questions.append({
        "id": "ml-num-f1-score",
        "type": "numeric",
        "title": "F1 Score from Confusion Matrix",
        "prompt": (
            f"A binary classifier yields True Positives (TP) = {tp}, False Positives (FP) = {fp}, "
            f"and False Negatives (FN) = {fn}. What is its F1 score? (Give exact decimal)"
        ),
        "answer": str(f1),
        "explanation": f"F1 = 2·TP / (2·TP + FP + FN) = {2*tp} / ({2*tp + fp + fn}) = {f1}.",
    })

    # 2. Gradient Descent Step with L2 Regularization
    w0 = random.randint(2, 5)
    lr = random.choice([0.1, 0.25, 0.5])
    lam = random.choice([2, 4])
    grad = 2 * (w0 - 1) + lam * w0
    w1 = round(w0 - lr * grad, 3)
    ans_w1 = str(int(w1)) if w1.is_integer() else str(w1)
    questions.append({
        "id": "ml-num-gd-step",
        "type": "numeric",
        "title": "Gradient Descent Update with L2 Penalty",
        "prompt": (
            f"Consider minimizing L(w) = (w - 1)² + ({lam}/2)w². Starting at w₀ = {w0} with learning rate "
            f"η = {lr}, what is w₁ after one gradient descent step?"
        ),
        "answer": ans_w1,
        "explanation": f"L'(w₀) = 2({w0}-1) + {lam}({w0}) = {grad}. Thus w₁ = {w0} - {lr}×{grad} = {ans_w1}.",
    })

    # 3. PCA Proportion of Variance Explained
    tot_v = random.choice([20, 25, 50])
    ev1 = int(tot_v * random.choice([0.5, 0.6, 0.7, 0.8]))
    rem_v = tot_v - ev1
    ev2 = rem_v - 1
    ev3 = 1
    pca_ratio = round(ev1 / tot_v, 2)
    questions.append({
        "id": "ml-num-pca-var",
        "type": "numeric",
        "title": "PCA Explained Variance Ratio",
        "prompt": (
            f"The sample covariance matrix of a 3D dataset has eigenvalues λ₁ = {ev1}, λ₂ = {ev2}, and λ₃ = {ev3}. "
            f"What proportion of total variance is explained by the first principal component? (Give decimal)"
        ),
        "answer": str(pca_ratio),
        "explanation": f"λ₁ / (λ₁ + λ₂ + λ₃) = {ev1} / {tot_v} = {pca_ratio}.",
    })

    # 4. 1D Ridge Regression Estimate
    denom_r = random.choice([10, 20, 25])
    lam_r = random.randint(2, 8)
    s_xx = denom_r - lam_r
    s_xy = denom_r * random.randint(2, 6)
    w_ridge = s_xy // denom_r
    questions.append({
        "id": "ml-num-ridge-1d",
        "type": "numeric",
        "title": "1D Ridge Regression Closed-Form Weight",
        "prompt": (
            f"In 1D Ridge Regression without intercept, minimizing ||y - Xw||₂² + λw², suppose XᵀX = {s_xx}, "
            f"Xᵀy = {s_xy}, and λ = {lam_r}. What is the optimal ridge weight ŵ?"
        ),
        "answer": str(w_ridge),
        "explanation": f"ŵ = Xᵀy / (XᵀX + λ) = {s_xy} / ({s_xx} + {lam_r}) = {w_ridge}.",
    })

    # 5. Gini Impurity of a Decision Tree Node
    p_pos = random.choice([0.2, 0.25, 0.3, 0.4, 0.5])
    n_pos = int(100 * p_pos)
    n_neg = 100 - n_pos
    gini = round(2 * p_pos * (1 - p_pos), 4)
    questions.append({
        "id": "ml-num-gini-node",
        "type": "numeric",
        "title": "Decision Tree Node Gini Impurity",
        "prompt": (
            f"A binary classification tree node has {n_pos} positive samples and {n_neg} negative samples. "
            f"What is the Gini impurity of this node? (Give exact decimal)"
        ),
        "answer": str(gini),
        "explanation": f"Gini = 2 p (1 - p) = 2 × {p_pos} × {round(1 - p_pos, 2)} = {gini}.",
    })

    # 6. Hard-Margin SVM Geometric Margin Width
    w_x, w_y, w_norm = random.choice([(3, 4, 5), (6, 8, 10), (0, 4, 4), (0, 2, 2)])
    margin_w = round(2.0 / w_norm, 2)
    questions.append({
        "id": "ml-num-svm-margin",
        "type": "numeric",
        "title": "Hard-Margin SVM Geometric Margin Width",
        "prompt": (
            f"A hard-margin linear SVM has weight vector w = ({w_x}, {w_y})ᵀ and bias b = -1. "
            f"What is the total geometric margin width between the support hyperplanes wᵀx + b = ±1? (Give decimal)"
        ),
        "answer": str(margin_w),
        "explanation": f"Total margin width is 2 / ||w||₂ = 2 / √({w_x}² + {w_y}²) = 2 / {w_norm} = {margin_w}.",
    })

    # 7. Lasso Soft-Thresholding Operator
    z_ols = random.randint(5, 12)
    thresh = random.randint(1, z_ols - 1)
    w_lasso = z_ols - thresh
    questions.append({
        "id": "ml-num-soft-threshold",
        "type": "numeric",
        "title": "1D Lasso Soft-Thresholding Solution",
        "prompt": (
            f"With orthonormal feature ||x||₂² = 1, minimizing 0.5(w - {z_ols})² + {thresh}|w| yields "
            f"what optimal L1-regularized weight ŵ?"
        ),
        "answer": str(w_lasso),
        "explanation": f"By soft-thresholding S(z, λ) = sign(z) max(|z| - λ, 0) = {z_ols} - {thresh} = {w_lasso}.",
    })

    # --- 15 Unique MCQ Questions (Dynamic + Curated) ---

    # 8. Shannon Entropy of Uniform Discrete RV (Dynamic MCQ)
    k_bits = random.choice([3, 4, 5, 6])
    n_outcomes = 2**k_bits
    opts_ent, let_ent = make_mcq_options(
        f"{k_bits} bits",
        [f"{k_bits - 1} bits", f"{n_outcomes} bits", f"1/{n_outcomes} bits"],
    )
    questions.append({
        "id": "ml-mcq-shannon-entropy",
        "type": "mcq",
        "title": "Shannon Entropy of Uniform Discrete Distribution",
        "prompt": (
            f"Let X be a discrete random variable taking {n_outcomes} outcomes with equal probability "
            f"1/{n_outcomes} each. What is the Shannon entropy H(X) in bits (base-2 logarithm)?"
        ),
        "options": opts_ent,
        "answer": let_ent,
        "explanation": f"H(X) = log₂({n_outcomes}) = {k_bits} bits.",
    })

    # 9. Bias-Variance MSE Decomposition (Dynamic MCQ)
    bias_val = random.randint(2, 5)
    var_val = random.randint(3, 8)
    noise_std = random.randint(2, 4)
    tot_mse = bias_val**2 + var_val + noise_std**2
    opts_bv, let_bv = make_mcq_options(
        str(tot_mse),
        [
            str(bias_val + var_val + noise_std),
            str(bias_val**2 + var_val),
            str(bias_val**2 + var_val**2 + noise_std**2),
        ],
    )
    questions.append({
        "id": "ml-mcq-bias-var-mse",
        "type": "mcq",
        "title": "Expected Test MSE from Bias-Variance Decomposition",
        "prompt": (
            f"Suppose y = f(x) + ε where ε has mean 0 and standard deviation σ = {noise_std}. "
            f"At a test point x₀, an estimator f̂(x₀) has Bias = {bias_val} and Variance = {var_val}. "
            f"What is the expected squared prediction error E[(y - f̂(x₀))²]?"
        ),
        "options": opts_bv,
        "answer": let_bv,
        "explanation": f"MSE = Bias² + Variance + σ² = {bias_val}² + {var_val} + {noise_std}² = {tot_mse}.",
    })

    # 10-22. Curated Static MCQs
    static_ml_mcqs = [
        {
            "id": "ml-mcq-lasso-sparsity",
            "type": "mcq",
            "title": "Sparsity in L1 (Lasso) vs L2 (Ridge) Regularization",
            "prompt": "Why does L1 (Lasso) regularization produce exact zero weights (sparse solutions) whereas L2 (Ridge) regularization generally does not?",
            "options": [
                {"value": "A", "label": "The L1 constraint ball has sharp corners on the coordinate axes where loss contours often first intersect"},
                {"value": "B", "label": "The L1 penalty is twice continuously differentiable at zero"},
                {"value": "C", "label": "L1 regularization shifts all eigenvalues of XᵀX by a constant λ"},
                {"value": "D", "label": "L2 regularization is non-convex when features are correlated"},
            ],
            "answer": "A",
            "explanation": "The L1 ball is a cross-polytope with vertices on the axes, creating a non-zero subgradient threshold [-λ, λ] at 0.",
        },
        {
            "id": "ml-mcq-bagging-effect",
            "type": "mcq",
            "title": "Statistical Effect of Bagging (Bootstrap Aggregating)",
            "prompt": "In Random Forests and Bagging, what is the primary statistical purpose of averaging predictions across B bootstrap-trained deep trees?",
            "options": [
                {"value": "A", "label": "Reduces variance while leaving bias approximately unchanged"},
                {"value": "B", "label": "Reduces bias while increasing variance"},
                {"value": "C", "label": "Eliminates irreducible Bayes error"},
                {"value": "D", "label": "Forces all trees to have zero pairwise correlation"},
            ],
            "answer": "A",
            "explanation": "Averaging identically distributed estimators reduces variance without changing expected value (bias).",
        },
        {
            "id": "ml-mcq-sigmoid-deriv",
            "type": "mcq",
            "title": "Maximum Derivative of the Logistic Sigmoid",
            "prompt": "Let σ(z) = 1 / (1 + e^{-z}) be the logistic sigmoid activation function. What is the maximum value of σ'(z) over z ∈ ℝ?",
            "options": [
                {"value": "A", "label": "0.25 (achieved at z = 0)"},
                {"value": "B", "label": "0.50 (achieved at z = 0)"},
                {"value": "C", "label": "1.00 (achieved as z → ∞)"},
                {"value": "D", "label": "1 / e (achieved at z = 1)"},
            ],
            "answer": "A",
            "explanation": "σ'(z) = σ(z)(1 - σ(z)) ≤ 0.5 × 0.5 = 0.25 at z = 0.",
        },
        {
            "id": "ml-mcq-timeseries-cv",
            "type": "mcq",
            "title": "Cross-Validation for Financial Time Series",
            "prompt": "Why is standard random K-fold cross-validation invalid when evaluating alpha signals on financial time series?",
            "options": [
                {"value": "A", "label": "It introduces look-ahead bias (data leakage) by training on future timestamps to predict past timestamps"},
                {"value": "B", "label": "It requires balanced binary classes"},
                {"value": "C", "label": "It cannot be used with regularized linear models"},
                {"value": "D", "label": "It underestimates in-sample R²"},
            ],
            "answer": "A",
            "explanation": "Random splits leak future regime and serial correlation information into past validation folds; walk-forward CV is required.",
        },
        {
            "id": "ml-mcq-mae-median",
            "type": "mcq",
            "title": "Bayes Optimal Predictor Under L1 Loss (MAE)",
            "prompt": "While the conditional mean E[Y | X] minimizes expected squared error E[(Y - f(X))²], what statistic of P(Y | X) minimizes expected absolute error E[|Y - f(X)|]?",
            "options": [
                {"value": "A", "label": "The conditional median"},
                {"value": "B", "label": "The conditional mode"},
                {"value": "C", "label": "The conditional geometric mean"},
                {"value": "D", "label": "The conditional mid-range"},
            ],
            "answer": "A",
            "explanation": "Setting the subgradient of E[|Y - c| | X] to 0 gives P(Y ≤ c | X) = P(Y ≥ c | X), the conditional median.",
        },
        {
            "id": "ml-mcq-roc-auc",
            "type": "mcq",
            "title": "Probabilistic Interpretation of ROC-AUC",
            "prompt": "What does the Area Under the ROC Curve (ROC-AUC) represent probabilistically for a binary scorer s(x)?",
            "options": [
                {"value": "A", "label": "The probability that a randomly drawn positive sample is scored higher than a randomly drawn negative sample"},
                {"value": "B", "label": "The harmonic mean of precision and recall at threshold 0.5"},
                {"value": "C", "label": "The proportion of positive predictions that are true positives"},
                {"value": "D", "label": "One minus the Brier score"},
            ],
            "answer": "A",
            "explanation": "ROC-AUC = P(s(X⁺) > s(X⁻)), equivalent to the Mann-Whitney U statistic.",
        },
        {
            "id": "ml-mcq-multicollinearity",
            "type": "mcq",
            "title": "Multicollinearity Impact on OLS Estimators",
            "prompt": "When predictors in an Ordinary Least Squares (OLS) regression are strongly (but not perfectly) collinear, how are the OLS coefficient estimates β̂ affected?",
            "options": [
                {"value": "A", "label": "They remain unbiased, but their variances (standard errors) become very large"},
                {"value": "B", "label": "They become systematically biased toward zero"},
                {"value": "C", "label": "The Gauss-Markov theorem no longer holds and OLS is biased"},
                {"value": "D", "label": "The regression residuals have non-zero sample mean"},
            ],
            "answer": "A",
            "explanation": "Near-collinearity makes (XᵀX)⁻¹ have huge eigenvalues, inflating Cov(β̂) = σ²(XᵀX)⁻¹ without biasing E[β̂].",
        },
        {
            "id": "ml-mcq-kl-properties",
            "type": "mcq",
            "title": "Properties of Kullback-Leibler (KL) Divergence",
            "prompt": "Which statement about the Kullback-Leibler divergence D_KL(P || Q) between two probability distributions P and Q is true?",
            "options": [
                {"value": "A", "label": "D_KL(P || Q) ≥ 0 always, and it is asymmetric so D_KL(P || Q) ≠ D_KL(Q || P) in general"},
                {"value": "B", "label": "D_KL(P || Q) is a symmetric metric satisfying the triangle inequality"},
                {"value": "C", "label": "D_KL(P || Q) can be negative when P has higher entropy than Q"},
                {"value": "D", "label": "D_KL(P || Q) is bounded above by 1"},
            ],
            "answer": "A",
            "explanation": "By Jensen's inequality D_KL(P || Q) ≥ 0 (with 0 iff P = Q), and it is not symmetric.",
        },
        {
            "id": "ml-mcq-boosting-vs-bagging",
            "type": "mcq",
            "title": "Gradient Boosting with Shallow Trees",
            "prompt": "Unlike Random Forests (which average deep, independent trees), Gradient Boosted Decision Trees (GBDT) sequentially fit shallow trees to the negative gradients of the loss primarily to:",
            "options": [
                {"value": "A", "label": "Reduce bias by additively correcting residual errors of preceding learners"},
                {"value": "B", "label": "Guarantee zero training variance without a learning rate"},
                {"value": "C", "label": "Make tree training embarrassingly parallel across boosting rounds"},
                {"value": "D", "label": "Ensure the model is strictly linear in the input features"},
            ],
            "answer": "A",
            "explanation": "Boosting combines high-bias, low-variance weak learners sequentially to reduce bias.",
        },
        {
            "id": "ml-mcq-knn-complexity",
            "type": "mcq",
            "title": "Bias-Variance Tradeoff in k-Nearest Neighbors (k-NN)",
            "prompt": "In k-Nearest Neighbors (k-NN) regression, how do model bias and variance change as the number of neighbors k increases from 1 toward N?",
            "options": [
                {"value": "A", "label": "Bias increases and variance decreases"},
                {"value": "B", "label": "Bias decreases and variance increases"},
                {"value": "C", "label": "Both bias and variance decrease"},
                {"value": "D", "label": "Both bias and variance increase"},
            ],
            "answer": "A",
            "explanation": "Averaging over more neighbors (larger k) smooths predictions, lowering variance(σ²/k) while increasing smoothing bias.",
        },
        {
            "id": "ml-mcq-logistic-hessian",
            "type": "mcq",
            "title": "Convexity of Logistic Regression Cross-Entropy Loss",
            "prompt": "For binary logistic regression with design matrix X, the Hessian of the negative log-likelihood (binary cross-entropy loss) with respect to weights w is H = Xᵀ D X, where D_ii = p_i(1 - p_i). This implies the loss is:",
            "options": [
                {"value": "A", "label": "Convex everywhere (and strictly convex if X has full column rank)"},
                {"value": "B", "label": "Non-convex with multiple local minima"},
                {"value": "C", "label": "Concave everywhere"},
                {"value": "D", "label": "Admitting a closed-form non-iterative solution like OLS"},
            ],
            "answer": "A",
            "explanation": "Since p_i(1 - p_i) > 0, D is positive definite and XᵀDX is positive semi-definite, making the loss convex.",
        },
        {
            "id": "ml-mcq-pca-scaling",
            "type": "mcq",
            "title": "Feature Standardization Before PCA",
            "prompt": "Why is it standard practice to standardize features to zero mean and unit variance before running Principal Component Analysis (PCA) on features measured in different units?",
            "options": [
                {"value": "A", "label": "PCA maximizes variance, so unscaled features with large numerical magnitudes would dominate the first principal component"},
                {"value": "B", "label": "The covariance matrix is not symmetric unless features have unit variance"},
                {"value": "C", "label": "Singular Value Decomposition (SVD) fails to converge on unscaled matrices"},
                {"value": "D", "label": "Standardization guarantees that all eigenvalues are equal to 1"},
            ],
            "answer": "A",
            "explanation": "PCA is scale-dependent; without standardization, a feature measured in small units (e.g. cents vs. dollars) artificially dominates total variance.",
        },
        {
            "id": "ml-mcq-vanishing-grad",
            "type": "mcq",
            "title": "ReLU vs. Sigmoid in Deep Neural Networks",
            "prompt": "What is the primary advantage of the ReLU activation function f(x) = max(0, x) over the logistic sigmoid in deep neural networks?",
            "options": [
                {"value": "A", "label": "ReLU has a constant gradient of 1 for x > 0, mitigating the vanishing gradient problem during backpropagation"},
                {"value": "B", "label": "ReLU outputs are bounded in [0, 1] and represent probabilities directly"},
                {"value": "C", "label": "ReLU is twice differentiable at x = 0"},
                {"value": "D", "label": "ReLU prevents any neuron from ever outputting zero"},
            ],
            "answer": "A",
            "explanation": "Sigmoid derivatives are bounded by 0.25, causing gradients to decay exponentially with depth; ReLU has derivative 1 on (0, ∞).",
        },
    ]

    questions.extend(static_ml_mcqs)
    return questions


def write_question_files() -> list[str]:
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)

    categories = {
        "linear_algebra_calculus.json": generate_linear_algebra_calculus(),
        "probability_statistics.json": generate_probability_statistics(),
        "coding_algorithms.json": generate_coding_questions(),
        "machine_learning.json": generate_machine_learning(),
    }

    written_files: list[str] = []
    total_q = 0
    total_mcq = 0
    total_comp = 0
    for filename, q_list in categories.items():
        out_path = QUESTIONS_DIR / filename
        payload = {"questions": q_list}
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written_files.append(filename)
        n_mcq = sum(1 for q in q_list if q["type"] == "mcq")
        n_comp = len(q_list) - n_mcq
        total_q += len(q_list)
        total_mcq += n_mcq
        total_comp += n_comp
        print(
            f"Wrote {len(q_list):2d} unique questions ({n_mcq:2d} MCQ, {n_comp:2d} Complete) "
            f"-> question-bank/questions/{filename}"
        )

    print(f"Total unique questions: {total_q} ({total_mcq} MCQ, {total_comp} Complete)")
    return sorted(written_files)


def update_manifest(files: list[str]) -> None:
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        manifest = {
            "assessmentConfig": {
                "durationMinutes": 15,
                "targetQuestionCount": 30,
            },
            "files": [],
        }

    manifest["files"] = files
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {MANIFEST_PATH} with {len(files)} question set file(s).")


if __name__ == "__main__":
    generated_files = write_question_files()
    update_manifest(generated_files)