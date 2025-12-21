# Contributing

Thanks for contributing! This project succeeds because of people like you.

## Bug or issue?

To raise a bug or issue, please use [our GitHub](https://github.com/phalt/cicerone/issues).

Check if the issue already exists by using the search feature.

When submitting an issue or bug, please include:

1. The version of cicerone you are using
2. Any errors or outputs you see in your terminal
3. The OpenAPI schema you are using (this is particularly important).

## Contribution

If you want to directly contribute you can do so in two ways:

1. Documentation
2. Code

### Documentation

We use [mkdocs](https://www.mkdocs.org/) and [GitHub pages](https://pages.github.com/) to deploy our docs.

Fixing grammar, spelling mistakes, or expanding the documentation to cover undocumented features are all valuable contributions.

Please see the **Set up** instructions below to run the docs locally on your computer.

### Code

Writing code for new features or fixing bugs is a great way to contribute.

#### Set up

Clone the repo:

```sh
git@github.com:phalt/cicerone.git
cd cicerone
```

Move to a feature branch:

```sh
git branch -B my-branch-name
```

Install UV (if not already installed):

```sh
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip:
pip install uv
```

Install all the dependencies:

```sh
make install
```

This will use UV to create a virtual environment and install all dependencies. UV handles the virtual environment automatically—no need to activate it manually.

To make sure you have things set up correctly, run the tests:

```sh
make test
```

### Preparing changes for review

See if tests pass:

```sh
make test
```

You can also test cicerone against all schemas from the APIs-guru/openapi-directory repository (4000+ schemas):

```sh
make test-openapi-directory
```

This command clones the openapi-directory, tests parsing all schemas, and reports results. This is useful for ensuring cicerone works with real-world OpenAPI schemas.

Check your `git diff` to see if anything unexpected changed. If something changed that you didn't expect, something went wrong. We want to avoid unintended changes to the codebase.

Format and lint the code:

```sh
make format
```

The generated code is automatically formatted with Ruff for both style and linting.

Make sure you add to `CHANGELOG.md` and `docs/CHANGELOG.md` what changes you have made.

Make sure you add your name to `CONTRIBUTORS.md` as well!

### Making a pull request

Please push your changes to a feature branch and make a new [pull request](https://github.com/phalt/cicerone/compare) on GitHub.

Please add a description to the PR explaining what changed and why.

After a review you might need to make more changes.

Once accepted, a core contributor will merge your changes!
