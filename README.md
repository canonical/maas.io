Static Django website blueprint
===

A stripped-down bootstrap Django project to serving static templates directly.
It is intented as a bootstrap for the Ubuntu design team's informational sites.

Much of Django's dynamic functionality (e.g. sessions, any database interation)
has been removed. URLs map directly to template locations, so creating a new
web page is as simple as creating a new template file.

While this project is public, you won't be able to use it out of the box unless
you have access to the private `django-fenchurch` plugin - which is currently
only accessible by members of Canonical. We have plans to change this soon.

Basic usage
---

Just clone the project and delete its version history:

``` bash
git clone https://github.com/ubuntudesign/static-django-bootstrap.git example-project
cd example-project
rm -rf .git   # Remove the existing git information
make setup    # Install dependencies etc. for development
make develop  # Run the development server
```

Now visit <http://0.0.0.0:8099>.

You can customise the port for the dev server by specifying the `PORT` environment variable:

``` bash
PORT=8054 make develop
```

Customisation
---

The most basic way to customise the project is to create templates and stylesheets:

``` bash
vim template/index.html  # Edit the homepage
vim template/about.html  # Create a new page
vim static/css/global.scss  # Edit the styles
```

Your changes should show immediately. Your new `about.html` page should be
immediately available at <http://0.0.0.0:8007/about>.

### Readme

You should probably customise the README for your new project:

``` bash
cp README.template.md README.md  # Overwrite this README
vim README.md  # Customise the README
```

### Error pages

You will probably want to make your error pages look prettier:

``` bash
vim templates/error/404.html  # Customise the 404 page
vim templates/error/500.html  # Customise the 500 page
```

### Dev port

By default, `make develop` will start the development server on port 8099.
However you may want to customise this by editing the `Makefile`:

``` bash
# Makefile

ifeq ($(PORT),)
    PORT=8099  # Default port for the dev server
endif
```

### Secret key

The app comes with the SECRET_KEY setting set to
"SECRET_KEY_INSECURE_PLACEHOLDER".

It doesn't matter that this is insecure initially, as none of the functionality
of the basic project uses the SECRET_KEY. However, you should change it when
you get the chance in case someone adds functionality that uses it in the
future.

Visit the
[secret key generator](http://www.miniwebtool.com/django-secret-key-generator/)
to generate a new key, and then set it in `webapp/settings.py` as follows:

``` python.py
# webapp/settings.py

SECRET_KEY = '!!!YOUR_NEW_SECRET_KEY_HERE!!!'
```

Dependencies
---

Among the dependencies of this project are several modules which we,
the Ubuntu design team, have written ourselves:

- django-fenchurch (private - soon to be open-sourced)
- [django-versioned-static-url](https://github.com/ubuntudesign/django-versioned-static-url)
- [django-static-root-finder](https://github.com/ubuntudesign/django-static-root-finder)
- [django-asset-server-url](https://github.com/ubuntudesign/django-asset-server-url)
