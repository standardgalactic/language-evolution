# Compilation Instructions

## Documents Ready for Compilation

### 1. Monograph: Admissible Reconstruction
**File**: `main.tex`
**Chapters**: 6 (intro + 4 theorems + conclusion)
**Size**: ~4,500 words

**Compile**:
```bash
cd /home/bonobo/github/language-evolution/admissible-reconstruction
lualatex main.tex
lualatex main.tex  # Second pass for cross-references
```

**Fallback** (if LuaLaTeX has microtype issues):
```bash
xelatex main.tex
xelatex main.tex
```

**Output**: `main.pdf`

---

### 2. Essay: Structural Invariance Across Modalities
**File**: `essay.tex`
**Chapters**: 10 (full cross-modal application)
**Size**: ~12,250 words

**Compile**:
```bash
cd /home/bonobo/github/language-evolution/admissible-reconstruction
lualatex essay.tex
lualatex essay.tex  # Second pass for cross-references
```

**Fallback**:
```bash
xelatex essay.tex
xelatex essay.tex
```

**Output**: `essay.pdf`

---

## Shared Dependencies

Both documents share:
- `preamble.tex` - Fonts, packages, theorem environments, macros
- `references.tex` - Bibliography (7 entries including Powers 1973)

Both use:
- **Font**: TeX Gyre Pagella (OpenType, via fontspec)
- **Engines**: LuaLaTeX primary, XeLaTeX fallback
- **Packages**: amsmath, amsthm, hyperref, microtype, enumitem

---

## Structure

```
admissible-reconstruction/
├── main.tex                    # Monograph driver
├── essay.tex                   # Essay driver
├── preamble.tex               # Shared preamble
├── references.tex             # Shared bibliography
└── chapters/
    ├── ch00-introduction.tex          # Monograph intro
    ├── ch01-representation-invariance.tex
    ├── ch02-admissibility-preservation.tex
    ├── ch03-monotonic-relaxation.tex
    ├── ch04-non-identifiability.tex
    ├── ch05-conclusion.tex            # Monograph conclusion
    ├── ch06-essay-introduction.tex    # Essay Section I
    ├── ch07-essay-math-foundations.tex    # Essay Section II
    ├── ch08-essay-crossmodal.tex          # Essay Section III
    ├── ch09-essay-pct.tex                 # Essay Section IV
    ├── ch10-essay-synthesis.tex           # Essay Section V
    ├── ch11-essay-implications.tex        # Essay Section VI
    ├── ch12-essay-limits.tex              # Essay Section VII
    ├── ch13-essay-objections.tex          # Essay Section VIII
    ├── ch14-essay-future.tex              # Essay Section IX
    └── ch15-essay-conclusion.tex          # Essay Section X
```

---

## LaTeX Installation (if needed)

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install texlive-luatex texlive-xetex texlive-latex-base \
                 texlive-latex-recommended texlive-fonts-recommended
```

**Arch Linux**:
```bash
sudo pacman -S texlive-core texlive-bin
```

**macOS (with Homebrew)**:
```bash
brew install --cask mactex-no-gui
```

**Windows**:
Download MiKTeX or TeX Live installer from CTAN.

---

## Expected Compilation Time

- **Monograph** (~40 pages): 5-10 seconds per pass
- **Essay** (~90 pages): 10-20 seconds per pass
- **Total** (both documents, 2 passes each): ~1 minute

---

## Known Issues

### LuaLaTeX + microtype + TeX Gyre Pagella
On some systems, LuaLaTeX's microtype package conflicts with OpenType font loading.

**Symptom**: Error about font identifiers or pdf backend
**Solution 1**: Comment out `\usepackage{microtype}` in `preamble.tex`
**Solution 2**: Use XeLaTeX fallback instead

### Missing Fonts
If TeX Gyre Pagella is not found:

**Install fonts**:
```bash
sudo apt install tex-gyre  # Ubuntu/Debian
```

Or download from GUST: https://www.gust.org.pl/projects/e-foundry/tex-gyre

---

## Verification

After compilation, check:
- [ ] Both PDFs generated without errors
- [ ] Table of contents correct (page numbers)
- [ ] All cross-references resolved (no "??" marks)
- [ ] Hyperlinks work (if using PDF viewer)
- [ ] Bibliography entries formatted correctly
- [ ] No overfull/underfull hbox warnings (aesthetic)

---

## Gyre Protocol Compliance

Both documents comply with The Gyre Protocol:
- ✅ LuaLaTeX primary, XeLaTeX fallback
- ✅ TeX Gyre Pagella via fontspec
- ✅ Two-pass compilation documented
- ✅ thebibliography (no BibTeX)
- ✅ Zero self-citations
- ✅ Continuous prose (no bullets in body)
- ✅ "Flyxion, Independent Researcher" byline
- ✅ No exact publication dates

---

## File Sizes

**Source** (LaTeX):
- `main.tex`: 3 KB
- `essay.tex`: 3 KB
- `preamble.tex`: 2 KB
- `references.tex`: 1 KB
- All chapters: ~80 KB total

**Expected PDFs**:
- `main.pdf`: ~400-500 KB (40 pages)
- `essay.pdf`: ~800-1000 KB (90 pages)

---

## Next Steps

1. Install LaTeX (see instructions above)
2. Compile both documents
3. Review PDFs for LaTeX errors or formatting issues
4. Fix any typos discovered during PDF review
5. Optionally: Generate figures from theorems.py for inclusion

---

**Status**: Documents complete and ready for compilation.
**LaTeX available on this system**: No (Ubuntu Core, limited package management)
**Compilation location**: Any system with TeX Live or MiKTeX installed
