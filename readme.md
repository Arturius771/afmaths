# afmaths

A simple package of math functions. Originally this was written to enable logging out each step in the console in a pretty way, but that is too difficult to maintain. For now it just a reference repo and a means of documenting algorithms.

# Todo

- Add tests
- Create output functionality, which prints (in a user friendly way) the steps required
- Doc comments
- Document how to build/run
- Document how to upgrade the npm package
- Document and implement semantic versioning
- Use currying for functions
- Adapt hohmann transfer style to be closer to the repo's

## 1. Install or Activate the Virtual Environment

It's recommended to use a virtual environment for isolation. If you don't already have a virtual environment, create and activate one:

### Create and start virtual environment:

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

## 2. Install Required Dependencies

Ensure that setuptools and wheel are installed in your environment:

```bash
pip install setuptools wheel twine
```

or

```bash
pip install -r requirements.txt
```

## 3. Update version number

```bash
setup(
    name="astronomy_types",
    version="0.2.0",  # Update this to the new version number
    ...
)
```

## 4. Build the dist

```bash
python setup.py sdist bdist_wheel
```

## 5. Upload with `twine`

```bash
twine upload dist/*
```

And enter in the API token when prompted
