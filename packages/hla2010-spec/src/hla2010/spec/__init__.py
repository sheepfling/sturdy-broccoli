"""Clean Python HLA 1516.1-2010 specification package.

Use this package when you want the standalone spec surface:

```python
from hla2010.spec import RTIambassadorSpec, FederateAmbassadorSpec
```

The runtime adapter layer lives in :mod:`hla2010.runtime_api`.
"""
from __future__ import annotations

from .._spec_impl import (
    FederateAmbassadorSpec,
    RTIambassadorSpec,
    lower_camel_to_snake,
)

__all__ = [
    "FederateAmbassadorSpec",
    "RTIambassadorSpec",
    "lower_camel_to_snake",
]
