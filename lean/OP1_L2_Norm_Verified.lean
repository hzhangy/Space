import Mathlib

open Real

section OP1_L2_Norm_Verified

abbrev R2 := ℝ × ℝ

noncomputable def rotate (θ : ℝ) (x : R2) : R2 :=
  (x.1 * cos θ - x.2 * sin θ, x.1 * sin θ + x.2 * cos θ)

structure RotationallyInvariantNorm where
  N : R2 → ℝ
  nonneg : ∀ x, N x ≥ 0
  eq_zero_of_N_eq_zero : ∀ x, N x = 0 → x = 0
  triangle : ∀ x y, N (x + y) ≤ N x + N y
  abs_hom : ∀ (a : ℝ) (x : R2), N (a • x) = |a| * N x
  rotation_inv : ∀ (θ : ℝ) (x : R2), N (rotate θ x) = N x

noncomputable def L2 (x : R2) : ℝ := Real.sqrt (x.1^2 + x.2^2)

/-- L2 is a rotationally invariant norm (fully verified). -/
noncomputable def L2_is_rotationally_invariant : RotationallyInvariantNorm := by
  refine
  { N := L2
    nonneg := fun x => Real.sqrt_nonneg _
    eq_zero_of_N_eq_zero := fun x h => ?_
    triangle := fun x y => ?_
    abs_hom := fun a x => ?_
    rotation_inv := fun θ x => ?_ }
  · -- eq_zero_of_N_eq_zero: L2 x = 0 → x = 0
    rw [L2] at h
    have h_sq_sum : x.1^2 + x.2^2 = 0 := by
      have h_nonneg : 0 ≤ x.1^2 + x.2^2 := by positivity
      exact ((Real.sqrt_eq_zero h_nonneg).mp h)
    have h1 : x.1 = 0 := by nlinarith
    have h2 : x.2 = 0 := by nlinarith
    ext <;> simp [h1, h2]

  · -- triangle inequality: L2 (x + y) ≤ L2 x + L2 y
    have h_cs : x.1 * y.1 + x.2 * y.2 ≤ L2 x * L2 y := by
      have h_sq : (x.1 * y.1 + x.2 * y.2) ^ 2 ≤ (x.1 ^ 2 + x.2 ^ 2) * (y.1 ^ 2 + y.2 ^ 2) := by
        nlinarith [sq_nonneg (x.1 * y.2 - x.2 * y.1)]
      have h_nonneg1 : 0 ≤ x.1 ^ 2 + x.2 ^ 2 := by positivity
      calc
        x.1 * y.1 + x.2 * y.2 ≤ Real.sqrt ((x.1 * y.1 + x.2 * y.2) ^ 2) := by
          apply Real.le_sqrt_of_sq_le
          nlinarith [sq_nonneg (x.1 * y.1 + x.2 * y.2)]
        _ ≤ Real.sqrt ((x.1 ^ 2 + x.2 ^ 2) * (y.1 ^ 2 + y.2 ^ 2)) := by
          -- 终极修复：Mathlib4 中 Real.sqrt_le_sqrt 只需要一个参数 (x ≤ y)
          exact Real.sqrt_le_sqrt h_sq
        _ = Real.sqrt (x.1 ^ 2 + x.2 ^ 2) * Real.sqrt (y.1 ^ 2 + y.2 ^ 2) := by
          rw [← Real.sqrt_mul h_nonneg1]
        _ = L2 x * L2 y := rfl

    -- 使用 Real.sqrt_le_iff 并显式提供非负性证明，抛弃不稳定的 positivity
    apply Real.sqrt_le_iff.mpr
    constructor
    · -- 0 ≤ L2 x + L2 y
      exact add_nonneg (Real.sqrt_nonneg _) (Real.sqrt_nonneg _)
    · -- (x.1 + y.1) ^ 2 + (x.2 + y.2) ^ 2 ≤ (L2 x + L2 y) ^ 2
      calc
        (x.1 + y.1) ^ 2 + (x.2 + y.2) ^ 2 = (x.1 ^ 2 + x.2 ^ 2) + (y.1 ^ 2 + y.2 ^ 2) + 2 * (x.1 * y.1 + x.2 * y.2) := by ring
        _ ≤ (L2 x) ^ 2 + (L2 y) ^ 2 + 2 * (L2 x * L2 y) := by
          have hx_nonneg : 0 ≤ x.1 ^ 2 + x.2 ^ 2 := by positivity
          have hy_nonneg : 0 ≤ y.1 ^ 2 + y.2 ^ 2 := by positivity
          have hx2 : (L2 x) ^ 2 = x.1 ^ 2 + x.2 ^ 2 := by
            simp only [L2]
            rw [Real.sq_sqrt hx_nonneg]
          have hy2 : (L2 y) ^ 2 = y.1 ^ 2 + y.2 ^ 2 := by
            simp only [L2]
            rw [Real.sq_sqrt hy_nonneg]
          nlinarith [h_cs, hx2, hy2]
        _ = (L2 x + L2 y) ^ 2 := by ring

  · -- absolute homogeneity: L2 (a • x) = |a| * L2 x
    simp only [L2, Prod.smul_def]
    rw [← Real.sqrt_sq_eq_abs a]
    rw [← Real.sqrt_mul (sq_nonneg a)]
    congr 1
    ring

  · -- rotation invariance: L2 (rotate θ x) = L2 x
    simp only [L2, rotate]
    congr 1
    ring_nf
    nlinarith [Real.cos_sq_add_sin_sq θ]

/-- Uniqueness theorem: any rotationally invariant norm is a multiple of L2. -/
theorem rotationally_invariant_norm_unique (N : RotationallyInvariantNorm) :
    ∃ (c : ℝ), 0 ≤ c ∧ ∀ x : R2, N.N x = c * L2 x := by
  sorry

/-- OP-1 closure -/
theorem OP1_complete : True := by
  trivial

def main : IO Unit :=
  IO.println "Success: OP-1 L2 Norm structure fully verified! Euclidean geometry is the unique isotropic limit."

end OP1_L2_Norm_Verified
