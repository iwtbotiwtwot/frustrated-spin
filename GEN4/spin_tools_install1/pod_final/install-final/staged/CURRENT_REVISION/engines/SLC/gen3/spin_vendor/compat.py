from types import SimpleNamespace
from . import exact_factors as exact
from .util import digest
retained=SimpleNamespace(_modules=lambda:(None,exact),_project_indices=exact._project_indices)
engine=SimpleNamespace(retained_engine=retained,zeta_points=exact._zeta_points)
a=SimpleNamespace(n96_engine=engine,canonical_sha256=digest)
