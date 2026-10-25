from glob import glob
from setuptools import setup

package_name = 'hcw_perception'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='HCW team',
    maintainer_email='adekeyedamilarelekan@gmail.com',
    description='AprilTag perception for the healthcare-waste robot',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'tag_monitor = hcw_perception.tag_monitor:main',
            'verifier = hcw_perception.verifier:main',
        ],
    },
)
