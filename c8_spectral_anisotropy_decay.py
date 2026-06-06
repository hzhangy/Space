import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy import sparse
import random

# 构建 C8 图
L = 10
N = L**3

def node_index(x, y, z):
    return (z % L) * L * L + (y % L) * L + (x % L)

adj = [[] for _ in range(N)]
all_edges = []
for x in range(L):
    for y in range(L):
        for z in range(L):
            u = node_index(x, y, z)
            for dx, dy, dz in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
                v = node_index(x+dx, y+dy, z+dz)
                adj[u].append(v)
                if u < v:
                    all_edges.append((u, v))

# 构建基础拉普拉斯矩阵 L0
row = []
col = []
data = []
for x in range(L):
    for y in range(L):
        for z in range(L):
            u = node_index(x, y, z)
            degree = 0
            for dx, dy, dz in [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]:
                v = node_index(x+dx, y+dy, z+dz)
                row.append(u); col.append(v); data.append(-1)
                degree += 1
            row.append(u); col.append(u); data.append(degree)
L0 = sparse.csr_matrix((data, (row, col)), shape=(N, N))

# 初始化缝合边：随机选择 10%
num_stitch = int(0.1 * len(all_edges))
stitching_edges = set(random.sample(all_edges, num_stitch))

def build_laplacian(stitching_set):
    L_copy = L0.copy()
    for u, v in stitching_set:
        L_copy[u, v] -= 1
        L_copy[v, u] -= 1
        L_copy[u, u] += 1
        L_copy[v, v] += 1
    return L_copy

def anisotropy_norm(L_sparse):
    L_dense = L_sparse.toarray()
    off_diag = L_dense[~np.eye(N, dtype=bool)]
    return np.std(off_diag)

num_steps = 500
aniso_history = []
for step in range(num_steps):
    L_current = build_laplacian(stitching_edges)
    aniso = anisotropy_norm(L_current)
    aniso_history.append(aniso)

    # 随机重连一条缝合边
    if stitching_edges:
        edge_to_remove = random.choice(list(stitching_edges))
        stitching_edges.remove(edge_to_remove)
        candidates = [e for e in all_edges if e not in stitching_edges]
        edge_to_add = random.choice(candidates)
        stitching_edges.add(edge_to_add)

# 绘图
plt.figure(figsize=(10,4))
plt.plot(aniso_history)
plt.xlabel('Annealing step')
plt.ylabel('Anisotropic norm (Frobenius)')
plt.title('Decay of Laplacian anisotropy during rewiring')
plt.grid(alpha=0.3)

def exp_dec(t, a, tau, c):
    return a * np.exp(-t/tau) + c
try:
    popt, _ = curve_fit(exp_dec, np.arange(num_steps), aniso_history, p0=[1,100,0.1])
    plt.plot(np.arange(num_steps), exp_dec(np.arange(num_steps), *popt), 'r--', label=f'tau={popt[1]:.1f}')
    plt.legend()
except:
    pass

plt.tight_layout()
plt.show()
print(f"初始各向异性范数: {aniso_history[0]:.4f}")
print(f"最终各向异性范数: {aniso_history[-1]:.4f}")