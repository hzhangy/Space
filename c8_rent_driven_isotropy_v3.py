import numpy as np
import matplotlib.pyplot as plt
import random
from scipy.optimize import curve_fit
import multiprocessing as mp

# ========== 参数 ==========
L = 10
T_INIT = 10.0
T_MIN = 0.01
COOLING_RATE = 0.9995
STEPS = 5000
RECORD_INTERVAL = 100
NUM_TRIALS = 8
NUM_PROCESSES = 8

# ========== 图结构 ==========
def idx(x, y, z):
    return (z % L) * L * L + (y % L) * L + (x % L)

x_edges, y_edges, z_edges = [], [], []
for x in range(L):
    for y in range(L):
        for z in range(L):
            u = idx(x, y, z)
            vx = idx((x+1)%L, y, z)
            vy = idx(x, (y+1)%L, z)
            vz = idx(x, y, (z+1)%L)
            x_edges.append((u, vx) if u < vx else (vx, u))
            y_edges.append((u, vy) if u < vy else (vy, u))
            z_edges.append((u, vz) if u < vz else (vz, u))
x_edges = list(set(x_edges))
y_edges = list(set(y_edges))
z_edges = list(set(z_edges))
all_possible = set(x_edges + y_edges + z_edges)
candidates_pool = list(all_possible)

def compute_variance(stitch_set):
    nx = sum(1 for e in stitch_set if e in x_edges)
    ny = sum(1 for e in stitch_set if e in y_edges)
    nz = sum(1 for e in stitch_set if e in z_edges)
    return np.var([nx, ny, nz]), (nx, ny, nz)

def run_single_trial(seed):
    random.seed(seed)
    np.random.seed(seed)
    stitch_driven = set(random.sample(x_edges, 900))
    stitch_random = set(stitch_driven)
    candidates_driven = list(all_possible - stitch_driven)
    temp = T_INIT
    history_driven = []
    history_random = []
    for step in range(STEPS):
        # 租金驱动重连
        if stitch_driven and candidates_driven:
            old = random.choice(list(stitch_driven))
            new = random.choice(candidates_driven)
            old_var, _ = compute_variance(stitch_driven)
            stitch_driven.remove(old)
            stitch_driven.add(new)
            new_var, _ = compute_variance(stitch_driven)
            delta = new_var - old_var
            if delta <= 0 or random.random() < np.exp(-delta / max(temp, 1e-6)):
                candidates_driven.remove(new)
                candidates_driven.append(old)
            else:
                stitch_driven.remove(new)
                stitch_driven.add(old)
        # 纯随机重连
        if stitch_random:
            old = random.choice(list(stitch_random))
            new = random.choice(candidates_pool)
            while new in stitch_random:
                new = random.choice(candidates_pool)
            stitch_random.remove(old)
            stitch_random.add(new)
        temp = max(temp * COOLING_RATE, T_MIN)
        if step % RECORD_INTERVAL == 0:
            var_d, _ = compute_variance(stitch_driven)
            var_r, _ = compute_variance(stitch_random)
            history_driven.append(var_d)
            history_random.append(var_r)
    return np.array(history_driven), np.array(history_random)

if __name__ == '__main__':
    print(f"Running {NUM_TRIALS} trials in parallel...")
    with mp.Pool(processes=NUM_PROCESSES) as pool:
        results = pool.map(run_single_trial, range(NUM_TRIALS))
    all_driven = [res[0] for res in results]
    all_random = [res[1] for res in results]
    avg_driven = np.mean(all_driven, axis=0)
    avg_random = np.mean(all_random, axis=0)
    std_driven = np.std(all_driven, axis=0)
    std_random = np.std(all_random, axis=0)
    steps_record = np.arange(0, STEPS, RECORD_INTERVAL)

    # 绘图
    plt.figure(figsize=(10,5))
    plt.plot(steps_record, avg_driven, 'b-', linewidth=2, label='Rent-driven (Metropolis)')
    plt.fill_between(steps_record, avg_driven - std_driven, avg_driven + std_driven,
                     alpha=0.2, color='blue')
    plt.plot(steps_record, avg_random, 'r--', linewidth=2, label='Random rewiring')
    plt.fill_between(steps_record, avg_random - std_random, avg_random + std_random,
                     alpha=0.2, color='red')
    plt.xlabel('Rewiring steps')
    plt.ylabel('Anisotropy (variance)')
    plt.title('Emergence of Isotropy via Rent Minimization')
    plt.legend()
    plt.grid(alpha=0.3)

    # 拟合：单指数 + 常数平台
    def exp_plus_const(t, a, tau, c):
        return a * np.exp(-t / tau) + c
    try:
        # 初始猜测：振幅约为初始方差，时间常数约300步，平台约最终方差
        p0 = [180000, 300, 1.0]
        bounds = (0, [np.inf, np.inf, np.inf])  # 所有参数非负
        popt, pcov = curve_fit(exp_plus_const, steps_record, avg_driven,
                               p0=p0, bounds=bounds, maxfev=5000)
        a_fit, tau_fit, c_fit = popt
        plt.plot(steps_record, exp_plus_const(steps_record, *popt), 'k:',
                 label=f'Exp fit: τ={tau_fit:.0f}, c={c_fit:.2f}')
        plt.legend()
        # 计算拟合优度
        residuals = avg_driven - exp_plus_const(steps_record, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((avg_driven - np.mean(avg_driven))**2)
        r_squared = 1 - (ss_res / ss_tot)
        print(f"拟合结果：τ = {tau_fit:.0f} 步, 平台 c = {c_fit:.2f}, R² = {r_squared:.4f}")
    except Exception as e:
        print("拟合失败:", e)

    plt.tight_layout()
    plt.show()

    print(f"\n最终平均驱动方差: {avg_driven[-1]:.2f} (±{std_driven[-1]:.2f})")
    print(f"最终平均随机方差: {avg_random[-1]:.2f} (±{std_random[-1]:.2f})")