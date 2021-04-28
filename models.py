from os.path import join, dirname, basename
from json import load

data = open(join(dirname(__file__), basename(__file__).replace('.py', '.json')))
models = load(data)
models_ids = []
for vendor in models.keys():
    for model in models[vendor]:
        models_ids.append(vendor+':'+model[1])
del data
