from trytond.pool import Pool

import library
import wizard


def register():
    Pool.register(
        library.Genre,
        library.Editor,
        library.EditorGenreRelation,
        library.Author,
        library.Book,
        library.Exemplary,
        module="library",
        type_="model",
    )
    Pool.register(
        wizard.CreateExemplaries,
        wizard.CreateExemplariesParameters,
        module="library",
        type_="wizard",
    )
