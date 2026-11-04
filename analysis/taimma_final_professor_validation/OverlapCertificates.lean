import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Ring

/- New audit certificates only. No frozen theorem or model outcome is changed.
   Named propositions preserve the exact binders/types/bodies of the five
   flagged pairs. Compiler success and axiom reports do not establish benchmark
   independence, contamination absence or human mathematical adjudication. -/
namespace ProfessorOverlapAudit

def D06 : Prop := ∀ (a b : Nat), (a+b)^2 = a^2 + 2*a*b + b^2
def T11 : Prop := ∀ (x y : Nat), (x+y)*(x+y)=x*x+2*x*y+y*y
def T12 : Prop := ∀ (x y : Nat), (x+y)^2=x^2+2*x*y+y^2
def D07 : Prop := ∀ (a b : Nat), a*(b+1)=a*b+a
def T13 : Prop := ∀ (x y z : Nat), x*(y+z)=x*y+x*z
def T07 : Prop := ∀ (a b : Nat), Nat.succ (a+b) = Nat.succ a+b
def T08 : Prop := ∀ (a b : Nat), a + Nat.succ b = Nat.succ (a + b)

-- Definitional equality after alpha-renaming binders and ignoring whitespace.
theorem d06_t12_definitional : D06 = T12 := rfl

-- Explicit proof transport via the square-to-multiplication identity.
theorem d06_to_t11 (h : D06) : T11 := by
  intro x y
  simpa only [pow_two] using h x y

theorem t11_to_t12 (h : T11) : T12 := by
  intro x y
  simpa only [pow_two] using h x y

theorem t12_to_t11 (h : T12) : T11 := by
  intro x y
  simpa only [pow_two] using h x y

-- A forward specialization certificate; no converse/generalization is asserted.
theorem t13_specializes_to_d07 (h : T13) : D07 := by
  intro a b
  simpa only [Nat.mul_one] using h a b 1

-- Propositions have different syntax; transport uses commutativity explicitly.
theorem t07_to_t08 (h : T07) : T08 := by
  intro a b
  calc
    a + Nat.succ b = Nat.succ b + a := Nat.add_comm _ _
    _ = Nat.succ (b + a) := (h b a).symm
    _ = Nat.succ (a + b) := congrArg Nat.succ (Nat.add_comm b a)

theorem t08_to_t07 (h : T08) : T07 := by
  intro a b
  calc
    Nat.succ (a + b) = Nat.succ (b + a) := congrArg Nat.succ (Nat.add_comm a b)
    _ = b + Nat.succ a := (h b a).symm
    _ = Nat.succ a + b := Nat.add_comm _ _

#print axioms d06_t12_definitional
#print axioms d06_to_t11
#print axioms t11_to_t12
#print axioms t12_to_t11
#print axioms t13_specializes_to_d07
#print axioms t07_to_t08
#print axioms t08_to_t07
end ProfessorOverlapAudit
