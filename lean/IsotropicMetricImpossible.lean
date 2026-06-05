import Mathlib.Data.Real.Basic
import Mathlib.Tactic

/-!
# 各向同性度规不可能定理

证明：在三维立方格 ℤ³ 上，不存在函数 g : ℝ → ℝ，
使得对于所有格点 p, q : ℤ × ℤ × ℤ，曼哈顿距离 d₁(p,q) = g(d₂(p,q))，
其中 d₂ 是欧几里得距离。

该定理干净利落地终结了“静态离散空间能通过某种各向同性连续函数
涌现出各向同性宏观几何”的可能性。它与“八面体各向异性定理”
和“静态方向分辨定理”共同构成 N.E.A. 框架中“静态模型必死”的
形式化数学根基。
-/

section IsotropicMetricImpossible

-- 曼哈顿距离（L¹ 范数）
def manhattan (p q : ℤ × ℤ × ℤ) : ℤ :=
  let (x₁, y₁, z₁) := p
  let (x₂, y₂, z₂) := q
  |x₁ - x₂| + |y₁ - y₂| + |z₁ - z₂|

-- 欧几里得距离平方（避免开方，仅比较平方值）
def euclideanSq (p q : ℤ × ℤ × ℤ) : ℤ :=
  let (x₁, y₁, z₁) := p
  let (x₂, y₂, z₂) := q
  (x₁ - x₂)^2 + (y₁ - y₂)^2 + (z₁ - z₂)^2

-- 原点
def origin : ℤ × ℤ × ℤ := (0, 0, 0)

-- 关键反例：p = (7,4,1)，q = (5,5,4)
def p : ℤ × ℤ × ℤ := (7, 4, 1)
def q : ℤ × ℤ × ℤ := (5, 5, 4)

-- 它们的欧氏距离平方相等
example : euclideanSq origin p = euclideanSq origin q := by
  unfold euclideanSq origin p q
  norm_num

-- 但它们的曼哈顿距离不同
example : manhattan origin p ≠ manhattan origin q := by
  unfold manhattan origin p q
  norm_num

-- 主定理：不存在各向同性度规函数
theorem no_isotropic_metric :
  ¬ ∃ (g : ℝ → ℝ), ∀ (x y : ℤ × ℤ × ℤ), (manhattan x y : ℝ) = g (Real.sqrt (euclideanSq x y)) := by
  rintro ⟨g, h⟩
  have hpq_sq_eq : euclideanSq origin p = euclideanSq origin q := by
    unfold euclideanSq origin p q; norm_num
  have h_dist_eq : Real.sqrt (euclideanSq origin p) = Real.sqrt (euclideanSq origin q) := by
    rw [hpq_sq_eq]
  have hp_eq := h origin p
  have hq_eq := h origin q
  -- 从 h 得到曼哈顿距离等于 g(√…)
  have hp_val : (manhattan origin p : ℝ) = g (Real.sqrt (euclideanSq origin p)) := hp_eq
  have hq_val : (manhattan origin q : ℝ) = g (Real.sqrt (euclideanSq origin q)) := hq_eq
  rw [h_dist_eq] at hp_val
  -- 现在 hp_val 和 hq_val 的右侧相同，所以左侧应相等
  have h_contra : (manhattan origin p : ℝ) = (manhattan origin q : ℝ) := by
    rw [hp_val, hq_val]
  -- 但左侧实际不相等
  have h_diff : (manhattan origin p : ℤ) ≠ (manhattan origin q : ℤ) := by
    unfold manhattan origin p q; norm_num
  -- 转化为 ℝ 上的不相等
  apply h_diff
  exact_mod_cast h_contra

end IsotropicMetricImpossible
def main : IO Unit :=
  IO.println "Isotropic Metric Impossibility Theorem successfully verified!"
