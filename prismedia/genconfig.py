from os.path import join, abspath, isfile, dirname
from os import listdir
from shutil import copyfile


def genconfig():
    path = join(dirname(__file__), 'config')
    files = [f for f in listdir(path) if isfile(join(path, f))]

    for f in files:
        copyfile(join(path, f), f)


if __name__ == '__main__':
    genconfig()
