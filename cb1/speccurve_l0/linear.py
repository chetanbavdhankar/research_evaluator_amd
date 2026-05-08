from __future__ import annotations

import math


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(column) for column in zip(*matrix, strict=False)]


def matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    right_t = transpose(right)
    return [[sum(a * b for a, b in zip(row, column, strict=False)) for column in right_t] for row in left]


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(row, vector, strict=False)) for row in matrix]


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(matrix)
    augmented = [row[:] + [vector[index]] for index, row in enumerate(matrix)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            raise ValueError("singular matrix")
        if pivot != col:
            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]

        scale = augmented[col][col]
        augmented[col] = [value / scale for value in augmented[col]]

        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            if factor == 0:
                continue
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[col], strict=False)
            ]

    return [row[-1] for row in augmented]


def inverse(matrix: list[list[float]]) -> list[list[float]]:
    n = len(matrix)
    columns: list[list[float]] = []
    for col in range(n):
        basis = [0.0] * n
        basis[col] = 1.0
        columns.append(solve_linear_system(matrix, basis))
    return transpose(columns)


def fit_linear_model(
    design: list[list[float]],
    outcome: list[float],
    ridge_lambda: float = 0.0,
) -> dict[str, object]:
    if not design:
        raise ValueError("empty design matrix")
    if len(design) != len(outcome):
        raise ValueError("design and outcome length mismatch")

    xt = transpose(design)
    xtx = matmul(xt, design)
    for index in range(len(xtx)):
        xtx[index][index] += ridge_lambda
    xty = matvec(xt, outcome)
    beta = solve_linear_system(xtx, xty)

    predictions = matvec(design, beta)
    residuals = [actual - predicted for actual, predicted in zip(outcome, predictions, strict=False)]
    dof = max(1, len(outcome) - len(beta))
    sigma2 = sum(residual * residual for residual in residuals) / dof

    try:
        covariance_base = inverse(xtx)
        standard_errors = [math.sqrt(max(0.0, sigma2 * covariance_base[i][i])) for i in range(len(beta))]
    except ValueError:
        standard_errors = [float("nan")] * len(beta)

    return {
        "beta": beta,
        "standard_errors": standard_errors,
        "rss": sum(residual * residual for residual in residuals),
        "dof": dof,
        "n": len(outcome),
    }


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("median requires values")
    sorted_values = sorted(values)
    midpoint = len(sorted_values) // 2
    if len(sorted_values) % 2:
        return sorted_values[midpoint]
    return (sorted_values[midpoint - 1] + sorted_values[midpoint]) / 2.0
