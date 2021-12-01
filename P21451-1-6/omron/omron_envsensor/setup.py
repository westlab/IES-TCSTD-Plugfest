from setuptools import setup
import omron_envsensor

setup(
    name = "omron_envsensor",
    version = omron_envsensor.__version__,
    description = ("OMRON 2JCIE-BL01 SENSOR"),
    entry_points={
        'console_scripts' : [
            'omron_env = run:main',
            'omron_csv = cat_csv:main',
        ],
    },
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ]
)
