import numpy as np

def random_u1_element():
    """生成一个随机的 u(1) 元素（纯虚数）"""
    # 1×1 矩阵，即复数 i*a，其中 a 是随机实数
    return 1j * np.random.randn(1, 1)

def u1_closure_rank(gens, tol=1e-10):
    """
    对于 U(1)，李括号恒为零，所以闭包秩就是 gens 作为实向量空间的秩。
    每个 u(1) 元素是纯虚数，其实部恒为零，所以实向量空间维数最大为 1。
    """
    # 将每个矩阵展平为实向量（只有1个复数，实部0，虚部为其系数）
    vectors = [np.array([[g.imag.item()]]) for g in gens]  # 1维向量
    A = np.array(vectors).reshape(len(gens), 1)
    U, s, _ = np.linalg.svd(A, full_matrices=False)
    rank = np.sum(s > tol)
    return rank

def run_u1_trials(num=5000):
    success = 0
    for i in range(num):
        gens = [random_u1_element() for _ in range(2)]  # 取两个随机生成元
        r = u1_closure_rank(gens)
        if r == 1:   # 期望秩为1（只要生成元不都为零）
            success += 1
        else:
            print(f"Trial {i}: rank = {r}")
    print(f"U(1) closure rank = 1: {success}/{num}")

if __name__ == "__main__":
    run_u1_trials(5000)