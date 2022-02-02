# Heidegger index

<https://delve.nu/heidegger-index>

## Add lemmas to `index/heidegger-index.yml`

```pycon
>>> from index import add_ref
>>> add_ref('Grundriß', 'ZW', '79')
>>> add_ref('Kierkegaard, Søren', 'GA 29/30', '226', 'p') # Referencing personal names
>>> add_ref('Sein und Zeit', 'ZEG', '63', 'w') # Referencing works
>>> add_ref('Grundriß', 'GA 61', '159-160', 'r') # Referencing related terms
```

This function is also available als a terminal command `add-ref`, that can be installed using

```sh
pip install .
```

Usage:

```sh
$ add-ref --help
Usage: add-ref [OPTIONS] LEMMA WORK REF

Options:
  -t, --type [p|w]  Type of lemma (p: person, w: work)
  --help            Show this message and exit.
```

E.g.:

```sh
add-ref Grundriß ZW 79
add-ref --type p 'Kierkegaard, Søren' 'GA 29/30' 226
```

### Page reference

We datafy the page references based on the input string. It is matched against a regular expression that roughly looks like:

```python
'{start}(?:-{end}|{suffix}.?)?'
```

Where

- `start` is the first page (required, integer)
- `end` is the last page (optional, integer)
- `suffix` is a suffix (optional, 'f' or 'ff')

As can be seen from the regular expression, `end` and `suffix` are optional, and cannot appear simultaneously. Valid references are, for example `123`, `123-124` (make sure **not** to abbreviate final page numbers, like `123-4`) and `12f.`.

### Work references

The references to Heideggers works are gathered in `index/works.yml` in CSL YAML format. Using a citeproc processor these can be converted to a styled bibliography using the command `format-refs`. The output is stored in `index/works.html`

## Django project

A Django project is included with models into which `index/heidegger-index.yml` can be ingested and served as a dynamic HTML page. Follow the steps below to spin up the project.

1. Install requirements:

   ```sh
   pip install -r requirements.txt
   ```

2. Initialize the databse:

   ```sh
   python manage.py migrate
   ```

3. Populate the database:

   ```sh
   python manage.py populate_index
   ```

4. Spin up the django project:

   ```sh
   python manage.py runserver
   ```

5. Navigate to <http://localhost:8000>.
