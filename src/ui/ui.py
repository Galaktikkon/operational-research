import matplotlib.pyplot as plt

from model.solution import Solution


def draw_solution(solution: Solution):
    points = solution.problem.graph.points.T

    plt.figure(figsize=(12, 8))
    plt.scatter(points[0], points[1], s=60)

    w = solution.problem.graph.warehouse
    plt.scatter(points[0][w], points[1][w], s=65, c="red")

    for j in range(solution.problem.n_vehicles):
        for u, v in zip(solution.x_jv[j], solution.x_jv[j, 1:]):
            plt.arrow(
                *points[:, u],
                *(points[:, v] - points[:, u]),
                color=f"C{j}",
                head_width=0.6,
                length_includes_head=True,
            )
            if v == solution.problem.graph.warehouse:
                break
    plt.show()


def draw_comparison(s1: Solution, s2: Solution):
    _, axes = plt.subplots(1, 2, figsize=(16, 7))
    points = s1.problem.graph.points.T
    axes[0].scatter(points[0], points[1], s=60)

    w = s1.problem.graph.warehouse
    axes[0].scatter(points[0][w], points[1][w], s=65, c="red")

    for j in range(s1.problem.n_vehicles):
        for u, v in zip(s1.x_jv[j], s1.x_jv[j, 1:]):
            axes[0].arrow(
                *points[:, u],
                *(points[:, v] - points[:, u]),
                color=f"C{j}",
                head_width=0.6,
                length_includes_head=True,
            )
            if v == s1.problem.graph.warehouse:
                break

    for i in range(points.shape[1]):
        axes[0].annotate(f"{i}", (points[0][i], points[1][i]))

    points = s2.problem.graph.points.T
    axes[1].scatter(points[0], points[1], s=60)

    w = s2.problem.graph.warehouse
    axes[1].scatter(points[0][w], points[1][w], s=65, c="red")

    for j in range(s2.problem.n_vehicles):
        for u, v in zip(s2.x_jv[j], s2.x_jv[j, 1:]):
            axes[1].arrow(
                *points[:, u],
                *(points[:, v] - points[:, u]),
                color=f"C{j}",
                head_width=0.6,
                length_includes_head=True,
            )
            if v == s2.problem.graph.warehouse:
                break

    for i in range(points.shape[1]):
        axes[1].annotate(f"{i}", (points[0][i], points[1][i]))

    plt.show()
