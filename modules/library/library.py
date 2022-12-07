from trytond.model import ModelSQL, ModelView, fields

from modules import library


__all__ = [
    'Genre',
    'EditorGenreRelation',
    'Editor',
    'Author',
    'Book',
    'Exemplary',
    ]


class Genre(ModelSQL, ModelView):
    'Genre'
    __name__ = 'library.genre'

class EditorGenreRelation(ModelSQL):
    'Editor - Genre relation'
    __name__ = 'library.editor-library.genre'

    editor = fields.Many2One('library.editor', 'Editor', required=True, ondelete='CASCADE')
    genre = fields.Many2One('library.genre', 'Genre', required=True, ondelete='RESTRICT')

class Editor(ModelSQL, ModelView):
    'Editor'
    __name__ = 'library.editor'

    genres = fields.Many2Many('library.editor-library.genre', 'editor', 'genre', 'Genres')


class Author(ModelSQL, ModelView):
    'Author'
    __name__ = 'library.author'

    books = fields.One2Many('library.book', 'author', 'Books')


class Book(ModelSQL, ModelView):
    'Book'
    __name__ = 'library.book'

    author = fields.Many2One('library.author', 'Author', required=True)
    exemplaries = fields.One2Many('library.book.exemplary', 'book', 'Exemplaries')
    genre = fields.Many2One('library.genre', 'Genre', ondelete='RESTRICT', required=False)
    editor = fields.Many2One('library.editor', 'Editor', ondelete='CASCADE', required=True)


class Exemplary(ModelSQL, ModelView):
    'Exemplary'
    __name__ = 'library.book.exemplary'

    book = fields.Many2One('library.book', 'Book', ondelete='CASCADE', required=True)
