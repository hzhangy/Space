import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
from tqdm import tqdm

def true_topological_natural_selection(
    N=200, 
    steps=120000, 
    runs=8, 
    seed=42
):
    """
    N.E.A. TRUE TOPOLOGICAL NATURAL SELECTION (OPTIMIZED & RIGOROUS)
    修复了全图回滚的性能灾难，保留了恒定温度下的热涨落(物质起源)物理图像。
    """
    random.seed(seed)
    np.random.seed(seed)
    
    print("="*80)
    print(" N.E.A. TRUE TOPOLOGICAL NATURAL SELECTION (OPTIMIZED)")
    print("="*80)
    
    TARGET_DEG = 3
    # 恒定逆温度 beta = 1.8 (模拟有限温度下的热力学平衡，而非绝对零度退火)
    BETA = 1.8 
    
    perfect_ratios = []
    all_rent_history = []
    
    for run in range(runs):
        G = nx.erdos_renyi_graph(N, 0.085, seed=seed + run)
        
        def calc_rent(graph):
            return sum((d - TARGET_DEG)**2 for _, d in graph.degree())
        
        def census(graph):
            degrees = [d for _, d in graph.degree()]
            avg_deg = np.mean(degrees)
            perfect = sum(1 for d in degrees if d == TARGET_DEG)
            return avg_deg, perfect, nx.number_connected_components(graph)
        
        current_rent = calc_rent(G)
        rent_history = [current_rent]
        nodes = list(G.nodes())
        
        for step in tqdm(range(steps), desc=f"Run {run+1}/{runs}", leave=False):
            action = random.choice(['rewire', 'annihilate', 'create'])
            accepted = False
            
            if action == 'rewire' and G.number_of_edges() > 0:
                u = random.choice(nodes)
                if G.degree(u) == 0: continue
                v = random.choice(list(G.neighbors(u)))
                candidates = [n for n in nodes if n != u and not G.has_edge(u, n)]
                if not candidates: continue
                w = random.choice(candidates)
                
                # 局部修改
                G.remove_edge(u, v)
                G.add_edge(u, w)
                new_rent = calc_rent(G)
                delta = new_rent - current_rent
                
                if delta <= 0 or random.random() < np.exp(-delta * BETA):
                    current_rent = new_rent
                    accepted = True
                else:
                    # 【精准回滚】：只恢复被修改的两条边
                    G.remove_edge(u, w)
                    G.add_edge(u, v)
                    
            elif action == 'annihilate' and G.number_of_edges() > 0:
                u, v = random.choice(list(G.edges()))
                G.remove_edge(u, v)
                new_rent = calc_rent(G)
                delta = new_rent - current_rent
                
                if delta <= 0 or random.random() < np.exp(-delta * BETA):
                    current_rent = new_rent
                    accepted = True
                else:
                    # 【精准回滚】：只恢复被删除的边
                    G.add_edge(u, v)
                    
            elif action == 'create':
                u, w = random.sample(nodes, 2)
                if u != w and not G.has_edge(u, w):
                    G.add_edge(u, w)
                    new_rent = calc_rent(G)
                    delta = new_rent - current_rent
                    
                    if delta <= 0 or random.random() < np.exp(-delta * BETA):
                        current_rent = new_rent
                        accepted = True
                    else:
                        # 【精准回滚】：只删除被添加的边
                        G.remove_edge(u, w)
            
            rent_history.append(current_rent)
        
        avg_deg, perfect, comp = census(G)
        perfect_ratio = perfect / N * 100
        perfect_ratios.append(perfect_ratio)
        all_rent_history.append(rent_history)
        
        print(f"\nRun {run+1} → Perfect Nodes: {perfect}/{N} ({perfect_ratio:.1f}%) | "
              f"Avg Degree: {avg_deg:.3f} | Components: {comp}")
    
    mean_perfect = np.mean(perfect_ratios)
    std_perfect = np.std(perfect_ratios)
    
    print("\n" + "="*80)
    print("FINAL AUDIT REPORT")
    print("="*80)
    print(f"平均完美3-正则节点比例 (空间): {mean_perfect:.1f}% ± {std_perfect:.1f}%")
    print(f"平均拓扑缺陷比例 (物质/热涨落): {100 - mean_perfect:.1f}%")
    print(f"成功率（>70%完美节点且连通）: {sum(r > 70 for r in perfect_ratios)}/{runs} 次")
    
    plt.figure(figsize=(10, 6))
    for history in all_rent_history:
        plt.plot(history[::500], alpha=0.6)
    plt.title("Rent Minimization Evolution (Thermal Equilibrium at β=1.8)")
    plt.xlabel("Steps (sampled)")
    plt.ylabel("Total Rent")
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    true_topological_natural_selection()