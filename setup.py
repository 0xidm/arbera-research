# arbera

from setuptools import setup, find_packages

setup(
    version="0.1.0",
    name='arbera',
    description="arbera",
    packages=["arbera"],
    scripts=[],
    include_package_data=True,
    keywords='',
    author="idm",
    author_email="",
    install_requires=[
        "pytest",
        "click",
        "trogon",
        "rich",
        "watchdog[watchmedo]",
        "hiplot",
        "pandas",
        "jupyterlab",
    ],
    license='proprietary',
    zip_safe=False,
)
