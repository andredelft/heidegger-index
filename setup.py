from setuptools import setup, find_packages

setup(
    name="heidegger_index",
    version="1.0",
    description="Heidegger index",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "add-ref=index:click_add_ref",
            "add-rel=index:click_add_rel",
            "add-metadata=index:click_add_metadata",
            "find-ref=index:click_find_ref",
            "format-refs=index:click_format_refs",
        ]
    },
)
