# Copyright 2018-2019 Bernardo Fontes <https://github.com/labcodes/mocks_context/>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.

#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

with open("README.md") as fd:
    long_description = fd.read()

with open("VERSION") as fd:
    version = fd.read().strip()

setup(
    name="mocks_context",
    version=version,
    description="A Python lib to help unit tests with Mock's management",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Bernardo Fontes',
    maintainer='Bernardo Fontes',
    maintainer_email='bernardoxhc@gmail.com',
    url="https://github.com/labcodes/mocks_context",
    license='GNU Lesser General Public License version 3',
    packages=find_packages(),
    python_requires='>=3.6',
    keywords="tdd mock testing test refactoring",
)
