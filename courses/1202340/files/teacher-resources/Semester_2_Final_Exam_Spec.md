# Semester 2 Final Exam — Specification (Teacher-Facing)

**Course:** Precalculus Honors (Florida 1202340) · Optima Academy Online
**Placement:** Week 36 (Semester 2 Finals Week), the week's third and culminating item (after the review lesson and review activity).
**Implementation:** Hand-built in Canvas from this spec. This document is teacher-facing only — standards codes appear here and must **never** appear on the student-facing exam.

---

## 1. Purpose and format

The Semester 2 final is the course's capstone act of intellectual honesty: one cumulative, hand-written assessment across Units 6–10, sat in a single quiet block, that asks the student to recognize which of the plane's five languages — rectangular, polar, parametric, complex, and vector — a problem wants, without a unit label attached, and to run a full year's standing disciplines unprompted. Where the Semester 1 final closed the loop on functions and conics, this final closes the loop on the whole course: the virtue arc it caps runs Responsibility (U6) → Self-government (U7) → Wonder (U8) → Courage (U9) → Service (U10), and the final itself asks for one more virtue beneath all of them — the same intellectual honesty every unit test has asked for all year.

| Parameter | Decision |
|---|---|
| Coverage | Cumulative, Units 6–10, weighted per §3 |
| Sitting | One sitting, target length **~2 hours** (Part A ≈ 50 min, Part B ≈ 45 min, Part C ≈ 25 min) |
| Mode | Hand-written on paper → photograph/scan → **one PDF upload** (course standard) |
| Tools | Calculator for **arithmetic and inverse-trigonometric evaluation only** (evaluating a trig ratio, reading an angle off the calculator's inverse sine/cosine/tangent key, evaluating a decimal or root as a number); no notes, no lesson pages, no classmates, no AI tools, no solution sites |
| Honor pledge | Signed at the top of page 1: *"I completed this exam on my own, without help from people, notes, or AI tools."* — identical wording to the unit tests and the Semester 1 final |
| Structure | **Part A — Fluency** (7 items) · **Part B — Reasoning** (4 items, written as arguments) · **Part C — Synthesis** (2 items, cross-unit) |
| Grading | Standing 4-criterion rubric, 15 pts per criterion (§6) |

## 2. Point value: 60 pts

**60 pts = the standing 4-criterion rubric × 15 pts per criterion.** The scale is deliberate relative to the 40-pt unit tests (4 × 10): the final spans five units and a two-hour sitting rather than one unit and ninety minutes, so it carries 1.5× a unit test's weight — heavy enough to be the semester's capstone, light enough that no single sitting can swamp a semester of weekly work (this semester's five unit tests alone total 200 pts against the final's 60). The rubric criteria and their meanings are unchanged; only the per-criterion scale grows, so students meet exactly the standard they have met ten times before — five times this semester alone.

## 3. Blueprint — composition by unit weight

Weights per the approved assessment plan (`02_Design/plan.md` §5): **U6 20% · U7 30% · U8 15% · U9 10% · U10 25%.**

A straight proportional split of 13 items (7A + 4B + 2C) across these weights would give U6 ≈ 2.6, U7 ≈ 3.9, U8 ≈ 1.95, U9 ≈ 1.3, U10 ≈ 3.25 items — rounding to **U6: 2, U7: 3–4, U8: 1–2, U9: light/shared, U10: 2–3**, which is what the table below builds. U7's 30% share is honored by giving it *three* of the seven Part A slots (no other unit gets more than two) plus a dedicated Part B item and the lead share of Part C's synthesis lineage. U9's 10% share is honored differently than a flat item-count would suggest: rather than a dedicated Part A slot, U9 supplies the connective tissue of the capstone Part C item (C2) and a light alternate inside Part B — proportionally smaller, but not absent, exactly as U1 (15%) carried no full Part A item of its own on the Semester 1 final.

| Unit | Weight | Part A (fluency) | Part B (reasoning) | Part C (synthesis) | Approx. share |
|---|---|---|---|---|---|
| U6 Right Triangle Trig | 20% | A1 (unit-circle & six-function fluency), A2 (arc length/sector + right-triangle solve) | share of B1 (derivation choice: 30-60-90 seeds) | C1 lead-in (ramp/inverse-trig thread) | ~20% |
| U7 Trig Functions | 30% | A3 (transformation + reciprocal graph), A4 (Law of Sines & Cosines + area), A5 (inverse trig + Pythagorean + sum-formula) | share of B1 (double-angle→reduction derivation option); B2 (ambiguous case, primary) | C1 (general-solution/odd-even thread, primary) | ~30% |
| U8 Polar & Parametric | 15% | A6 (polar↔rectangular conversion + curve classification) | share of B3 (limaçon classify-and-justify option) | contributes the polar-circle language to C2 | ~15% |
| U9 Complex Numbers | 10% | — (folded into C2 as primary content) | share of B3 (complex-conjugate-pair argument option) | C2 (primary vehicle: trigonometric form, rotation, product rule) | ~10% |
| U10 Vectors | 25% | A7 (vector fluency bundle: components/magnitude/direction, scalar multiplication, unit vector, dot product) | B4 (wind-and-current *or* Law-of-Cosines→dot-product derivation) | C2 anchor (fresh scenario opens here) | ~25% |

Item count: **13** (7 A + 4 B + 2 C). Parts A/B draw primarily from the unit-test pools (§4); Part C uses the fresh synthesis items (§5). When assembling, keep every number exact-friendly (the pools and fresh items below are all hand/Python-verified) and never label items by unit — recognizing which of the five languages a problem speaks is part of the assessment.

## 4. Item pools — unit-test items to adapt

Adapt = change the numbers/context while preserving the structure and the discipline being tested; the unit tests were written to seed this pool. Citations are by part/number from the five built unit tests (`03_Develop/unit-0N-*/unit-test.html`), verified by direct reading of each file.

### Unit 6 — Right Triangle Trigonometry (T.1.8, T.2.1–2.5) — 20%
- **Part A pool:** U6 test A1 (315°/5π/3 degree–radian conversion), A2 (coterminal angle for −750°, then radians, then arc length/sector area for r=9, θ=2π/3), A3 (right triangle: leg 14, angle 38°, solve + Pythagorean verification), A4 (5π/3 unit-circle special values, quadrant/reference-angle stated), A5 (all six functions at 120°, sign pattern stated first), A6 (sec 250° to four decimals, technology-checked against a predicted sign), A7 (sinθ=0.6 in QII, cosθ and tanθ via the Pythagorean identity, not the calculator), A8 (40 m baseline, 55° elevation, building height).
- **Part B pool:** U6 test B9 (derive the 30-60-90 seed values from an equilateral triangle's altitude — the primary B1 derivation-choice option), B10 (two-station field problem: 42°/24° elevation angles, 35 m apart, solved as a system and cross-verified).
- **Part C seed:** U6 test C11 (ADA ramp, tanθ=1/12, widened to a second periodic solution, connected explicitly to Unit 4's one-to-one/horizontal-line-test criterion) — feeds the C1 lineage below.

### Unit 7 — Trigonometric Functions (T.3.1–3.3, T.1.3–1.7) — 30%
- **Part A pool:** U7 test A1 (amplitude/period/midline/phase shift for 3cos(2(x−π/4))−1, evaluated at x=π/4), A2 (period and nearest asymptotes for sec(3x)), A3 (arcsin(−1/2), arccos(−√3/2), ranges stated), A4 (2sinθ−1=0 on [0,2π)), A5 (Law of Sines: A=40°, B=75°, a=12), A6 (Law of Cosines + area: a=8, b=10, C=50°), A7 (cosθ=−5/13 in QIII, Pythagorean identity), A8 (cos 75° via a sum/difference decomposition).
- **Part B pool:** U7 test B9 (derive cos2θ=cos²θ−sin²θ from the sum formula, then the reduction formula sin²θ=(1−cos2θ)/2 — the primary B1 derivation-choice alternate), B10 (the ambiguous case fully resolved: a=15, b=20, A=35°, all valid triangles found — the primary B2 template).
- **Part C seed:** U7 test C11 (sinθ=0.6 general solution family, calculator's returned value identified as one member, connected explicitly to Unit 4's one-to-one/horizontal-line-test criterion, plus the odd/cosine-even symmetry closer) — the second link in the C1 lineage.

### Unit 8 — Polar Coordinates & Parametric Equations (T.4.1–4.7) — 15%
- **Part A pool:** U8 test A1 (point conversion both directions: (3, 2π/3) and (−2, 2√3)), A2 (negative-r point (−2, π/4)), A3 (equation conversion both directions: x²+y²=6y and r=4cosθ), A4 (cardioid r=2−2sinθ: max r, pole angle, axis of symmetry), A5 (limaçon classification for r=4+2cosθ via the ratio test), A6 (lemniscate r²=9sin(2θ): petal count, reality condition), A7 (rose curve r=2cos(3θ): petal count and parity reasoning), A8 (parametric x=2t+1, y=t²−3: table, direction of motion, elimination).
- **Part B pool:** U8 test B9 (limaçon r=3+2sinθ classified and justified from four computed points — a primary B3 option), B10 (projectile parametric model x=20t, y=15t−4.9t²: eliminate the parameter, find range two ways, explain why the rectangular equation alone cannot answer "when").
- **Part C seed:** U8 test C11 (limaçon r=1+2sinθ, poles found by the *exact* general-solution-then-restrict method from Lesson 7-8, then connected back to that lesson's technique) — this item is the model for how Part C1 below reuses a Unit 7 technique inside Unit 8's content, and its "same machinery, new uniform" framing is the direct ancestor of the fresh C2 item.

### Unit 9 — Complex Numbers (NSO.2.2–2.6) — 10%
- **Part A pool:** U9 test A1 (arithmetic on 3−2i and −1+5i), A2 (plot 4−3i, distance from origin), A3 (distance/midpoint between 1+2i and 5−i), A4 (rectangular-to-trigonometric for 3+3i√3), A5 (trigonometric-to-rectangular for 5cis210°), A6 (product and quotient of 3cis40° and 2cis110° — the product/quotient rule this final's C2 item reuses), A7 (De Moivre power: (1+i)⁸), A8 (De Moivre roots: both square roots of 2+2i√3).
- **Part B pool:** U9 test B9 (x²+4x+13=0: complex conjugate solutions plotted, moduli found, conjugate-pair argument made — a light B3 alternate), B10 (all four fourth roots of −16, verified, shown to form a square, real-vs-complex root existence explained).
- **Part C seed:** U9 test C11 (z=−5−5i converted to trigonometric form using Unit 8's own rectangular-to-polar machinery, with the tanθ=1 quadrant trap named explicitly) — this is the direct model for the fresh C2 item's "same object, different uniform" move, now run in the opposite direction (vector → complex).

### Unit 10 — Vectors (NSO.3.1–3.4, 3.6–3.9) — 25%
- **Part A pool:** U10 test A1 (component form, magnitude, direction angle for A(2,−1) to B(7,11)), A2 (tip-to-tail sketch plus algebraic addition/subtraction for u=⟨−3,7⟩, v=⟨5,−2⟩), A3 (resultant from magnitudes/directions: 8 lb at 0°, 6 lb at 90°), A4 (scalar multiplication 3v and −2v for v=⟨−4,9⟩), A5 (unit vector in the direction of w=⟨−8,15⟩), A6 (form conversion for v=⟨−5√3,−5⟩), A7 (dot product and orthogonality test for p=⟨6,−2⟩, q=⟨1,3⟩), A8 (vector projection of a=⟨8,1⟩ onto b=⟨4,3⟩).
- **Part B pool:** U10 test B9 (24 mph engine due east, 7 mph current due south — resultant ground velocity, speed, direction, and the "why not just add the speeds" argument), B10 (deriving u·v=|u||v|cosθ from the Law of Cosines and the algebraic expansion of (u−v)·(u−v) — a genuine derivation, parallel in spirit to U6's and U7's Part B derivations).
- **Part C seed:** U10 test C11 (v=⟨−3,3√3⟩ converted to vector trigonometric form, then re-expressed as the complex number −3+3√3i in trigonometric form, verified both ways, and named explicitly as "the same underlying object wearing two different uniforms") — this is the closest existing ancestor of the fresh C2 item, which escalates the same move into a full force-rotation scenario.

## 5. Fresh synthesis items (drafted in full, hand/Python-verified)

One fresh item per unit: **F1 = U6, F2 = U7, F3 = U8, F4 = U9.** **F5 is Part C item C2**, opens as a vector/force scenario (U10), converts into complex trigonometric form and a De Moivre-style rotation (U9), and closes by naming the polar/parametric circle the same tip traces (U8) — crossing three units outright, with the exactness of its numbers resting on the same special-triangle machinery U6/U7 built. All numeric results below were checked with Python (`cmath`/`math`) in addition to hand computation; the verification transcript is summarized inline.

### F1 (U6) — The zip-line inspection
> A zip-line cable runs from a platform 84 ft up a tower to a ground anchor 112 ft (horizontal distance) from the tower's base.
> ① Find the angle of depression θ from the platform to the anchor (nearest tenth of a degree) and the exact length of the cable.
> ② Using only \(\sin^2\theta+\cos^2\theta=1\) — not the calculator's inverse function — find \(\cos\theta\) from the triangle's side ratios, and confirm it agrees with \(\cos\theta\) evaluated directly from your angle in ①.
> ③ Course safety policy caps the depression angle at 35°. State, with the specific number that decides it, whether this line passes inspection.

**Worked solution.** ① The triangle is a 3-4-5 right triangle scaled by 28: legs 84 = 28(3) and 112 = 28(4), so the cable (hypotenuse) = 28(5) = **140 ft** exactly — confirmed by \(\sqrt{84^2+112^2}=\sqrt{19{,}600}=140\). \(\tan\theta = 84/112 = 3/4\), so \(\theta=\arctan(0.75)\approx\)**36.9°**. ② From the triangle, \(\sin\theta = 84/140 = 0.6\) (opposite/hypotenuse); \(\cos\theta=\sqrt{1-0.6^2}=\sqrt{0.64}=0.8\) — and \(\cos(36.9^\circ)\approx0.7997\approx0.80\) ✓, matching to two decimal places as required. ③ Since \(36.9^\circ>35^\circ\), **this zip-line fails inspection** — the specific number is the computed 36.9°, which exceeds the 35° cap; the anchor must move to lengthen the horizontal run (or the platform must be lowered) before the line may be used.

### F2 (U7) — The carousel horse
> A carousel horse's height above the platform (in meters) is modeled by \(h(t)=0.9\sin\!\left(\dfrac{\pi}{4}t\right)+1.1\), \(t\) in seconds.
> ① State the amplitude, period, and midline, and find the first time \(t>0\) at which the horse reaches its highest point.
> ② Find every time in \([0,8)\) seconds at which \(h(t)=1.55\) m, solving the equation exactly before converting to decimals.
> ③ Verify the period algebraically (not by citing the coefficient): expand \(\sin\!\left(\dfrac{\pi}{4}(t+8)\right)\) with the sum formula and show it simplifies to \(\sin\!\left(\dfrac{\pi}{4}t\right)\).

**Worked solution.** ① Amplitude **0.9 m**, midline **h = 1.1 m**, period \(=2\pi/(\pi/4)=\)**8 s**. Maximum occurs when \(\sin(\cdot)=1\): \(\frac{\pi}{4}t=\frac{\pi}{2}\Rightarrow\)**t = 2 s** (check: \(h(2)=0.9(1)+1.1=2.0\) ✓). ② Set \(0.9\sin(\frac{\pi}{4}t)+1.1=1.55\Rightarrow\sin(\frac{\pi}{4}t)=\frac{0.45}{0.9}=0.5\). So \(\frac{\pi}{4}t=\frac{\pi}{6}\) or \(\frac{5\pi}{6}\), giving **t = 2/3 s ≈ 0.67 s** and **t = 10/3 s ≈ 3.33 s** (both verified: \(h(2/3)=h(10/3)=1.55\) exactly). ③ \(\sin\!\left(\frac{\pi}{4}t+2\pi\right)=\sin\!\left(\frac{\pi}{4}t\right)\cos(2\pi)+\cos\!\left(\frac{\pi}{4}t\right)\sin(2\pi)=\sin\!\left(\frac{\pi}{4}t\right)(1)+\cos\!\left(\frac{\pi}{4}t\right)(0)=\sin\!\left(\frac{\pi}{4}t\right)\) — the period is not merely read off the coefficient but earned algebraically from the sum formula, cos 2π = 1, sin 2π = 0.

### F3 (U8) — The lawn sprinkler
> A rotating sprinkler's spray distance (in feet) is modeled in polar form by \(r=3-6\cos\theta\).
> ① Classify the curve (inner loop / cardioid / dimpled / convex) using the ratio test, and find the maximum value of \(r\) and the \(\theta\) at which it occurs.
> ② Find every \(\theta\in[0,2\pi)\) at which \(r=0\).
> ③ A garden path is modeled parametrically by \(x(t)=2t-3,\ y(t)=t^2\) for \(t\ge0\). Eliminate the parameter, identify the shape, and state its vertex point.
> ④ In 2–3 sentences: physically, what does it mean for the sprinkler curve to have an inner loop — what happens to the spray "direction" for \(\theta\) between your two answers in ②?

**Worked solution.** ① Ratio test: \(|a/b|=|3/{-6}|=0.5<1\Rightarrow\)**inner loop**. Maximum \(r\) occurs where \(\cos\theta=-1\), i.e. \(\theta=\pi\) (180°): \(r=3-6(-1)=\)**9**. ② Set \(3-6\cos\theta=0\Rightarrow\cos\theta=\frac12\Rightarrow\)**θ = π/3 and θ = 5π/3** (both exact — verified numerically: \(r(\pi/3)=r(5\pi/3)=0\) to machine precision). ③ Solve \(t=\frac{x+3}{2}\); substitute: \(y=\left(\frac{x+3}{2}\right)^2=\dfrac{(x+3)^2}{4}\), an upward-opening **parabola**, restricted to \(x\ge-3\) (since \(t\ge0\)); **vertex (−3, 0)**. ④ Between \(\theta=5\pi/3\) and \(\theta=\pi/3\) (passing through \(\theta=0\)), \(\cos\theta>\frac12\) so \(r=3-6\cos\theta<0\) — the model reports a negative distance, meaning the plotted point lands in the *opposite* direction from where the sprinkler head is aimed. That is exactly what draws the inner loop: near \(\theta=0\) the spray's true landing point crosses back near and through the pole, tracing a small loop inside the larger outer curve rather than reaching straight out along \(\theta\).

### F4 (U9) — The impossible root, put to use
> Find all three solutions to \(x^3=-8i\).
> ① Convert \(-8i\) to trigonometric form.
> ② Use De Moivre's Theorem to find all three cube roots, in trigonometric form and then exact rectangular form.
> ③ Verify one root by cubing it directly.
> ④ State the radius of the circle the three roots lie on and the angle between consecutive roots.
> ⑤ In one or two sentences: connect this problem to the unit's virtue of courage — unlike \(x^3=-8\) (which has the ordinary real solution \(-2\) sitting right on the number line before any complex root is ever sought), not one of this equation's three roots is a real number. What does accepting \(i\) as a legitimate number make solvable here that the real numbers, on their own, could never even begin?

**Worked solution.** ① \(-8i = 0-8i\), so \(r=8\); its angle is \(270^\circ\) (or \(-90^\circ\)): \(-8i = 8\,\text{cis}\,270^\circ\). ② Cube roots have modulus \(8^{1/3}=2\) and angles \(\theta_k=\dfrac{270^\circ+360^\circ k}{3}\) for \(k=0,1,2\): \(\theta_0=90^\circ,\ \theta_1=210^\circ,\ \theta_2=330^\circ\). In rectangular form: \(2\text{cis}90^\circ=2i\); \(2\text{cis}210^\circ=-\sqrt3-i\); \(2\text{cis}330^\circ=\sqrt3-i\). ③ Verify \((2i)^3\): \((2i)^3=8i^3=8(i^2\cdot i)=8(-1)(i)=\)**−8i** ✓ (confirmed independently by computer algebra, along with the other two roots). ④ All three roots have modulus **2** (radius of the circle); consecutive angles are 120° apart (90°→210°→330°), the three points forming an equilateral triangle inscribed in that circle — but unlike a real cubic, no rotation of that triangle ever lands on the real axis. ⑤ For \(x^3=-8\), a real root (\(-2\)) was available without ever leaving the real numbers, and De Moivre's Theorem only *supplied the other two*. For \(x^3=-8i\), the real numbers offer nothing at all to start from — every one of the three roots requires accepting \(i\) as legitimate; courage here is not embellishing an answer that real numbers already had, but making the whole family of solutions exist in the first place.

### F5 (U10 × U9 × U8) — **Part C item C2: The tugboats' turn** *(crosses three units)*
> Two tugboats pull a barge with forces \(\mathbf{F_1}=\langle12,0\rangle\) kN (due east) and \(\mathbf{F_2}=\langle0,5\rangle\) kN (due north).
> ① **Find the resultant.** Give the resultant force \(\mathbf{R}\) in component form, its magnitude, and its direction angle (nearest tenth of a degree).
> ② **Re-express as a complex number.** Write \(\mathbf{R}\) as the complex number \(z=12+5i\), and convert \(z\) to trigonometric form, stating the modulus and angle exactly where possible.
> ③ **Execute the turn.** A harbor pilot needs the net force rotated \(90^\circ\) counterclockwise (same magnitude) to push the barge broadside toward the dock. Multiply \(z\) by \(i\) (which is \(1\,\text{cis}\,90^\circ\)) using the product rule for two numbers in trigonometric form — moduli multiply, angles add — to find the new complex number \(z'\), then convert \(z'\) back to a force vector in component form. Verify \(|z'|=|z|\).
> ④ **Name the circle.** As the pilot sweeps the net force's *direction* from your angle in ① to your angle in ③ while holding its magnitude fixed at that constant value, the vector's tip traces part of a circle. Give that circle's polar equation, and a parametric pair \((x(\theta), y(\theta))\) tracing it.
> ⑤ **Close the arc** (2–3 sentences): name what \(\mathbf{R}\), \(z\), and the circle in ④ are — rectangular vector, complex number in trigonometric form, and polar/parametric curve — and explain why multiplying by \(i\) (a number of modulus 1) is the same operation as a 90° rotation, tying it to the product-rule reasoning that also underlies De Moivre's Theorem (repeated multiplication by the same modulus-1 angle).

**Worked solution.** ① \(\mathbf{R}=\mathbf{F_1}+\mathbf{F_2}=\langle12,5\rangle\); \(|\mathbf{R}|=\sqrt{12^2+5^2}=\sqrt{169}=\)**13 kN**; direction angle \(\theta=\arctan(5/12)\approx\)**22.6°** (a 5-12-13 triangle — \(\cos\theta=12/13,\ \sin\theta=5/13\) exactly). ② \(z=12+5i=13(\cos22.6^\circ+i\sin22.6^\circ)=13\,\text{cis}\,22.6^\circ\), modulus **13** exact, angle **≈22.6°** (exact via \(\cos\theta=12/13\)). ③ \(z'=z\cdot i=(12+5i)i=12i+5i^2=-5+12i\); by the product rule, modulus \(13\times1=13\) and angle \(22.6^\circ+90^\circ=112.6^\circ\), so \(z'=13\,\text{cis}\,112.6^\circ\); as a force vector, \(\mathbf{R}'=\langle-5,12\rangle\) — check \(|\mathbf{R}'|=\sqrt{25+144}=\sqrt{169}=\)**13** ✓, matching \(|\mathbf{R}|\) exactly, confirming the rotation preserved magnitude (both cross-checked independently by computer algebra). ④ The circle is \(r=13\) in polar form; parametrically, \((x(\theta),y(\theta))=(13\cos\theta,\ 13\sin\theta)\), \(\theta\) sweeping from \(22.6^\circ\) to \(112.6^\circ\). ⑤ \(\mathbf{R}\), \(z\), and the circle in ④ are the same fact told in three languages: a rectangular vector, a complex number in trigonometric (modulus-argument) form, and a polar/parametric curve — all describing the tip of a fixed-length arrow sweeping through angle. Multiplying by \(i\) rotates by 90° because \(i\) itself is \(1\,\text{cis}\,90^\circ\): the product rule says multiplying two trigonometric-form numbers multiplies their moduli and *adds* their angles, so multiplying by a modulus-1 number changes only the angle, by exactly that number's own angle — the identical mechanism that, applied to the same number over and over, *is* De Moivre's Theorem.

**Units crossed:** vector resultant and rotation (U10), complex trigonometric form and the product rule (U9), the polar/parametric description of the traced circle (U8) — with the exact 5-12-13 ratio underneath supplied by the same triangle machinery U6 and U7 built all semester. This item satisfies the "Part C crosses three or more units" requirement and is the semester's own version of the "five languages of the plane" grand arc named in `02_Design/plan.md` §8.

**Part C item C1 (assembly note).** Build C1 from the U6 C11 / U7 C11 lineage: both unit-test items already end by connecting an inverse-trigonometric question (recovering an angle from tanθ = 1/12, or from sinθ = 0.6) back to Unit 4's one-to-one/horizontal-line-test criterion — the strongest S1→S2 callback named in `02_Design/plan.md` §8. Fresh numbers; keep the two-angle "tangent/sine is not one-to-one over its full domain, restriction earns invertibility" argument as the throughline, and consider closing with the odd/even symmetry contrast from U7 C11 (why sine's restricted domain sits symmetrically about 0 while cosine's does not) if length allows.

## 6. Grading guidance — standing rubric at 15 pts per criterion

Same four criteria as every hand-graded item all year; only the scale changes. Score each 0–15 (rough bands: 13–15 excellent · 10–12 proficient · 6–9 developing · 0–5 beginning), total /60.

| Criterion (15 pts each) | What excellent looks like on the final | Where the evidence lives |
|---|---|---|
| **Understanding of the material** | Degree–radian and unit-circle fluency, Law of Sines/Cosines, identity substitutions, polar/parametric conversion and curve classification, De Moivre's Theorem, and vector arithmetic/dot-product/projection all executed correctly and fluently across five units, with notation exact throughout — the right language chosen for each unlabeled problem. | Mostly Part A |
| **Quality of reasoning** | Part B items read as real arguments: the 30-60-90 or double-angle derivation earns every line; the ambiguous case is fully resolved with its logic explained; the limaçon/complex-conjugate argument and the wind-and-current or Law-of-Cosines derivation are argued, not asserted; Part C's cross-unit connections (to Unit 4's inverse-function criterion, and among vector/complex/polar languages) are made explicitly. | Mostly Parts B & C |
| **Presentation & precision** | Clean vertical work, aligned equals signs, exact values kept (radical and π-forms before decimals, cis-notation used correctly), sketches labeled with asymptotes/poles/foci as relevant, pages in order — two hours of work a stranger could follow. | Whole exam |
| **Intellectual honesty** | Honor pledge signed and honored; work shown as actually done; proved vs. approximated facts labeled as such; any unfinished problem carries an honest note of where and why the student stopped — which earns respect, never punishment. | Whole exam |

**Load:** full-rubric grading at ~5 min/student, consistent with the unit-test budget (this is the year's final full Tier 3 sitting, alongside the ten unit tests and the Semester 1 final). Comment briefly on one strength and one target — this is the last written feedback the course gives.

## 7. Canvas implementation notes

- **Assignment type:** plain Canvas Assignment (no quiz component, per course standard). **Name:** `Semester 2 Final Exam · Precalculus Honors`. **Points:** 60. **Submission:** File Upload, `.pdf` only, one attempt.
- **Attach the rubric in Canvas:** the four standing criteria at 15 pts each, using the §6 descriptors, so scoring happens in SpeedGrader against the same rubric students have seen all year.
- **Module placement:** Semester 2 Finals Week module, third item, after the review lesson page and the review activity; due at the end of finals week. No lesson pages or other assignments share the week.
- **Timing:** the ~2-hour length is communicated, not enforced by a timer — the asynchronous format plus the honor pledge is the course's standing trust model (identical to unit tests and the Semester 1 final).
- **Student-facing description** must carry, verbatim in the course's standard wording, the ground-rules paragraph (one sitting, work alone, calculator for arithmetic and inverse-trigonometric evaluation only, notes closed), the honor line — *"I completed this exam on my own, without help from people, notes, or AI tools."* — and the standard submission block:

  > **Canvas Assignment Name:** Semester 2 Final Exam · Precalculus Honors
  > Complete the exam by hand on paper, honor line first. When you finish, photograph or scan your pages, combine them into **one PDF** with the pages in order, and upload the single file here. Name the file **LastName_FirstName_Precalculus_S2Final.pdf**.

- **No standards codes, no unit labels, no OpenStax references** anywhere on the student-facing exam. Items appear as Part A/B/C numbering only.
- After grading closes, release worked solutions (course self-correction convention) so students can review their year's-end feedback.
