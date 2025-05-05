from model.solution import Solution
import matplotlib.pyplot as plt


def draw_solution(solution: Solution):
    points = solution.problem.graph.points.reshape(2, -1)

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
