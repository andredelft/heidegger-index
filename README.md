# Heidegger index

```pycon
>>> from index import add_to_index
>>> add_to_index('Grundriß', 'ZW', '79')
>>> add_to_index('Grundriß', 'GA 79', '8-9', 'r') # Not exact term, but related discussion
>>> add_to_index('Kierkegaard, Søren' , 'GA 29/30', '226', 'p') # Referencing personal names
```

## References

The references to Heideggers works are gathered in `references.yml` in CSL YAML format. Using a citeproc processor these can be converted to a styled bibliography:

```shell
$ python refs.py
```

Output is stored in `references.html`
