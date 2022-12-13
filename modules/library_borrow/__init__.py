from trytond.pool import Pool


def register():
    Pool.register(module="library", type_="model")

    Pool.register(module="library", type_="wizard")
