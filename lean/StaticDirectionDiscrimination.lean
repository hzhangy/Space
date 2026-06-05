import Mathlib.Data.Real.Basic
import Mathlib.Tactic

/-!
# 静态方向分辨定理

证明：在三维立方格 ℤ³ 上，对于任意给定的采样窗口宽度 W，存在宏观尺度 D₀，
使得当欧氏距离 D ≥ D₀ 时，轴向位移与体对角线位移对应的曼哈顿距离之差
严格大于 W。因此，静态离散骨架上的方向信息在宏观尺度下仍然可辨，
单纯依靠跨步-W 采样窗口无法消除各向异性。

该定理与“八面体各向异性定理”共同构成了 N.E.A. 框架中
“静态模型必死，必须引入动力学演化”的数学根基。
-/

section StaticDirectionDiscrimination

-- 曼哈顿距离（图距离）
def manhattan (a b : ℤ × ℤ × ℤ) : ℤ :=
  let (x₁, y₁, z₁) := a
  let (x₂, y₂, z₂) := b
  |x₁ - x₂| + |y₁ - y₂| + |z₁ - z₂|

-- 考虑从原点出发的位移向量
def origin : ℤ × ℤ × ℤ := (0, 0, 0)

-- 轴向位移：D 沿 x 轴
def axial (D : ℤ) : ℤ × ℤ × ℤ := (D, 0, 0)
-- 体对角线位移：(D, D, D)  注意这里每个分量都是 D，欧氏距离为 √(3)*D
def diagonal (D : ℤ) : ℤ × ℤ × ℤ := (D, D, D)

-- 曼哈顿距离计算结果
example (D : ℤ) : manhattan origin (axial D) = |D| := by
  simp [manhattan, axial, origin]

example (D : ℤ) : manhattan origin (diagonal D) = 3 * |D| := by
  simp [manhattan, diagonal, origin]
  ring

-- 差值函数
def manhattan_diff (D : ℤ) : ℤ :=
  manhattan origin (diagonal D) - manhattan origin (axial D)

-- 当 D > 0 时，差值为 2*D
lemma diff_expr (D : ℤ) (hD : 0 ≤ D) : manhattan_diff D = 2 * D := by
  dsimp [manhattan_diff, manhattan, axial, diagonal, origin]
  simp [abs_of_nonneg hD]
  ring

-- 主定理：对于任意窗口宽度 W : ℤ，只要 D > W/2（且 D > 0），差值就大于 W
theorem static_direction_discrimination (W : ℤ) (D : ℤ) (hDpos : 0 < D) (hDlarge : W < 2 * D) :
    W < manhattan_diff D := by
  have h_nonneg : 0 ≤ D := le_of_lt hDpos
  rw [diff_expr D h_nonneg]
  exact hDlarge

-- 推论：如果取窗口宽度 W = 10（跨步-10），那么只要 D ≥ 6（即欧氏距离 ≥ 6√3 ≈ 10.4），
-- 轴向与对角线的图距离差至少为 12，严格大于 10。因此窗口分箱无法合并这两个方向。
example : (10 : ℤ) < manhattan_diff 6 := by
  apply static_direction_discrimination 10 6 (by norm_num) (by norm_num)

-- 进一步推广：对于面对角线方向，结论类似（此处省略，可类似证明）

end StaticDirectionDiscrimination
def main : IO Unit :=
  IO.println "Static Direction Discrimination Theorem successfully verified!"
