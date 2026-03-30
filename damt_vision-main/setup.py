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
            'decoder = damt_vision.cam_decoder:main',
            'encoder = damt_vision.cam_encoder:main',
            'pac_Ai = damt_vision.pacman_ai:main',
            'pac_logik = damt_vision.pacman_logik:main',
            'cam_combined = damt_vision.cam_combined:main',
            'controllhub = damt_vision.controllhub:main',
        ],
    },
)
