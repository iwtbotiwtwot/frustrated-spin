# Dependencies and separate rights

MIT/CC BY grants apply only to project-owned material as specified in [LICENSING.md](LICENSING.md). Dependencies are installed separately and retain their own terms, including all bundled-library notices in the actual distribution used.

| Component | Role | License/source |
|---|---|---|
| Python 3.12 | Interpreter and standard library | [PSF and bundled notices](https://docs.python.org/3/license.html) |
| NumPy 2.1.2 | Required by the N2000 runtime and retained foundation | [BSD-3-Clause and distribution notices](https://numpy.org/doc/stable/license.html) |
| python-flint 0.8.0 | **Required** for N2000 exact integer/polynomial arithmetic | [MIT wrapper](https://github.com/flintlib/python-flint/blob/0.8.0/LICENSE) |
| FLINT | Native arithmetic library used/bundled by python-flint | [LGPL-3.0-or-later](https://github.com/flintlib/flint/blob/v3.3.1/COPYING.LESSER); installed binary distribution notices apply |
| GMP/MPFR and other libraries bundled in arithmetic wheels | Native dependencies | Their own licenses and source/distribution notices, as included with the installed wheel |
| gdown 5.2.0 | Optional public data download helper | [MIT](https://github.com/wkentaro/gdown/blob/v5.2.0/LICENSE) and its dependency notices |
| Zstandard | Optional compressed-data verification/restoration | [Upstream licensing](https://github.com/facebook/zstd#license); BSD/GPL alternatives as distributed |
| PyOpenCL | Optional earlier hardware routes | [MIT](https://documen.tician.de/pyopencl/misc.html#license) |
| CUDA/CuPy/compiler/OpenCL implementations | Optional historical GPU/hardware routes | Respective vendor/project terms; not required by portable CPU reproduction |

A license on the Python wrapper does not replace FLINT or bundled-library licenses. Anyone redistributing those dependency binaries must retain and comply with their own accompanying licenses. The N2000 requirements are pinned in `reproduce/n2000/requirements.txt` and `requirements-download.txt`.

The sealed foundation source supplement is a project-owned component included by its exact hash in [RUNTIME_LICENSE.md](RUNTIME_LICENSE.md). Separately licensed third-party materials, including any historical collections with their own notices, remain under those notices. This spin release does not change licenses of the unrelated SAMA collection in the parent repository.
