# Dependencies and separate rights

The SAM Research-Only Licence applies only to rights controlled by its licensor.
It does not restrict independent rights in the following software, which is
installed separately and not vendored in this release.

| Component | Use | Licence/source |
|---|---|---|
| Python | Interpreter and standard library | [PSF licence and bundled notices](https://docs.python.org/3/license.html) |
| NumPy | Required by the retained V6 foundation; array and numerical helpers | [BSD 3-Clause](https://numpy.org/doc/stable/license.html) |
| PyOpenCL | Optional retained hardware source; not required by the portable core tests | [MIT licence](https://documen.tician.de/pyopencl/misc.html#license) |
| System C compiler/OpenCL implementation | Optional hardware-specific modules | Provider-specific licences; not included |

The tested NumPy version is recorded in requirements-tested.txt. Installed
NumPy distributions can include further components and notices, which remain
with that distribution. This repository does not relicense those packages.

The exported Q3/Q2/Q1 compatibility code, V6 source archive, native kernels and
J4/Li-6 source data are identified project components in
provenance/SOURCE_MANIFEST.json. The historical names preserve provenance; they
are not new third-party licences. Earlier grants covering particular copies
remain effective according to their terms. See legal/RIGHTS_AND_COPYRIGHT.md.

The supporting `SAMA/` collection retains its independent licences and originating
Courtroom notices. See [SAMA licences](SAMA/LICENSE.md) and
[SAMA licence directory](SAMA/LICENSES/README.md). Optional python-flint is not
vendored; its independently applicable licence and dependency notices accompany
its installed distribution. It is not needed by the required NumPy-only setup.
