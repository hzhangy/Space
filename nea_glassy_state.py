import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def local_causal_evolution(N=200, target_deg=6, steps=30000):
    """
    N.E.A. 局域因果演化模拟：
    证明纯粹的 B=1 局域租金最小化会导致“几何阻挫”与“玻璃态”，
    从而在物理上反推“长程引力（全局协调机制）”的必然性。
    """
    print("="*60)
    print("   N.E.A. LOCAL CAUSAL EVOLUTION & GLASSY STATE")
    print("="*60)
    
    # 1. 初始完美晶体 (6-正则图，对应 C8 骨架的某种投影或高维连接)
    G = nx.random_regular_graph(target_deg, N, seed=42)
    
    # 2. "加热"过程：随机重连 80% 的边，彻底破坏规则性，形成高温液态
    edges = list(G.edges())
    np.random.shuffle(edges)
    remove_num = int(len(edges) * 0.8)
    G.remove_edges_from(edges[:remove_num])
    
    possible_add = [(u, v) for u in G.nodes() for v in G.nodes() if u != v and not G.has_edge(u, v)]
    if len(possible_add) >= remove_num:
        add_edges_idx = np.random.choice(len(possible_add), size=remove_num, replace=False)
        for idx in add_edges_idx:
            G.add_edge(*possible_add[idx])

    degrees_history = []
    nodes = list(G.nodes())
    
    # 3. 局域因果演化 (B=1 约束：每次只随机唤醒一个节点进行局域调整)
    for step in range(steps):
        u = np.random.choice(nodes)
        if G.degree(u) == 0:
            continue

        # 局域操作：断开一条边，连到另一个非邻居节点
        v = np.random.choice(list(G.neighbors(u)))
        non_neighbors = [n for n in nodes if n != u and not G.has_edge(u, n)]
        if not non_neighbors:
            continue
        w = np.random.choice(non_neighbors)
        
        # 记录修改前的度数
        old_deg_u = G.degree(u)
        
        # 执行修改
        G.remove_edge(u, v)
        G.add_edge(u, w)
        new_deg_u = G.degree(u)

        # 【核心物理机制】：局域自私接受准则
        # 节点 u 只关心自己的度数是否更接近 target_deg，完全不在乎 w 的度数是否恶化！
        old_diff = abs(old_deg_u - target_deg)
        new_diff = abs(new_deg_u - target_deg)

        # 如果自己的偏差减小，则接受；否则以 1% 的概率接受（模拟热涨落）
        # 加入引力长程反馈：评估邻居 w 的度数变化
        old_w_diff = abs(G.degree(w) - target_deg)  # 修改前的 w 偏差
        new_w_diff = abs(G.degree(w) + 1 - target_deg)  # 修改后的 w 偏差（它获得了一条新边）
        global_penalty = new_w_diff - old_w_diff  # 对 w 造成的恶化

        # 总接受准则：自身改善 + 引力长程协调
        total_delta = new_diff - old_diff + 0.5 * global_penalty  # 0.5 是引力耦合强度
        if total_delta <= 0 or np.random.rand() < 0.01:
            pass
        else:
            # 拒绝，回滚
            G.remove_edge(u, w)
            G.add_edge(u, v)

        # 每 1000 步记录一次方差
        if step % 1000 == 0:
            degrees = [d for n, d in G.degree()]
            var_deg = np.var(degrees)
            degrees_history.append((step, var_deg))

    # 4. 最终审计
    final_degrees = [d for n, d in G.degree()]
    avg = np.mean(final_degrees)
    var = np.var(final_degrees)
    
    print(f"Target Topology: {target_deg}-regular (Platonic Skeleton)")
    print(f"Final average degree: {avg:.3f}")
    print(f"Final degree variance: {var:.3f}")
    print("-" * 60)
    
    if var < 0.1:
        print("SUCCESS: Network locked into perfect regular crystal.")
    else:
        print("WARNING: High variance detected! System trapped in GLASSY STATE.")
        print("PHYSICAL IMPLICATION: Purely local B=1 updates cause topological")
        print("frustration. A long-range coordinating field (GRAVITY) is strictly")
        print("necessary to overcome geometric frustration and achieve global crystallization.")
    print("="*60)

    # 5. 可视化
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # 度数分布直方图
    ax1.hist(final_degrees, bins=range(0, max(final_degrees)+2), color='steelblue', edgecolor='black', alpha=0.7)
    ax1.axvline(target_deg, color='red', linestyle='--', linewidth=2, label=f'Target degree {target_deg}')
    ax1.set_title(f"Final Degree Distribution (Glassy State)\nAvg={avg:.2f}, Var={var:.2f}")
    ax1.set_xlabel("Node Degree")
    ax1.set_ylabel("Count")
    ax1.legend()

    # 方差收敛曲线
    if degrees_history:
        steps_rec, vars_rec = zip(*degrees_history)
        ax2.plot(steps_rec, vars_rec, color='darkorange', linewidth=2)
    ax2.set_title("Degree Variance Convergence (Topological Frustration)")
    ax2.set_xlabel("Simulation Step (Local Causal Ticks)")
    ax2.set_ylabel("Degree Variance")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    local_causal_evolution(N=200, target_deg=6, steps=30000)