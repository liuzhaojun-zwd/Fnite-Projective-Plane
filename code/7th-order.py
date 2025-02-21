import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
from math import cos, sin, pi

def generate_projective_plane_points(order=7):
    """
    生成7阶有限射影平面的点
    7阶射影平面有 7² + 7 + 1 = 57 个点
    """
    num_points = order ** 2 + order + 1  # 7² + 7 + 1 = 57
    points = []

    # 中心点
    points.append((0, 0))

    # 生成多个环，每个环 8 个点
    num_rings = (num_points - 1) // 8
    for ring in range(num_rings):
        radius = 2 + ring * 2  # 每个环的半径逐渐增大
        for i in range(8):
            angle = 2 * pi * i / 8
            x = radius * cos(angle)
            y = radius * sin(angle)
            points.append((x, y))

    return np.array(points)

def generate_projective_lines(points, order=7):
    """
    生成7阶有限射影平面的线
    7阶射影平面有 7² + 7 + 1 = 57 条线，每条线上有8个点
    """
    num_points = len(points)
    num_lines = order ** 2 + order + 1  # 57条线
    points_per_line = order + 1  # 每条线上有8个点

    lines = []

    # 1. 生成通过中心点的线
    center_idx = 0
    for i in range(1, 9):  # 从第 1 个点到第 8 个点开始生成线
        line = [center_idx]
        current_idx = i
        for _ in range(points_per_line - 1):
            line.append(current_idx)
            current_idx = (current_idx + 8) % (num_points - 1) + 1  # 按环的间隔选取点
        lines.append(line)

    # 2. 生成环内的线
    for ring_start in range(1, num_points, 8):
        for start_offset in range(8):
            line = []
            for i in range(points_per_line):
                idx = (ring_start + start_offset + i) % 8 + ring_start
                line.append(idx)
            lines.append(line)

    # 3. 生成跨越环的线
    while len(lines) < num_lines:
        start_point = np.random.randint(1, num_points)
        line = [start_point]
        remaining = points_per_line - 1
        candidates = list(set(range(1, num_points)) - set(line))
        np.random.shuffle(candidates)
        line.extend(candidates[:remaining])
        if sorted(line) not in [sorted(l) for l in lines]:
            lines.append(line)

    return lines[:num_lines]

def create_bezier_curve(p1, p2, control_point_factor=0.3):
    """为两点创建三阶贝塞尔曲线路径"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    perp_x = -dy * control_point_factor
    perp_y = dx * control_point_factor
    ctrl1 = ((p1[0] + p2[0]) / 2 + perp_x, (p1[1] + p2[1]) / 2 + perp_y)
    ctrl2 = ((p1[0] + p2[0]) / 2 - perp_x, (p1[1] + p2[1]) / 2 - perp_y)
    verts = [p1, ctrl1, ctrl2, p2]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    return Path(verts, codes)

def visualize_projective_plane_curved(order=7):
    """
    使用曲线可视化7阶有限射影平面
    """
    points = generate_projective_plane_points(order)
    lines = generate_projective_lines(points, order)

    plt.figure(figsize=(16, 16), facecolor='white')
    ax = plt.gca()
    ax.set_facecolor('white')

    # 添加背景辉光
    # for i in range(12):
    #     alpha = 0.02
    #     size = 20 - i
    #     circle = plt.Circle((0, 0), size, color='#1a1a4a', alpha=alpha)
    #     ax.add_artist(circle)

    # 绘制曲线
    patches_list = []
    colors = []

    # 创建和谐的颜色方案
    color_list = []
    n_lines = len(lines)
    golden_ratio = (1 + 5 ** 0.5) / 2
    for i in range(n_lines):
        hue = (i * golden_ratio) % 1
        saturation = 0.8
        lightness = 0.6
        c = (1 - abs(2 * lightness - 1)) * saturation
        x = c * (1 - abs((hue * 6) % 2 - 1))
        m = lightness - c / 2
        if hue < 1 / 6:
            r, g, b = c + m, x + m, m
        elif hue < 2 / 6:
            r, g, b = x + m, c + m, m
        elif hue < 3 / 6:
            r, g, b = m, c + m, x + m
        elif hue < 4 / 6:
            r, g, b = m, x + m, c + m
        elif hue < 5 / 6:
            r, g, b = x + m, m, c + m
        else:
            r, g, b = c + m, m, x + m
        color_list.append((r, g, b, 0.75))

    # 为每条线计算贝塞尔曲线
    control_factor = 0.35
    for i, line in enumerate(lines):
        for j in range(len(line)):
            for k in range(j + 1, len(line)):
                p1 = points[line[j]]
                p2 = points[line[k]]
                dist = np.linalg.norm(p1 - p2)
                adjusted_factor = control_factor * (1 + dist / 20)
                path = create_bezier_curve(p1, p2, adjusted_factor)
                patch = patches.PathPatch(path, facecolor='none', lw=2, alpha=0.8)
                patches_list.append(patch)
                colors.append(color_list[i % len(color_list)])

    collection = PatchCollection(patches_list, facecolor='none', edgecolors=colors, linewidths=1.5)
    ax.add_collection(collection)

    # 为点添加光晕效果
    for p in points:
        for r in [0.8, 0.5, 0.3]:
            circle = plt.Circle((p[0], p[1]), r, color='gold', alpha=0.07)
            ax.add_artist(circle)

    # 绘制点
    plt.scatter(points[:, 0], points[:, 1], s=180, c='#fff7cc', alpha=0.9,
                edgecolors='#ffd700', linewidth=1.5, zorder=10)

    # 使用大字号标注点的编号
    for i, p in enumerate(points):
        circle = plt.Circle((p[0], p[1]), 0.8, color='white', alpha=0.7, zorder=11)
        ax.add_artist(circle)
        plt.text(p[0], p[1], str(i), color='black', ha='center', va='center',
                 fontsize=16, fontweight='bold', zorder=12)

    plt.axis('off')
    plt.axis('equal')

    plt.tight_layout()
    plt.savefig('finite_projective_plane_order7_curved.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

    print(f"总点数: {len(points)} (应为 {order ** 2 + order + 1})")
    print(f"总线数: {len(lines)} (应为 {order ** 2 + order + 1})")
    print(f"每条线上的点数: {[len(line) for line in lines[:3]]}... (应全为 {order + 1})")

# 执行可视化
np.random.seed(42)  # 设置随机种子以确保可重复性
visualize_projective_plane_curved(7)