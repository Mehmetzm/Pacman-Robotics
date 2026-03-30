from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'damt_game'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ahmet',
    maintainer_email='ahcelik@uni-osnabrueck.de',
    description='Pac-Man ROS2 game',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pacman_game = damt_game.main:main',
        ],
    },
)
