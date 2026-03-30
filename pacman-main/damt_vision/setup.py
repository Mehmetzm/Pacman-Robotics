from setuptools import find_packages, setup

package_name = 'damt_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'rclpy', 'numpy', 'opencv-python'],
    zip_safe=True,
    maintainer='damt',
    maintainer_email='ahcelik@uni-osnabrueck.de',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_decoder = damt_vision.camera_decoder:main',
            'camera_stream = damt_vision.camera_stream:main'
        ],
    },
)
