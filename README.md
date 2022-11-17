### Running the tests

You use `poetry` and `pytest` to run the tests:

`poetry run pytest -s`

You can also run specific files

`poetry run pytest tests/<test_folder>/<test_file.py>`

and even use filtering with `-k`

`poetry run pytest -k "Manager"`

You can use the flags `-vx` where `v` prints the test & `x` makes the test stop if any tests fails (Verbose, X-fail)

You can get the coverage report like this:

`poetry run pytest -s --cov --cov-report term-missing`

### Using the app

You can boot the app like this:

```
poetry lock
poetry install
docker-compose up
```

You can use the app like this:

```
import requests
r = requests.get("http://0.0.0.0:8000/LDAP/all")
print(r.json()[-2])
```

Or you can go to [the swagger documentation](http://localhost:8000/docs) for a more graphic interface