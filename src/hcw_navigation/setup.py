from glob import glob
from setuptools import setup

package_name = 'hcw_navigation'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*')),
        ('share/' + package_name + '/maps', glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='HCW team',
    maintainer_email='adekeyedamilarelekan@gmail.com',
    description='Mapping and navigation for the healthcare-waste robot',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'map_clinic = hcw_navigation.map_clinic:main',
            'go_to = hcw_navigation.go_to:main',
        ],
    },
)
