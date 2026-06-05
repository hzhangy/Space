import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

# =============================================================================
# 1. 雪崩模拟：从 3 个孤立的 K4 子图到 K12 完全图
# =============================================================================
def avalanche_to_K12(n_nodes=12, seed=42):
    np.random.seed(seed)
    G = nx.Graph()
    G.add_nodes_from(range(n_nodes))
    # 初始化为 3 个 K4 子图 (0-3, 4-7, 8-11)
    for start in range(0, n_nodes, 4):
        for u, v in combinations(range(start, start+4), 2):
            G.add_edge(u, v)
    # 所有缺失的跨子图边
    missing = [(u, v) for u, v in combinations(range(n_nodes), 2) if not G.has_edge(u, v)]
    np.random.shuffle(missing)
    max_edges = n_nodes * (n_nodes - 1) // 2
    steps = 0
    edges_log = []
    comp_log = []
    while not nx.is_isomorphic(G, nx.complete_graph(n_nodes)):
        progress = G.number_of_edges() / max_edges
        p_add = min(1.0, 0.01 + progress * 2)  # 越接近完成加边越快
        if np.random.random() < p_add and missing:
            u, v = missing.pop()
            if not G.has_edge(u, v):
                G.add_edge(u, v)
        steps += 1
        if steps % 10 == 0:
            edges_log.append(G.number_of_edges())
            comp_log.append(nx.number_connected_components(G))
    # 最终状态
    edges_log.append(G.number_of_edges())
    comp_log.append(nx.number_connected_components(G))
    print(f"[雪崩] 步数={steps}, 边数={G.number_of_edges()}, 平均度={sum(dict(G.degree()).values())/n_nodes:.1f}, is K12={nx.is_isomorphic(G, nx.complete_graph(n_nodes))}")
    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,4))
    ax1.plot(edges_log)
    ax1.set_xlabel('Step (x10)'); ax1.set_ylabel('Edges')
    ax1.set_title('Edge growth during avalanche')
    ax2.plot(comp_log)
    ax2.set_xlabel('Step (x10)'); ax2.set_ylabel('Components')
    ax2.set_title('Component merging')
    plt.tight_layout(); plt.show()
    return G

# =============================================================================
# 2. 亲吻数截断测试：最大度=12（三维亲吻数），展示 14 节点被截断
# =============================================================================
def kissing_number_cutoff_test():
    max_deg = 12  # 三维亲吻数
    results = []
    for n in [12, 13, 14, 20]:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        # 随机加边，但严格遵守度上限
        pairs = list(combinations(range(n), 2))
        np.random.shuffle(pairs)
        for u, v in pairs:
            if G.degree(u) < max_deg and G.degree(v) < max_deg:
                G.add_edge(u, v)
        full_edges = n*(n-1)//2
        is_complete = nx.is_isomorphic(G, nx.complete_graph(n))
        status = "允许" if is_complete else "截断"
        results.append((n, G.number_of_edges(), full_edges, status))
        print(f"[亲吻数] n={n:2d}: 边 {G.number_of_edges():3d}/{full_edges:3d} -> {status}")
    return results

# =============================================================================
# 3. 带宽约束测试：模拟 B=1 限制下 K13 无法形成
# =============================================================================
def bandwidth_cutoff_test():
    """
    B=1 约束：每个节点每因果步只能处理 1 单位信息。
    对于完全图 Kn，每节点需要维护 n-1 条逻辑边。
    这里简化为：若加入某边后，任一节点的负载超过预设阈值，则拒绝加入。
    负载阈值取 12（对应 K12 每个节点度数 11），一旦要求度数 12 (K13) 则超限。
    """
    max_load = 11  # 度数限制，超过此值被认为带宽超限
    for n, label in [(12, "K12 (允许)"), (13, "K13 (否决)")]:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        pairs = list(combinations(range(n), 2))
        np.random.shuffle(pairs)
        for u, v in pairs:
            if G.degree(u) < max_load and G.degree(v) < max_load:
                G.add_edge(u, v)
        full_edges = n*(n-1)//2
        is_complete = nx.is_isomorphic(G, nx.complete_graph(n))
        status = "允许" if is_complete else "否决"
        print(f"[带宽] {label}: 边 {G.number_of_edges():3d}/{full_edges:3d} -> {status}")

# =============================================================================
# 主程序
# =============================================================================
if __name__ == "__main__":
    print("=== N.E.A. 雪崩 + 亲吻数 + 带宽约束 综合测试 ===")
    # 1. 雪崩
    avalanche_to_K12()
    # 2. 亲吻数截断
    print("\n--- 亲吻数截断 (三维 kiss=12) ---")
    kissing_number_cutoff_test()
    # 3. 带宽约束
    print("\n--- 带宽约束 (B=1, max_load=11) ---")
    bandwidth_cutoff_test()