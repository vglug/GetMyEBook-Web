# -*- coding: utf-8 -*-
# Compatibility shim — the actual implementation lives in cps/models/db.py.
#
# Using sys.modules aliasing ensures that cps.db and cps.models.db are the
# SAME Python module object. This means mutable module-level state (e.g.
# `cc_classes`) is always shared — setting attributes anywhere is visible
# to functions defined inside cps/models/db.py without any indirection.
import sys
from cps.models import db as _real_db

sys.modules[__name__] = _real_db
