# Unit Test

### Test all module

```bash
python -m unittest discover tests/ -v
```

### Test single module

```bash
python -m unittest -v tests/test_satellite.py
```

### Coverage report

```bash
coverage run -m unittest discover tests/ -v
```
```bash
coverage report
```
```bash
coverage html
```