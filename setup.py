# -*- coding: utf-8 -*-

from setuptools import setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


def set_entry_points():
    r = {'console_scripts': [
        'opigen-export_font_def=opigen.config:export_font_def',
        'opigen-export_color_def=opigen.config:export_color_def',
        'opigen-export_attr_map=opigen.config:export_attr_map',
    ]}
    return r


setup(
    name='opigen',
    version='1.1.0',
    description='OPI Generation for CS-Studio and Phoebus',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/archman/opi-generator',
    license='APACHE',
    author='Tong Zhang',
    author_email='zhangt@frib.msu.edu',
    packages=[
        'opigen.renderers', 'opigen.renderers.css',
        'opigen.contrib', 'opigen.config', 'opigen.renderers.phoebus',
        'opigen',
    ],
    package_dir={
        'opigen.renderers': 'opigen/renderers',
        'opigen.renderers.css': 'opigen/renderers/css',
        'opigen.renderers.phoebus': 'opigen/renderers/phoebus',
        'opigen.contrib': 'opigen/contrib',
        'opigen.config': 'opigen/config',
        'opigen': 'opigen',
    },
    include_package_data=True,
    install_requires=['lxml'],
    keywords="CS-Studio Phoebus OPI XML",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points=set_entry_points(),
)
