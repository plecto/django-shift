from setuptools import setup, find_packages

setup(
    name = 'django-shift',
    version = '0.1',
    description = '',
    long_description = '',
    author = 'Kristian Oellegaard',
    author_email = 'kristian@kristian.io',
    url = 'https://github.com/plecto/django-shift',
    packages = find_packages(
        exclude = [
            'example_project',
        ],
    ),
    zip_safe=False,
    include_package_data = True,
    install_requires=[
        'Django>=1.8',
    ],
    classifiers = [
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ]
)