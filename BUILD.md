# Build Instructions

- Update `pyproject.toml` with version bump (SEMVER)

## Build Process

```bash
rm -rf dist/ build/ src/*.egg-info

./buidtest.sh # This uploads it to Test pypi
```

### Publish to PyPi Test

Test in Virtual Environment in fresh folder outside of project root

```bash
cd ../agentify-test
mkdir <version>
cd <version>
```

#### Create Virtual Python environment to ensure package is not loaded

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Install Package from Test PyPi

```bash
pip install
    --index-url https://test.pypi.org/simple
    --extra-index-url https://pypi.org/simple/ agentify-toolkit==0.2.1
```

#### Verify agentify-toolkit is running from virtual environment

```bash
pip show agentify-toolkit
```

#### Check version to confirm

```bash
agentify --version
```

#### Clean-up

```bash
deactivate
```

Once confirmed to be working successfully, do the same for prod:

```bash
rm -rf dist/ build/ *.egginfo
./buid.sh # This uploads it to PyPi Prod
```

Then repeat steps to test and verify version.
