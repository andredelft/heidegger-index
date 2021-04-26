# Heidegger index

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
  -t, --type [p]  Type of reference (e.g. 'p' for 'person')
  --help          Show this message and exit.
```

E.g.:
```sh
$ hi-add 'Grundriß' 'ZW' '79'
$ hi-add 'Kierkegaard, Søren' 'GA 29/30' '226' --type p
```

## References

The references to Heideggers works are gathered in `references.yml` in CSL YAML format. Using a citeproc processor these can be converted to a styled bibliography:

```shell
$ python refs.py
```

Output is stored in `references.html`
