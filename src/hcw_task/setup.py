from glob import glob
from setuptools import setup

package_name = 'hcw_task'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='HCW team',
    maintainer_email='adekeyedamilarelekan@gmail.com',
    description='Task manager and simulated magnet',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'task_manager = hcw_task.task_manager:main',
            'magnet = hcw_task.magnet:main',
            'request = hcw_task.request:main',
        ],
    },
)
