from setuptools import setup


setup(
    name="dpres-mets-builder",
    packages=["mets_builder"],
    package_dir={
        "mets_builder": "mets_builder"
    },
    install_requires=[
        "lxml"
    ],
    python_requires=">=3.6",
    use_scm_version=True
)
