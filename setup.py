from setuptools import setup

setup(
    name="ahrl",
    version="0.0.1",
    license="MIT",
    python_requires=">=3.6",
    long_description=open("README.md").read(),
    url="http://github.com/rhaamo/ahrl",
    author="Dashie",
    author_email="dashie@sigpipe.me",
    install_requires=[
        "Flask",
        "SQLAlchemy",
        "WTForms",
        "WTForms-Alchemy",
        "SQLAlchemy-Searchable",
        "SQLAlchemy-Utils",
        "Flask-Bootstrap",
        "Flask-DebugToolbar",
        "Flask-Login",
        "Flask-Mail",
        "Flask-Migrate",
        "Flask-Principal",
        "Flask-Security",
        "Flask-SQLAlchemy",
        "Flask-Uploads",
        "Flask-WTF",
        "bcrypt",
        "psycopg2-binary",
        "unidecode",
        "Flask_Babelex",
        "texttable",
        "python-slugify",
        "flask-accept",
        "geohelper",
        "flask_testing",
        "parameterized",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov", "jsonschema"],
)
