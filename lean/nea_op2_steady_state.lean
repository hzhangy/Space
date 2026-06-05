import Mathlib.Data.Real.Basic
import Mathlib.Tactic

/-!
# N.E.A. OP2 稳态对账证明 (终极兼容版 v3)
解决点：
1. 修复了 List.Perm.sum_map_eq 的识别问题，改用更底层的 map_sum 逻辑。
2. 强化了对 u 的构造审计，确保代数步进透明。
3. 闭合了 0.5 + 0.5 = 1.0 的实数域结算。
-/

noncomputable section

-- 1. 定义基本单元
inductive Cell | K4 | C8
  deriving DecidableEq, Repr

-- 2. 定义寻址租金 (ZY)
def rent : Cell → ℝ
  | Cell.K4 => 1
  | Cell.C8 => 1/2

-- 3. 定义总指标
def totalRent (t : List Cell) : ℝ := (t.map rent).sum

def IsStable (t : List Cell) (supply : ℝ) : Prop :=
  totalRent t = supply ∧ ∀ u : List Cell, totalRent u = supply → u.length ≤ t.length

-- ============================================================
-- 核心定理：稳态中不含 K4
-- ============================================================

theorem OP2_C8_dominance (t : List Cell) (supply : ℝ) (h_stable : IsStable t supply) :
  Cell.K4 ∉ t := by
  -- 开启反证审计：假设存在 K4
  intro h_mem

  -- 构造：注销 1个 K4，平替增发 2个 C8
  let u := t.erase Cell.K4 ++ [Cell.C8, Cell.C8]

  -- 1. 证明租金守恒 (能量平账)
  have h_rent_u : totalRent u = supply := by
    unfold totalRent
    dsimp [u]
    -- 展开列表操作：map(A ++ B).sum = map(A).sum + map(B).sum
    rw [List.map_append, List.sum_append]
    -- 计算 [C8, C8] 的租金
    simp [rent]
    -- 获取资产：(t.map rent).sum = supply
    have h_t := h_stable.left
    unfold totalRent at h_t
    -- 核心逻辑：利用置换原理证明 sum(map t) = 1 + sum(map (t.erase K4))
    -- 使用更底层的 List.Perm.sum_eq 配合 List.Perm.map
    let p := List.perm_cons_erase h_mem -- t ~ K4 :: (t.erase K4)
    let p_map := p.map rent             -- map(t) ~ map(K4 :: (t.erase K4))
    have h_sum_eq := p_map.sum_eq       -- sum(map(t)) = sum(map(K4 :: (t.erase K4)))
    rw [h_sum_eq] at h_t
    -- 此时 h_t : (rent K4 + (map rent (t.erase K4)).sum) = supply
    simp [rent] at h_t
    -- 最终代数消元
    linarith

  -- 2. 证明容量增加 (寻址套利)
  have h_len_u : u.length = t.length + 1 := by
    dsimp [u]
    rw [List.length_append]
    -- 资产：t 含有元素，所以长度 > 0
    have h_pos : 0 < t.length := List.length_pos_of_mem h_mem
    -- 凭证：抹除一个元素，长度减 1
    rw [List.length_erase_of_mem h_mem]
    -- 2个 C8 长度是 2
    simp
    -- 结算：(n-1) + 2 = n + 1
    omega

  -- 3. 最终矛盾清算
  -- 根据稳态定义，u 的长度不能超过 t
  have h_max := h_stable.right u h_rent_u
  rw [h_len_u] at h_max
  -- 结论：t + 1 ≤ t 产生逻辑坏账，产生矛盾
  omega

-- 审计完成签名
#check OP2_C8_dominance

end

def main : IO Unit :=
  pure ()
