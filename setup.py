import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.rst")) as f:
    CHANGES = f.read()

requires = ["celery", "pyramid", "pyramid_cors", "SQLAlchemy"]

tests_require = ["WebTest >= 1.3.1", "pytest >= 3.7.4", "pytest-cov"]  # py3 compat

setup(
    name="pyramid_celeryjobs",
    version="0.0",
    description="Pyramid Celery job tracking",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="",
    author_email="",
    url="",
    keywords="web pyramid",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    extras_require={"testing": tests_require},
    install_requires=requires,
    entry_points={},
)
