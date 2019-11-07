MAAS website project
===

[![CircleCI build status](https://circleci.com/gh/canonical-web-and-design/maas.io.svg?style=shield)](https://circleci.com/gh/canonical-web-and-design/maas.io)
[![Code coverage](https://codecov.io/gh/canonical-web-and-design/maas.io/branch/master/graph/badge.svg)](https://codecov.io/gh/canonical-web-and-design/maas.io)

This is the simple Flask project behind <https://maas.io>.

## Local development

The simplest way to run the site locally is to first [install Docker](https://docs.docker.com/engine/installation/) (on Linux you may need to [add your user to the `docker` group](https://docs.docker.com/engine/installation/linux/linux-postinstall/)), and then use the `./run` script:

``` bash
./run
```

Once the containers are setup, you can visit <http://127.0.0.1:8006> in your browser.

### Building CSS

For working on [Sass files](_sass), you may want to dynamically watch for changes to rebuild the CSS whenever something changes.

To setup the watcher, open a new terminal window and run:

``` bash
./run watch
```
