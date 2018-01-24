from setuptools import setup, find_packages
from beepboop import __version__

requirements = [
    'discord.py[voice]',
    'gtts',
    'giphypop',
    'psutil',
    'lxml'
]


if not __version__:
    raise RuntimeError('version is not set')

try:
    with open('README.md') as f:
        readme = f.read()
except FileNotFoundError:
    readme = ""

setup(name='beepboop',
      author='Brendon1555',
      author_email='brendon1555@gmail.com',
      url='https://github.com/brendon1555/BeepBoop',
      bugtrack_url='https://github.com/brendon1555/BeepBoop/issues',
      version=__version__,
      license='MIT',
      description='Discord bot built on discord.py',
      long_description=readme,
      maintainer_email='brendon1555@gmail.com',
      download_url='https://github.com/brendon1555/BeepBoop',
      include_package_data=True,
      packages=find_packages(),
      zip_safe=False,
      install_requires=requirements,
      platforms=['Any'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ],
      entry_points={
          'console_scripts': [
              'beepboop = beepboop.bot:main'
          ]
      }
     )
