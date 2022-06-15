MAAS website project
===

[![Code coverage](https://codecov.io/gh/canonical-web-and-design/maas.io/branch/master/graph/badge.svg)](https://codecov.io/gh/canonical-web-and-design/maas.io)

This is the simple Flask project behind <https://maas.io>.

## Development

The simplest way to run the site is with [the `dotrun` snap](https://github.com/canonical-web-and-design/dotrun/):

```bash
dotrun
```

Afterwards the website will be available at <http://localhost:8006>.

When you start changing files, the server should reload and make the changes available immediately.

### Building CSS

For working on [Sass files](static/sass), you may want to dynamically watch for changes to rebuild the CSS whenever something changes.

To setup the watcher, open a new terminal window and run:

``` bash
./run watch
```

# Deploy
You can find the deployment config in [konf/site.yaml](konf/site.yaml)
