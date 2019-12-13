from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='salem',
      version='1.0',
      packages=find_packages(),
      install_requires=requirements,
      package_data={'salem': ['data/*.txt', 'web/*']},
      entry_points={'console_scripts': ['salem = salem.__main__:main']}
)
