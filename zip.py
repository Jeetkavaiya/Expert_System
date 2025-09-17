import zipfile
with zipfile.ZipFile('Expert_system.zip', 'w') as myzip:
    myzip.write('Originals')
    myzip.write('modified_images')
    myzip.write('random')
    myzip.write('test_system.py')
    myzip.write('forensics_detective.py')
    myzip.write('rules.py')
    myzip.write('requirements.txt')
    myzip.write('README.md')