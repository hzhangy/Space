import numpy as np
from itertools import combinations

def random_su3_element():
    """生成一个随机的 su(3) 元素（反厄米、无迹）"""
    # 用 Gell-Mann 矩阵的线性组合来生成
    # 但更简单：生成任意矩阵，投影到 su(3)
    M = np.random.randn(3, 3) + 1j * np.random.randn(3, 3)
    # 反厄米化：X = A - A^H，此时迹为纯虚数
    X = M - M.conj().T
    # 减去 (trace(X)/3) * I 以强制无迹
    X = X - np.trace(X) / 3 * np.eye(3)
    # 确保反厄米性不受破坏（以上操作仍保持）
    # 除以范数使其数值稳定
    X = X / np.linalg.norm(X)
    return X

def algebraic_closure_rank(initial_matrices, max_iter=100, tol=1e-10):
    """
    从初始矩阵列表开始，通过对易子扩展代数，返回最终的基（实向量空间）和维数。
    所有矩阵都应该是反厄米，我们存储为复数矩阵但作为实向量空间（基的实系数组合）。
    因为反厄米矩阵的实线性组合仍然是反厄米；实维数等于复矩阵独立参数个数。
    我们通过将矩阵展平为实部和虚部拼接的向量，再计算秩。
    """
    # 将每个矩阵转换为 18 维实向量 (9个位置的实部 + 9个虚部)
    def matrix_to_real_vector(M):
        return np.concatenate([M.real.flatten(), M.imag.flatten()])
    
    basis_vectors = []
    # 初始基
    for M in initial_matrices:
        v = matrix_to_real_vector(M)
        basis_vectors.append(v)
    
    # 正交化得到当前基
    def orthonormalize(vectors, tol):
        if not vectors:
            return []
        A = np.array(vectors)
        Q, _ = np.linalg.qr(A.T)
        # Q 的列是正交基，但由于 QR 分解可能包含符号和顺序变化，
        # 我们直接取非零奇异值对应的基
        # 更简单：使用 SVD 获取秩和正交基
        U, s, Vh = np.linalg.svd(A, full_matrices=False)
        rank = np.sum(s > tol)
        return Vh[:rank]  # 返回行向量作为基
    
    # 当前基的矩阵表示（复数）
    def vectors_to_matrices(vectors):
        mats = []
        for v in vectors:
            real_part = v[:9].reshape(3,3)
            imag_part = v[9:].reshape(3,3)
            mats.append(real_part + 1j*imag_part)
        return mats
    
    current_basis = orthonormalize(basis_vectors, tol)
    current_mats = vectors_to_matrices(current_basis)
    
    for iteration in range(max_iter):
        new_vectors = []
        # 计算所有对的李括号
        for X, Y in combinations(current_mats, 2):
            Z = X @ Y - Y @ X
            # Z 仍然是反厄米（李代数封闭），因为 X,Y 反厄米 => [X,Y] 反厄米
            # 并且迹为零
            z_vec = matrix_to_real_vector(Z)
            new_vectors.append(z_vec)
        
        # 也将这些新向量与当前基合并
        all_vectors = [matrix_to_real_vector(M) for M in current_mats] + new_vectors
        new_basis = orthonormalize(all_vectors, tol)
        new_mats = vectors_to_matrices(new_basis)
        
        if len(new_basis) == len(current_basis):
            # 没有新的线性无关向量，闭包达到
            break
        current_basis = new_basis
        current_mats = new_mats
    else:
        print("Warning: Max iterations reached without convergence.")
    
    rank = len(current_basis)
    return rank

def run_experiment(num_trials=10000):
    success = 0
    for i in range(num_trials):
        # 生成三个随机的 su(3) 元素作为初始生成元
        gens = [random_su3_element() for _ in range(3)]
        rank = algebraic_closure_rank(gens)
        if rank == 8:
            success += 1
        else:
            print(f"Trial {i}: rank = {rank} (unexpected)")
    print(f"Success rate: {success}/{num_trials}")

if __name__ == "__main__":
    run_experiment(5000)  # 运行 5000 次足够