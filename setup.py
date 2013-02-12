from setuptools import setup, find_packages
import os

version = '1.0.1-dev'

tests_require = ['zope.testing']

setup(name='collective.newrelic',
      version=version,
      description="Zope/Plone Newrelic instrumentation",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "TODO.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'newrelic'
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='collective.newrelic.tests.test_suite',
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=[],
      paster_plugins=[],
      )
