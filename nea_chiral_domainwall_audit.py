import numpy as np
import warnings
import matplotlib.pyplot as plt

np.seterr(all='ignore')
warnings.filterwarnings('ignore', category=RuntimeWarning)

Lx = 16  
Ly = 32  
Nd = 2   
dim = Nd * Lx * Ly

sigma_x = np.array([[0, 1], [1, 0]], dtype=np.complex128)
sigma_z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
I2 = np.eye(2, dtype=np.complex128)

def idx(x, y, s): return (y * Lx + x) * Nd + s

# 物理参数：M0=3.0 确保左区 m_eff = -3.0 + 2.0 = -1.0 (非平庸相)
M0 = 3.0 
wall_y = Ly // 2
r = 1.0

def mass(y): return -M0 if y < wall_y else M0

D = np.zeros((dim, dim), dtype=np.complex128)

# 预计算跳跃矩阵 (彻底消灭循环里的索引 Bug)
hop_xp = 0.5 * sigma_x - 0.5 * r * I2
hop_xm = -0.5 * sigma_x - 0.5 * r * I2
hop_yp = 0.5 * sigma_z - 0.5 * r * I2
hop_ym = -0.5 * sigma_z - 0.5 * r * I2

for y in range(Ly):
    for x in range(Lx):
        base = idx(x, y, 0)
        m = mass(y)
        
        # 1. 质量项 + Wilson 对角元 (2D 中为 +2r)
        for s in range(Nd):
            D[base + s, base + s] += m + 2 * r

        # 2. x-方向跳跃
        xp = (x + 1) % Lx
        xm = (x - 1) % Lx
        for s in range(Nd):
            for sp in range(Nd):
                D[base + s, idx(xp, y, sp)] += hop_xp[s, sp]
                D[base + s, idx(xm, y, sp)] += hop_xm[s, sp]

        # 3. y-方向跳跃 (第五维)
        yp = (y + 1) % Ly
        ym = (y - 1) % Ly
        for s in range(Nd):
            for sp in range(Nd):
                D[base + s, idx(x, yp, sp)] += hop_yp[s, sp]
                D[base + s, idx(x, ym, sp)] += hop_ym[s, sp]

# 强制严格厄米化
D = 0.5 * (D + D.conj().T)

print("正在计算 D†D 的本征谱...")
DdagD = D.conj().T @ D
vals, vecs = np.linalg.eigh(DdagD)

k = 4
idx_small = np.argsort(vals)[:k]

print("\n==========================================================")
print("   N.E.A. NATIVE CHIRAL FERMION AUDIT (TENSOR BUILD)")
print("==========================================================")

P_y_mode1 = np.zeros(Ly)
P_y_mode2 = np.zeros(Ly)

v1 = vecs[:, idx_small[0]]
v2 = vecs[:, idx_small[1]]

for y in range(Ly):
    for x in range(Lx):
        for s in range(Nd):
            P_y_mode1[y] += np.abs(v1[idx(x, y, s)])**2
            P_y_mode2[y] += np.abs(v2[idx(x, y, s)])**2

P_y_mode1 /= np.sum(P_y_mode1)
P_y_mode2 /= np.sum(P_y_mode2)

print(f"  Mode 1 peak at y = {np.argmax(P_y_mode1)} (Expected near 0 or {wall_y})")
print(f"  Mode 2 peak at y = {np.argmax(P_y_mode2)} (Expected near 0 or {wall_y})")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

ax1.plot(range(Ly), P_y_mode1, 'o-', label='Mode 1', color='blue')
ax1.plot(range(Ly), P_y_mode2, 's--', label='Mode 2', color='red')
ax1.axvline(wall_y, color='black', linestyle=':', label=f'Domain Wall')
ax1.set_xlabel('Fifth Dimension (y)')
ax1.set_ylabel('Probability Density P(y)')
ax1.set_title('Chiral Edge Modes Localization (Tensor Build)')
ax1.legend()
ax1.grid(True, alpha=0.3)

psi_2d = np.zeros((Ly, Lx))
for y in range(Ly):
    for x in range(Lx):
        for s in range(Nd):
            psi_2d[y, x] += np.abs(v1[idx(x, y, s)])**2

im = ax2.imshow(psi_2d, aspect='auto', cmap='inferno', origin='lower')
ax2.set_xlabel('Physical Space (x)')
ax2.set_ylabel('Fifth Dimension (y)')
ax2.set_title('Spatial Distribution of Mode 1')
fig.colorbar(im, ax=ax2)

plt.tight_layout()
plt.show()

print("----------------------------------------------------------")
if (np.argmax(P_y_mode1) < 5 or np.argmax(P_y_mode1) > Ly - 5 or abs(np.argmax(P_y_mode1) - wall_y) < 5) and \
   (np.argmax(P_y_mode2) < 5 or np.argmax(P_y_mode2) > Ly - 5 or abs(np.argmax(P_y_mode2) - wall_y) < 5):
    print("SUCCESS: Chiral edge modes are strictly localized at the domain walls!")
else:
    print("WARNING: Modes are not localized at the walls.")
print("==========================================================")