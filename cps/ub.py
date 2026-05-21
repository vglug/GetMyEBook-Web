# -*- coding: utf-8 -*-
# Compatibility shim — the actual implementation lives in cps/models/ub.py.
#
# Using sys.modules aliasing ensures that cps.ub and cps.models.ub are the
# SAME Python module object. This means mutable module-level state (e.g.
# `session`) is always shared — setting `ub.session = x` anywhere is visible
# to functions defined inside cps/models/ub.py without any indirection.
import sys
from cps.models import ub as _real_ub

sys.modules[__name__] = _real_ub
