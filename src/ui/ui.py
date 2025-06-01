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

def draw_solution_to_axis(solution, axis):
    points = solution.problem.graph.points.T
    axis.scatter(points[0], points[1], s=60)

    w = solution.problem.graph.warehouse
    axis.scatter(points[0][w], points[1][w], s=65, c="red")

    for j in range(solution.problem.n_vehicles):
        for u, v in zip(solution.x_jv[j], solution.x_jv[j, 1:]):
            axis.arrow(
                *points[:, u],
                *(points[:, v] - points[:, u]),
                color=f"C{j}",
                head_width=0.6,
                length_includes_head=True,
            )
            if v == solution.problem.graph.warehouse:
                break

    for i in range(points.shape[1]):
        axis.annotate(f"{i}", (points[0][i], points[1][i]))

def draw_comparison(s1: Solution, s2: Solution):
    _, axes = plt.subplots(1, 2, figsize=(16, 7))
    draw_solution_to_axis(s1, axes[0])    
    draw_solution_to_axis(s2, axes[1])
    plt.show()
