MAAS website project
===

This is a simple databaseless informational website project, based on
[static-django-bootstrap](https://github.com/ubuntudesign/static-django-bootstrap).

Basic usage
---

To run the site locally:

``` bash
make setup    # Install dependencies - only needed the first time
npm install   # Install all node dependencies and vanilla theme
make develop  # Auto-compile sass files and run the dev server
```

Now visit <http://127.0.0.1:8000>.

To see what other `make` commands are available, run `make help`.

Documentation
---

The documentation lived under `/docs`, but isn't included in this repository.

It is pulled in from [maas-docs](https://github.com/canonicalltd/maas-docs),
using the [documentation-builder](https://github.com/canonicalltd/documentation-builder)
and the [wrapper.jinja2](config/wrapper.jinja2) template.

Build the docs:

``` bash
pip3 install documentation-builder
make docs
```

Then run the site and visit <http://127.0.0.1:8000/docs/en/>.
