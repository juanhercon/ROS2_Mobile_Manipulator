from setuptools import find_packages, setup

package_name = 'mobile_ur3_controller'

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
    maintainer='juan',
    maintainer_email='juan@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': ['mobile_ur3_controller = mobile_ur3_controller.mobile_ur3_controller:main','mobile_ur3_pred = mobile_ur3_controller.mobile_ur3_pred:main','mobile_ur3_invisible = mobile_ur3_controller.mobile_ur3_invisible:main','resultados = mobile_ur3_controller.resultados',
        ],
    },
)
