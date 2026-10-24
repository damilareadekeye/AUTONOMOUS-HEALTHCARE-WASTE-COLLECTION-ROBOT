from glob import glob
from setuptools import setup

package_name = 'hcw_world'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/worlds', glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='HCW team',
    maintainer_email='adekeyedamilarelekan@gmail.com',
    description='Clinic world for the healthcare-waste robot',
    license='Apache-2.0',
)
