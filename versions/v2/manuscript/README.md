# Resolving the double-root conjecture: Section 5, Table 5, p. 23 (2017)

Haobo Ma (ChronoAI Pte Ltd, Singapore) and Wenlin Zhang (National University of
Singapore; ChronoAI Pte Ltd, Singapore).

For the polynomial-form tree modulo `(x-1)^2`, the complete generation counts are
`G_n = 1 + n(n-1)/2` for every `n >= 0`. Thus the recurrence with coefficients
`(3,-3,1)` holds for every `n >= 3`. The note also proves `G_n=n` for `n>=1`
modulo `x^2-1`, correcting the first row of Table 5 at `G_3` from 4 to 3.
For `x^2-x+1`, it proves `G_n=6n-20` for `n>=6` and the recurrence
`G_n=2G_(n-1)-G_(n-2)` precisely from `n=8`. For every `m>=1`, the quotient
by `x^m-1` has `G_n=sum(binomial(n-1,r),r=0..m-1)` for `n>=1`.
The case `m=3` has the same generation counts as the double-root tree.

## Build

The main source is `note.tex`, with its bibliography included. Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, use a LaTeX distribution providing `lmodern`, `amsmath`, `amssymb`,
`amsthm`, `booktabs`, `array`, `longtable`, `geometry`, and `hyperref`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

No external bibliography database or BibTeX pass is needed.

## Exact finite checks

Python 3.10 or later, standard library only:

```sh
python3 verify.py > verification.json
```

The output ends with status `ALL_CHECKS_OK`. The complete residue shells through
depth 80 are compared with the formulas, using monic integer polynomial division.
For the double root, a second implementation uses value-and-derivative pairs.
The checks also cover distances, accumulated counts, recurrence onsets, the eleven
double-root Table 5 values, and the corrected `x^2-1` value. Universal polynomial
generations and their reductions are checked through depth 13.
The hexagonal quotient is checked independently in polynomial and lattice
coordinates through depth 80, including complete sector shells, the sharp
recurrence onset and generating function. Quotients by `x^m-1` are checked
for `1<=m<=6` through depth 16, with every residue's distance and every count.

## Mathematical coverage

The paper's definitions are from Ballot, Kimberling and Moses, *Linear Recurrences
Originating From Polynomial Trees*, The Fibonacci Quarterly 55(5) (2017), 15–27:
https://doi.org/10.1080/00150517.2017.12427731 . The exact posing locator is Section 5,
Table 5, page 23, the row `x^2-2x+1`. This is a polynomial quotient, not evaluation
at the repeated root 1.

The pinned declaration `result : claim` in
https://github.com/the-omega-institute/trureturing/blob/50f2a97bb5e704842f2c32c6095f68a0dc62c779/D5/S3/Combinatorics/PolynomialTrees/BallotKimberlingMosesDoubleRootGeneration.lean
proves the double-root recurrence with witness `N=3`. In that source, `seen_spec`
describes the accumulated sets, `generation_succ_spec` describes the shells, and
`G_sum` gives their triangular-sum cardinalities. The distance formula, generating
function, accumulated-set cardinality, `x^2-1` correction, hexagonal quotient,
and cyclic-quotient family have written proofs
in the note. The finite checker verifies the explicit ranges above. The remaining
Table 5 rows, Table 6 rows, and numbered Conjectures 1–6 are distinguished in the
note's coverage table; they are not consequences claimed for the double-root case.

## License

The note and accompanying verification code are licensed under Creative Commons
Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/ .
Copyright 2026 Haobo Ma and Wenlin Zhang. Linked scientific works retain their
respective licenses.
