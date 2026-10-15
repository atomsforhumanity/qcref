# qcconst → qcref

`qcconst` has been renamed to [`qcref`](https://github.com/atomsforhumanity/qcref). This package only installs `qcref` and re-exports it under the old name with a `DeprecationWarning`.

```sh
python -m pip install qcref
```

```python
import qcref  # instead of: import qcconst
```

## Publishing (maintainers)

Publish once, after `qcref` 0.3.0 is on PyPI:

```sh
cd compat/qcconst
uv build
uv publish
```
