import numpy as np
from itertools import combinations

def random_su2_element():
    """生成一个随机的 su(2) 元素（反厄米、无迹）"""
    M = np.random.randn(2, 2) + 1j * np.random.randn(2, 2)
    X = M - M.conj().T                    # 反厄米化
    X = X - np.trace(X) / 2 * np.eye(2)  # 强制无迹
    X = X / np.linalg.norm(X)             # 归一化
    return X

def algebraic_closure_rank(initial_matrices, max_iter=100, tol=1e-10):
    """从初始矩阵列表开始，通过对易子扩展代数，返回实维数"""
    def matrix_to_real_vector(M):
        return np.concatenate([M.real.flatten(), M.imag.flatten()])
    
    # 初始基
    vecs = [matrix_to_real_vector(M) for M in initial_matrices]
    A = np.array(vecs)                    # 行向量矩阵
    U, s, Vh = np.linalg.svd(A, full_matrices=False)
    rank = np.sum(s > tol)
    current_basis = Vh[:rank]             # 右奇异向量作为标准正交基，每行长度 = 8
    
    for _ in range(max_iter):
        # 将基向量恢复为复矩阵
        mats = []
        for v in current_basis:
            real = v[:4].reshape(2,2)
            imag = v[4:8].reshape(2,2)
            mats.append(real + 1j*imag)
        
        # 计算所有对的李括号
        new_vecs = []
        for X, Y in combinations(mats, 2):
            Z = X @ Y - Y @ X
            new_vecs.append(matrix_to_real_vector(Z))
        
        # 合并原基与新向量，重新正交化
        all_vectors = np.vstack([current_basis, new_vecs])
        U, s, Vh = np.linalg.svd(all_vectors, full_matrices=False)
        new_rank = np.sum(s > tol)
        if new_rank == rank:
            break
        rank = new_rank
        current_basis = Vh[:new_rank]
    return rank

def run_su2_trials(num=5000):
    success = 0
    for i in range(num):
        gens = [random_su2_element() for _ in range(3)]
        r = algebraic_closure_rank(gens)
        if r == 3:
            success += 1
        else:
            print(f"Trial {i}: rank = {r}")
    print(f"SU(2) closure rank = 3: {success}/{num}")

if __name__ == "__main__":
    run_su2_trials(5000)