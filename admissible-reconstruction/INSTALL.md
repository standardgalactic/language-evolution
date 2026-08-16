# Installation Guide for Compiling LaTeX Documents

## Current System Status
- **OS**: Ubuntu Core 24
- **Package manager**: snap (available but permissions restricted)
- **LaTeX installed**: No
- **Can install packages**: No (insufficient permissions)

---

## Option 1: Tectonic (Recommended - Easiest)

**Best for**: Quick compilation, auto-downloads packages

**On a system with permissions**:
```bash
snap install tectonic
```

**Then compile**:
```bash
cd /home/bonobo/github/language-evolution/admissible-reconstruction

# Essay (10 chapters, ~90 pages)
tectonic essay.tex

# Monograph (6 chapters, ~40 pages)
tectonic main.tex
```

**Advantages**:
- Automatically downloads needed packages
- No need to install full TeX Live (~5GB)
- Single command compilation (handles multiple passes automatically)
- Based on XeTeX (supports our fontspec setup)

---

## Option 2: Full TeX Live Installation

**On Ubuntu/Debian with sudo**:
```bash
sudo apt update
sudo apt install texlive-luatex texlive-xetex \
                 texlive-latex-base \
                 texlive-latex-recommended \
                 texlive-fonts-recommended \
                 tex-gyre
```

**Size**: ~1-2 GB

**Then compile**:
```bash
cd /home/bonobo/github/language-evolution/admissible-reconstruction

# Primary engine (LuaLaTeX)
lualatex essay.tex
lualatex essay.tex  # Second pass for cross-references

lualatex main.tex
lualatex main.tex

# Fallback engine (XeLaTeX) if microtype issues
xelatex essay.tex
xelatex essay.tex

xelatex main.tex
xelatex main.tex
```

---

## Option 3: Overleaf (No Installation)

**Upload to Overleaf**:
1. Go to https://www.overleaf.com
2. Create new project → Upload Project
3. Zip the `admissible-reconstruction/` folder
4. Upload zip
5. Set compiler to LuaLaTeX (or XeLaTeX) in project settings

**Files to upload**:
```
admissible-reconstruction/
├── main.tex
├── essay.tex
├── preamble.tex
├── references.tex
└── chapters/ (all 16 .tex files)
```

**Advantages**:
- No local installation needed
- Compile in browser
- Automatically handles two passes
- Can download PDFs directly

---

## Option 4: Docker (Portable)

**Create Dockerfile**:
```dockerfile
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    texlive-luatex \
    texlive-xetex \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    tex-gyre
WORKDIR /work
```

**Build and compile**:
```bash
docker build -t latex-compiler .
docker run -v /home/bonobo/github/language-evolution/admissible-reconstruction:/work \
    latex-compiler \
    sh -c "lualatex essay.tex && lualatex essay.tex"
```

---

## Option 5: GitHub Actions (Automated)

**Create `.github/workflows/compile-latex.yml`**:
```yaml
name: Compile LaTeX
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: xu-cheng/latex-action@v2
        with:
          root_file: |
            admissible-reconstruction/essay.tex
            admissible-reconstruction/main.tex
          working_directory: .
          compiler: lualatex
      - uses: actions/upload-artifact@v3
        with:
          name: PDFs
          path: |
            admissible-reconstruction/essay.pdf
            admissible-reconstruction/main.pdf
```

**Advantages**:
- Automatic compilation on every commit
- Download PDFs from GitHub Actions artifacts
- No local setup needed

---

## Current Environment Limitations

This environment (Ubuntu Core in copilot-cli snap):
- ❌ Cannot install snap packages (permission denied)
- ❌ No apt/apt-get available
- ❌ Cannot use sudo for package installation
- ✅ Can read/write files in repository
- ✅ Can create/edit LaTeX source files

**To compile on THIS system**, you would need:
1. Administrator/root access to install packages, OR
2. Pre-installed TeX distribution, OR
3. Portable TeX installation in user directory

---

## Recommended Path Forward

**For immediate compilation**:
1. **Use Overleaf** (fastest, no installation)
   - Upload zip of `admissible-reconstruction/`
   - Compile in browser
   - Download PDFs

**For local compilation**:
1. **On another machine** with sudo access:
   ```bash
   snap install tectonic
   cd /path/to/language-evolution/admissible-reconstruction
   tectonic essay.tex
   tectonic main.tex
   ```

2. **Or full TeX Live**:
   ```bash
   sudo apt install texlive-luatex texlive-xetex \
                    texlive-latex-recommended tex-gyre
   cd /path/to/language-evolution/admissible-reconstruction
   lualatex essay.tex && lualatex essay.tex
   lualatex main.tex && lualatex main.tex
   ```

---

## Required Packages Summary

**Minimal (for our documents)**:
- LuaLaTeX or XeLaTeX engine
- amsmath, amssymb, amsthm
- mathtools
- geometry
- hyperref
- microtype
- enumitem
- titlesec
- fontspec
- TeX Gyre Pagella font

**Tectonic**: Auto-downloads all of these ✓
**TeX Live full**: Includes all of these ✓
**TeX Live basic**: Missing some, need manual installation ✗

---

## Next Steps

Choose one option above based on your access level:
- **No sudo, no other machine**: Use Overleaf (Option 3)
- **Have sudo somewhere**: Install Tectonic (Option 1) or TeX Live (Option 2)
- **Want automation**: Use GitHub Actions (Option 5)
- **Want portability**: Use Docker (Option 4)

Once compiled, PDFs will be:
- `essay.pdf` (~800-1000 KB, 90 pages)
- `main.pdf` (~400-500 KB, 40 pages)
