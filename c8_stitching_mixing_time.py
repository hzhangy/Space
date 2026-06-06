import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import random

# 构建 C8 图
L = 20
N = L**3

def node_index(x, y, z):
    return (z % L) * L * L + (y % L) * L + (x % L)

adj = [[] for _ in range(N)]
all_edges = set()
for x in range(L):
    for y in range(L):
        for z in range(L):
            u = node_index(x, y, z)
            for dx, dy, dz in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
                v = node_index(x+dx, y+dy, z+dz)
                adj[u].append(v)
                if u < v:
                    all_edges.add((u, v))

# 初始化缝合边：随机选择 5% 的边
num_stitch = int(0.05 * len(all_edges))
stitching_edges = set(random.sample(list(all_edges), num_stitch))

# 距离计算
def manhattan_dist(u, v):
    x1 = u % L; y1 = (u // L) % L; z1 = u // (L*L)
    x2 = v % L; y2 = (v // L) % L; z2 = v // (L*L)
    dx = min(abs(x1 - x2), L - abs(x1 - x2))
    dy = min(abs(y1 - y2), L - abs(y1 - y2))
    dz = min(abs(z1 - z2), L - abs(z1 - z2))
    return dx + dy + dz

def axis_diag_difference():
    # 轴向
    u1 = node_index(0,0,0)
    v1 = node_index(L//2,0,0)
    d_axis = manhattan_dist(u1, v1)
    # 体对角线
    u2 = node_index(0,0,0)
    v2 = node_index(L//4, L//4, L//4)
    d_diag = manhattan_dist(u2, v2)
    return abs(d_axis - d_diag)

# 重连动力学
num_steps = 2000
diff_history = []
for step in range(num_steps):
    diff = axis_diag_difference()
    diff_history.append(diff)
    
    # 随机移除一条缝合边
    edge_to_remove = random.choice(list(stitching_edges))
    stitching_edges.remove(edge_to_remove)
    # 随机添加一条非缝合边
    candidates = list(all_edges - stitching_edges)
    edge_to_add = random.choice(candidates)
    stitching_edges.add(edge_to_add)

# 绘图
plt.figure(figsize=(12,4))
plt.subplot(1,2,1)
plt.plot(diff_history, alpha=0.7)
plt.xlabel('Rewiring step')
plt.ylabel('Axis-diagonal distance difference')
plt.title('Directional difference decay')
plt.grid(alpha=0.3)

# 拟合指数衰减
def exp_decay(t, a, tau, c):
    return a * np.exp(-t/tau) + c

t_vals = np.arange(num_steps)
try:
    popt, _ = curve_fit(exp_decay, t_vals, diff_history, p0=[10, 500, 0])
    a, tau, c = popt
    plt.plot(t_vals, exp_decay(t_vals, *popt), 'r--', label=f'exp fit: tau={tau:.1f}')
    plt.legend()
except:
    pass

plt.subplot(1,2,2)
diff_arr = np.array(diff_history) - np.mean(diff_history)
autocorr = np.correlate(diff_arr, diff_arr, mode='full')
autocorr = autocorr[len(autocorr)//2:]
autocorr /= autocorr[0]
plt.plot(autocorr[:500])
plt.xlabel('Lag (steps)')
plt.ylabel('Autocorrelation')
plt.title('Autocorrelation of direction difference')
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()

print("混合时间分析：")
print(f"初始差异: {diff_history[0]:.2f}")
print(f"最终差异: {diff_history[-1]:.2f}")
if popt is not None:
    print(f"拟合时间常数 tau = {tau:.1f} 步")