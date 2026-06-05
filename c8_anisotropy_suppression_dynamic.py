import numpy as np

# =============================================================================
# 快速验证版：宏观观察者动态拟合各向同性度规
# 大幅降低计算量，但仍能展示统计平均对残余各向异性的压制趋势
# =============================================================================

L = 100                # 晶格大小
center = np.array([L//2, L//2, L//2])
n_sources = 200        # 源数量
distance = 40          # 宏观尺度，确保不越界

# 均匀采样方向（单位球面）
np.random.seed(42)
theta = np.arccos(2 * np.random.rand(n_sources) - 1)
phi = 2 * np.pi * np.random.rand(n_sources)
directions = np.column_stack([
    np.sin(theta) * np.cos(phi),
    np.sin(theta) * np.sin(phi),
    np.cos(theta)
])

def compute_spread(dvec):
    """模拟单个源的脉冲展宽（图距离方差）"""
    target = center + dvec * distance
    target = np.clip(np.round(target), 0, L-1).astype(int)
    spreads = []
    for _ in range(50):                # 微扰采样数减半
        perturb = np.random.randint(-1, 2, size=3)
        sub_target = np.clip(target + perturb, 0, L-1).astype(int)
        sub_gd = np.sum(np.abs(center - sub_target))
        spreads.append(sub_gd)
    return np.var(spreads)

# 初始单次测量
initial_spreads = np.array([compute_spread(d) for d in directions])

# 动态拟合：积分时间 T 从小到大
T_values = [5, 20, 100, 500]          # 大幅减小，但仍能看出趋势
residual_anisotropies = []

for T in T_values:
    mean_spreads = np.zeros(n_sources)
    for i in range(n_sources):
        # 每个源测量 T 次，取平均
        sample_spreads = [compute_spread(directions[i]) for _ in range(T)]
        mean_spreads[i] = np.mean(sample_spreads)
    
    # 方向投影（与最近主轴的夹角余弦）
    axial_proj = np.max(np.abs(directions), axis=1)
    corr = np.corrcoef(axial_proj, mean_spreads)[0, 1]
    residual = np.abs(corr) * np.std(mean_spreads) / np.mean(mean_spreads)
    residual_anisotropies.append(residual)

# 打印结果
print("=== Anisotropy Suppression by Dynamic Integration (Lightweight) ===")
print("Integration Time T | Residual Anisotropy")
print("-" * 40)
for T, res in zip(T_values, residual_anisotropies):
    print(f"{T:>16}  |  {res:.6e}")

# 预估：按 1/sqrt(T) 外推，需要多大的 T 才能达到 1e-17？
if residual_anisotropies[-1] > 0:
    required_T = (residual_anisotropies[-1] / 1e-17) ** 2
    print(f"\nBased on ~1/sqrt(T) scaling, to reach 1e-17 would require T ~ {required_T:.2e}")
    print("This is astronomically large, indicating that pure statistical averaging")
    print("is INSUFFICIENT. A dynamical mechanism (edge rewiring / global annealing)")
    print("is necessary to eliminate the systematic geometric bias at its root.")
else:
    print("\nResidual anisotropy already below threshold! (unexpected)")