# Heidegger index

<https://heidegger.delve.nu/index>

## Add lemmas to `index/heidegger-index.yml`

```pycon
>>> from index import add_ref
>>> add_ref('Grundriß', 'ZW', 79)
>>> add_ref('Kierkegaard, Søren', 'GA 29/30', 226, 'p')  # Referencing personal names
>>> add_ref('Sein und Zeit', 'ZEG', 63, 'w')  # Referencing works
>>> add_ref('Grundriß', 'GA 61', '159-160', ref_type='r')  # Referencing pages related to term
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
  -l, --lemma-type [p|w]  Type of lemma (p: person, w: work)
  -r, --ref-type [r]      Type of lemma (r: related)
  -b, --betacode          Convert lemma from betacode to unicode
  --help                  Show this message and exit.
```

E.g.:

```sh
add-ref Grundriß ZW 79
add-ref --lemma-type p 'Kierkegaard, Søren' 'GA 29/30' 226
```

## Add relations to `index/heidegger-index.yml`

```pycon
>>> from index import add_rel
>>> add_rel('φύσις', 'φύσει ὄντα', 'p')  # φύσις is parent of φύσει ὄντα
>>> add_rel('Aristoteles', 'De anima', 'a')  # Aristoteles is the author of De anima
>>> add_rel('μορφή', 'ὕλη', 'r')  # μορφή is related to ὕλη
```

This is also available via the terminal command `add-rel`:

```sh
$ add-rel --help

Usage: add-rel [OPTIONS] FIRST_LEMMA SECOND_LEMMA [p|a|r]
```

## Add a URN to lemmata in `index/heidegger-index.yml`

A Python function to add URNs to the lemma metadata. For now, we limit ourselves to the URNs used by [Perseus](https://scaife.perseus.org/). If the URN refers to a passage in the [Perseus Digital Library](https://scaife.perseus.org/) this passage will be rendered on the work lemma page. The lemma will also be accessible by the URN like so: `/index/lemma/example:urn:to:lemma`.

```pycon
>>> from index import add_urn
>>> add_urn('Aristoteles', 'p', 'urn:cts:greekLit:tlg0086') # Aristoteles can be found at this URN in Perseus and in the index.
```

A terminal command is also added:

```sh
$ add-urn --help

Usage: add-urn [OPTIONS] LEMMA [p|w] URN

Options:
  -f, --force  Overwrite URN if lemma already has a urn defined.
```

## Search for an existing reference

A terminal command `find-ref` is provided to search through existing references. It provides flexible matching, e.g.:

```sh
$ find-ref Seienden
Beziehung zu Seiendem als Solchem
Seiende im Ganzen
Sein zu Seiendem als Seidendem
```

## Page references

We datafy the page references based on the input string. It is matched against a regular expression that roughly looks like:

```python
'{start}(?:-{end}|{suffix}.?)?'
```

Where

- `start` is the first page (required, integer)
- `end` is the last page (optional, integer)
- `suffix` is a suffix (optional, 'f' or 'ff')

As can be seen from the regular expression, `end` and `suffix` are optional, and cannot appear simultaneously. Valid references are, for example `123`, `123-124` (make sure **not** to abbreviate final page numbers, like `123-4`) and `12f.`.

## Work references

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

## Tailwind

For styling, we make use of [Tailwind](https://tailwindcss.com). When editing the HTML, make sure to run the following command in a separate terminal window:

```sh
python manage.py tailwind
```

This will watch the HTML files and automatically render the necessary CSS into the stylesheet. Include the CSS changes into the commits.
