from setuptools import setup, find_packages

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="heidegger_index",
    version="1.0",
    description="Heidegger index",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "add-ref=index:click_add_ref",
            "add-rel=index:click_add_rel",
            "find-ref=index:click_find_ref",
            "format-refs=index:click_format_refs",
        ]
    },
)
