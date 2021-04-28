from os.path import join, dirname, basename
from json import load

data = open(join(dirname(__file__), basename(__file__).replace('.py', '.json')))
vendors = load(data)
del data
