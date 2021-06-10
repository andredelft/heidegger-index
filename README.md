# Heidegger index

## Add lemmas to `heidegger-index.yml`

```pycon
>>> from index import add_to_index
>>> add_to_index('Grundriß', 'ZW', '79')
>>> add_to_index('Kierkegaard, Søren' , 'GA 29/30', '226', 'p') # Referencing personal names
```

This function is also available als a terminal command `hi-add`, that can be installed using

```sh
$ pip install .
```

Usage:
```sh
$ hi-add --help
Usage: hi-add [OPTIONS] LEMMA WORK PAGE_REF

Options:
  -t, --type [p|w]  Type of lemma (e.g. 'p' for 'person')
  --help            Show this message and exit.
```

E.g.:
```sh
$ hi-add 'Grundriß' 'ZW' '79'
$ hi-add --type p 'Kierkegaard, Søren' 'GA 29/30' '226'
```

## Populate the Django DB

Initialize the databse:

```sh
$ python manage.py migrate
```

Populate the database:

```sh
$ python manage.py populate
```

Spin up the django project:
```sh
$ python manage.py runserver
```
and navigate to http://localhost:8000.

## References

The references to Heideggers works are gathered in `references.yml` in CSL YAML format. Using a citeproc processor these can be converted to a styled bibliography:

```shell
$ python refs.py
```

Output is stored in `references.html`