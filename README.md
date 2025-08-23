# python glue lock wrapper

![PyPI version](https://img.shields.io/pypi/v/pygluelock.svg)
[![Documentation Status](https://readthedocs.org/projects/pygluelock/badge/?version=latest)](https://pygluelock.readthedocs.io/en/latest/?version=latest)


pygluelock is a sync and async wrapper around the Glue Lock API for smart locks.

Please note that due to me only having an old generation of glue lock and that lock is missing the lock status, the lock status is not added in this project.

* PyPI package: https://pypi.org/project/pygluelock/
* Free software: MIT License
* Documentation: https://pygluelock.readthedocs.io

## Features

- Connect to Glue Lock API
- Retrieve all locks associated with your account
- Get lock status, battery, firmware, and events
- Control lock (lock/unlock)
- Async API using `aiohttp`

## Usage

### Run via CLI

After installing the package (e.g. `pip install .` or from PyPI), you can use the CLI:

```sh
pygluelock --username <your_username> --password <your_password>
```

This will connect to the Glue Lock API and print all locks associated with your account.

You can also run the main function straight away in your IDE of choice.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
