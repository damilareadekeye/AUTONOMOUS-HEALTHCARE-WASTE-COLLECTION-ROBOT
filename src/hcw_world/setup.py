import os
from glob import glob
from setuptools import setup

package_name = 'hcw_world'


def tree(src, dst):
    """data_files entries that copy the folder src (all sub-folders too) to share/<dst>."""
    out = []
    for folder, _, files in os.walk(src):
        files = [os.path.join(folder, f) for f in files if not f.startswith('.')]
        if files:
            out.append((os.path.join('share', package_name, dst, os.path.relpath(folder, src)).rstrip('./'), files))
    return out


setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/worlds', glob('worlds/*.sdf')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ] + tree('models', 'models'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='HCW team',
    maintainer_email='adekeyedamilarelekan@gmail.com',
    description='Clinic world for the healthcare-waste robot',
    license='Apache-2.0',
)
