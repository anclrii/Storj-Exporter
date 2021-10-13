def jsonFileLoader(filename):
    def loader(req, context):
        with open(filename, 'r') as f:
            return json.loads(f.read())
    return loader

