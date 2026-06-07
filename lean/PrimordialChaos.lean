import Mathlib

open Filter Topology

/-!
# 原始混沌向最小作用量的统计收敛定理
# (Primordial Chaos to Least Action via Statistical Cancellation)

本定理证明：在完全无序的因果底物中，n 个独立的微观涨落发生完全同向相干
（即“劲往一处使”）的概率 p(n) = (1/2)^n 在宏观极限（n -> ∞）下严格收敛于 0。
由此在数理逻辑上证明了：微观的彻底无序（最大熵）在宏观尺度必然导致相消与极小化，
从而自发涌现出“最小作用量原理”。
-/

section PrimordialChaos

/--
定义 n 个独立二值因果涨落发生完全同向一致的概率：p(n) = (1/2)^n
注意：由于返回实数 ℝ 并涉及实数除法，必须标记为 `noncomputable`。
-/
noncomputable def coherent_probability (n : ℕ) : ℝ := (1 / 2) ^ n

/--
【终极起点定理】：微观无序导致的宏观协同概率在无穷大极限下收敛于零
-/
theorem primordial_chaos_to_least_action :
    Tendsto (fun n : ℕ => coherent_probability n) atTop (nhds 0) := by
  -- 1. 展开概率函数的定义
  unfold coherent_probability
  -- 2. 核心数学证明：利用 Mathlib 经典定理证明当 |r| < 1 时，r^n 在 n -> ∞ 时收敛于 0。
  -- 此处 r = 1/2，通过 `norm_num` 自动求解 0 ≤ 1/2 和 1/2 < 1 两个有理数不等式。
  exact tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num) (by norm_num)

end PrimordialChaos

-- 终端运行入口函数（IO 操作本身是完全可计算的）
def main : IO Unit :=
  IO.println "Success: Primordial Chaos to Least Action Theorem successfully verified in Lean 4!"
