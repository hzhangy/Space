import numpy as np
import matplotlib.pyplot as plt

# 物理常数
G_exp = 6.67430e-11          # 实验引力常数 (m³ kg⁻¹ s⁻²)
M = 1.0e30                   # 源质量 (kg)

# N.E.A. 参数
R_c = 3.0e20                 # 临界半径 (m) ~3 kpc
delta = R_c / 2.0            # 过渡宽度

def newton_acc(r):
    return G_exp * M / r**2

def q_logistic(r):
    """有效维数：Logistic 平滑过渡，高密度→2，低密度→1。
       使用 scipy.special.expit 避免大数溢出。"""
    from scipy.special import expit
    # expit(x) = 1/(1+exp(-x))，这里需要 1/(1+exp((r-R_c)/delta)) = expit(-(r-R_c)/delta)
    return 1.0 + expit(-(r - R_c) / delta)

def nea_acc_safe(r):
    """N.E.A. 加速度，对极大 r 截断以避免模型失效。"""
    # 点质量模型仅在 r < 1e23 m 左右有效，超出后不再适用
    mask = r < 1e23
    a_nea = np.zeros_like(r)
    if np.any(mask):
        q = q_logistic(r[mask])
        a_nea[mask] = newton_acc(r[mask]) * (1.0 + r[mask] / R_c)**(2.0 - q)
    # 极大距离处直接设为 nan，不参与比较
    a_nea[~mask] = np.nan
    return a_nea

# ---------- 表格对比 ----------
r_table = np.array([1e-10, 1e-5, 1e0, 1e5, 1e10, 1e15,
                    1e20, R_c, 1e21, 3e21, 1e22, 1e26])
regions = ["Atomic", "Micro", "Everyday", "Terrestrial", "Solar sys",
           "Interstellar", "Galactic", "Galactic (R_c)", "Outer gal",
           "Outer gal", "Outer gal", "Cosmic (model limit)"]

print("=" * 105)
print(" NEWTON (GR) vs N.E.A. GRAVITATIONAL ACCELERATION  (Logistic q → 1, overflow-safe)")
print("=" * 105)
print(f"{'r (m)':<15} | {'Newton a':<18} | {'N.E.A. a':<18} | {'Dev (%)':<12} | {'Region'}")
print("-" * 105)

for r, reg in zip(r_table, regions):
    an = newton_acc(r)
    ae = nea_acc_safe(np.array([r]))[0]
    if np.isnan(ae):
        print(f"{r:<15.2e} | {an:<18.3e} | {'N/A (model limit)':<18} | {'---':<12} | {reg}")
    else:
        dev = (ae - an) / an * 100
        print(f"{r:<15.2e} | {an:<18.3e} | {ae:<18.3e} | {dev:<+12.2f} | {reg}")

print("=" * 105)
print("""
Note:
- For r >> 10 kpc, q stays at 1, yielding a ~ 1/r force law that keeps rotation curves flat.
- Beyond ~1e23 m (cosmological scales), the point-mass model is invalid; N.E.A. acceleration is
  not computed here because cosmic expansion dominates.
""")

# ---------- 全尺度对数图 ----------
r_plot = np.logspace(-10, 26, 1000)
a_newton = newton_acc(r_plot)
a_nea = nea_acc_safe(r_plot)

plt.figure(figsize=(12, 8))
plt.loglog(r_plot, a_newton, 'k--', linewidth=2, label="Newton / GR ($1/r^2$)")
# 只画出有效范围内的 N.E.A. 曲线
mask_valid = ~np.isnan(a_nea)
plt.loglog(r_plot[mask_valid], a_nea[mask_valid], 'r-', linewidth=2, alpha=0.8,
           label="N.E.A. (Logistic $q\\to 1$, valid range)")
plt.axvline(R_c, color='gray', linestyle=':', alpha=0.7, label=f"$R_c \\approx 3$ kpc")
# 标注关键尺度
scales = [1e-10, 1e0, 1e10, 1e20, 1e23]
labels = ['Atomic', '1 m', 'Solar sys', 'Galactic', 'Model limit']
for s, l in zip(scales, labels):
    plt.axvline(s, color='blue', linestyle=':', alpha=0.5)
    plt.text(s, 1e-5, l, rotation=90, fontsize=9)

plt.xlabel("Distance $r$ (m)", fontsize=14)
plt.ylabel("Gravitational acceleration $a$ (m/s²)", fontsize=14)
plt.title("Newton vs N.E.A. Gravitational Acceleration\n(Overflow‑safe, Logistic $q$, Model Limit at 1e23 m)", fontsize=16, fontweight='bold')
plt.legend(fontsize=12)
plt.grid(True, which='both', alpha=0.3)
plt.tight_layout()
plt.show()