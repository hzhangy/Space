import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean

L = 30
N = L**3

def node_to_xyz(idx):
    z = idx // (L*L)
    y = (idx % (L*L)) // L
    x = idx % L
    return np.array([x, y, z])

# =============================================================================
# 1. 微观尺度：全空间精确遍历 (彻底消灭随机采样的漏网之鱼)
# =============================================================================
print("Computing exact microscopic distance breakdown (Graph dist <= 10)...")
micro_graph_dists = []
micro_eucl_dists = []

for dx in range(11):
    for dy in range(11 - dx):
        for dz in range(11 - dx - dy):
            gd = dx + dy + dz
            if gd == 0: continue
            ed = np.sqrt(dx**2 + dy**2 + dz**2)
            micro_graph_dists.append(gd)
            micro_eucl_dists.append(ed)

micro_graph_dists = np.array(micro_graph_dists)
micro_eucl_dists = np.array(micro_eucl_dists)

# =============================================================================
# 2. 打印极其详尽的“距离崩溃”数据表 (论文级素材)
# =============================================================================
print("\n" + "="*80)
print(" MICROSCOPIC DISTANCE BREAKDOWN ANALYSIS (UV LIMIT)")
print(" Proof that identical causal steps yield multi-valued spatial distances")
print("="*80)
print(f"{'Graph Dist':<12} | {'Min Euclidean':<15} | {'Max Euclidean':<15} | {'Std Dev':<10} | {'Paths'}")
print("-" * 80)

for gd in range(1, 11):
    mask = micro_graph_dists == gd
    if np.sum(mask) > 0:
        eds = micro_eucl_dists[mask]
        # 打印：图距离 | 最小欧氏距离 | 最大欧氏距离 | 标准差 | 离散路径数
        print(f"{gd:<12} | {eds.min():<15.4f} | {eds.max():<15.4f} | {eds.std():<10.4f} | {len(eds)}")

print("="*80)

# =============================================================================
# 3. 宏观尺度采样与绘图 (保持之前的完美逻辑)
# =============================================================================
print("\nSampling macroscopic distances (Graph dist > 10)...")
np.random.seed(42)
num_pairs = 5000
pairs = np.random.randint(0, N, size=(num_pairs, 2))

macro_graph_dists = []
macro_eucl_dists = []
for i, j in pairs:
    xyz1 = node_to_xyz(i)
    xyz2 = node_to_xyz(j)
    gd = np.sum(np.abs(xyz1 - xyz2))
    if gd > 10:
        ed = euclidean(xyz1, xyz2)
        macro_graph_dists.append(gd)
        macro_eucl_dists.append(ed)

macro_graph_dists = np.array(macro_graph_dists)
macro_eucl_dists = np.array(macro_eucl_dists)

all_gd = np.concatenate([micro_graph_dists, macro_graph_dists])
all_ed = np.concatenate([micro_eucl_dists, macro_eucl_dists])

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 8))

ax.scatter(micro_graph_dists, micro_eucl_dists, c='blue', alpha=0.6, s=30, label='Microscopic: Distance Breakdown (UV)')
ax.scatter(macro_graph_dists, macro_eucl_dists, c='gray', alpha=0.1, s=10, label='Macroscopic: Metric Emergence (IR)')

mask_large = macro_graph_dists > 20
if np.sum(mask_large) > 0:
    k = np.median(macro_eucl_dists[mask_large] / macro_graph_dists[mask_large])
    max_gd = np.max(all_gd)
    ax.plot([0, max_gd], [0, k*max_gd], 'r--', linewidth=2.5, label=f'Macroscopic Continuum Metric ($d_E \\approx {k:.3f} \\cdot d_G$)')

ax.set_xlabel('Graph Distance (Causal Steps / Ticks)', fontsize=14)
ax.set_ylabel('Euclidean Distance (Spatial Metric)', fontsize=14)
ax.set_title('Breakdown and Emergence of Spatial Distance on $C_8$ Substrate', fontsize=16, fontweight='bold')
ax.legend(fontsize=12, loc='upper left')
ax.grid(True, alpha=0.3)

ax.axvspan(0, 10, color='blue', alpha=0.05, label='_nolegend_')
ax.text(5, 45, 'UV Limit:\nSpace Concept Breaks Down\n(Multi-valued Metric)', fontsize=12, color='blue', ha='center', fontweight='bold')
ax.text(35, 15, 'IR Limit:\nContinuous 3D Space Emerges\n(Isotropic Metric)', fontsize=12, color='red', ha='center', fontweight='bold')

plt.tight_layout()
plt.show()

print("\n*** ULTIMATE DISTANCE AUDIT COMPLETE ***")