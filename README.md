# fermi_problems

A library for fermi estimation and game to see how good you are at solving order of magnitude estimation problems

## Kinds of problems solved

- I don't have the real data (No need to aggressively round or avoid square roots)
- I don't have a calculator (Avoid square roots, round aggressively)
- But I do have some subjective estimates
- The problem can be decomposed into parts that I can know or estimate
- The numbers are very small or very large
- The decision doesn't turn on fine precision

## We have a computer

We shouldn't use calculations that are approximations, when we can use the actual root or log or what have you. However, we should pay attention to significant digits and attempt to not report spurious precision.

That said, I'm including the alternative approximate calculations for comparison.

- Don't aggressively round
- Use actual geometric mean
- Plug in estimates
    - Single estimate (with some number of digits of precision)
    - Magnitude only
    - Range, which is simplified to geometric mean
- Get bounds on the answer



## Possibly useful packages


https://github.com/slightlynybbled/engineering_notation/tree/master

https://pypi.org/project/magnitude/
https://pypi.org/project/fuzzysets/

### Steps

1. Think up a problem
2. Identify factors that chain together to multiply to the answer
3. Do unit conversions (dimensional analysis)
4. Represent the uncertainity in the factors:

- Single estimate (rounding rules set bounds of precision)
- Range estimate (with geometric mean or interval arithmetic)
- Triangular numbers/Fuzzy arithmetic
- Products of probability distributions, e.g. uniform or normal

5. Work out significant digits
6. Look at wost case range (interval arithmetic)
7. look at best case range (products of log normals)

## Related topics

- https://en.wikipedia.org/wiki/Fermi_problem
- https://www.lesswrong.com/posts/PsEppdvgRisz5xAHG/fermi-estimates
- https://en.wikipedia.org/wiki/Significant_figures


- http://www.astro.yale.edu/astro120/SigFig.pdf
- https://www.calculatorsoup.com/calculators/math/significant-figures.php - uh oh, computer numbers don't work like that
- https://chem.libretexts.org/Bookshelves/Analytical_Chemistry/Supplemental_Modules_(Analytical_Chemistry)
  /Quantifying_Nature/Significant_Digits

Is this useful? (fuzzy number multiplication)
https://www.sciencedirect.com/science/article/pii/S0888613X18303153
or
https://www.researchgate.net/publication/353821216_Triangular_fuzzy_numbers_multiplication_QKB_method

Various:

- https://nunosempere.com/blog/2022/08/20/fermi-introduction/ <- what are log normals?
- https://aperiodical.com/2018/02/approaching-fermi-problems-with-the-approximate-geometric-mean/
- https://www.cell.com/biophysj/pdfExtended/S0006-3495(14)01124-2

TODO- decide if this make sense: 2552*18.0-4.0002 =45932 (5 sig figs, why not 3?)
https://www.sigfigscalculator.com/