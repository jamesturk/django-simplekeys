from setuptools import setup, find_packages

setup(
    name='django-simplekeys',
    version="0.5.2",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description='Django API Key management & validation',
    author='James Turk',
    author_email='dev@jamesturk.net',
    license='MIT License',
    url='http://github.com/jamesturk/django-simplekeys/',
    long_description=open('README.rst').read(),
    platforms=["any"],
    install_requires=[
        "Django",
    ],
    extras_require={
        'dev': [
            'freezegun',
            'flake8',
            'sphinx',
            'sphinx-rtd-theme',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
