from setuptools import find_packages,setup
# -e will trigger the setup.py when we install the requirements.txt


def get_requirements():
    requirements=[]
    with open('requirements.txt') as file_obj:
        requirements=file_obj.readlines()
        requirements=[r.replace(" \n",'') for r in requirements]
        if '-e .' in requirements:
            requirements.remove('-e .')

    return requirements
#
setup(name="Traffic prediction",
      version='0.0.1'
      
      ,author='ChinmayaK10',
      author_email="chinmayakulkarni10@gmail.com",
      packages=find_packages(),
      install_requires=get_requirements()
      
      
      )