from trytond.model import ModelSQL, ModelView


__all__ = [
    'Author',
    'Book',
    'BookExemplary',
    'Editor',
    'Genre'
]


class Editor(ModelSQL, ModelView):
    """Editor

    Args:
        ModelSQL (ModelSQL): Define a model with storage in database.
        ModelView (ModelView): Define a model with views in Tryton.
    """
    __name__ = 'library.editor'


class Genre(ModelSQL, ModelView):
    """Genre

    Args:
        ModelSQL (ModelSQL): Define a model with storage in database.
        ModelView (ModelView): Define a model with views in Tryton.
    """
    __name__ = 'library.genre'


class Author(ModelSQL, ModelView):
    """Author

    Args:
        ModelSQL (ModelSQL): Define a model with storage in database.
        ModelView (ModelView): Define a model with views in Tryton.
    """
    __name__ = 'library.author'


class Book(ModelSQL, ModelView):
    """Book

    Args:
        ModelSQL (ModelSQL): Define a model with storage in database.
        ModelView (ModelView): Define a model with views in Tryton.
    """
    __name__ = 'library.book'


class Exemplary(ModelSQL, ModelView):
    """Exemplary

    Args:
        ModelSQL (ModelSQL): Define a model with storage in database.
        ModelView (ModelView): Define a model with views in Tryton.
    """
    __name__ = 'library.book.exemplary'
