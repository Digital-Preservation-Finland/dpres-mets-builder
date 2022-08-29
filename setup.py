from setuptools import setup


setup(
    name="dpres-mets-builder",
    packages=["mets_builder"],
    package_dir={
        "mets_builder": "mets_builder"
    },
    install_requires=[
        "lxml",
        "mets@git+https://gitlab.ci.csc.fi/dpres/mets.git@develop#egg=mets",
        "xml_helpers@git+https://gitlab.ci.csc.fi/dpres/xml-helpers.git"
        "@develop#egg=xml_helpers"
    ],
    python_requires=">=3.6",
    use_scm_version=True
)
