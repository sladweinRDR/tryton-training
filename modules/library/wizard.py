import datetime
from multiprocessing import pool

from trytond.model import ModelView, fields
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import PYSONEncoder, Eval
from trytond.wizard import Wizard, StateView, StateTransition, StateAction
from trytond.wizard import Button

__all__ = [
    "CreateExemplaries",
    "CreateExemplariesParameters",
]


class CreateExemplaries(Wizard):
    "Create Exemplaries"
    __name__ = "library.book.create_exemplaries"
    start_state = "parameters"
    parameters = StateView(
        "library.book.create_exemplaries.parameters",
        "library.create_exemplaries_parameters_view_form",
        [
            Button("Cancel", "end", "tryton-cancels"),
            Button("Create", "create_exemplaries", "tryton-go-next", default=True),
        ],
    )
    create_exemplaries = StateTransition()
    open_exemplaries = StateAction("library.act_exemplary")

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update(
            {
                "invalid_model": "This action should be started from a book",
                "invalid_date": "You cannot purchase books in the future",
            }
        )

    def default_parameters(self, name):
        if self.parameters._default_values:
            return self.parameters._default_values

        if Transaction().context.get("active_model", "") != "library.book":
            self.raise_user_error("invalid_model")
        return {
            "acquisition_date": datetime.date.today(),
            "book": Transaction().context.get("active_id"),
            "acquisition_price": 0,
        }

    def transition_create_exemplaries(self):
        if (
            self.parameters.acquisition_date
            and self.parameters.acquisition_date > datetime.date.today()
        ):
            self.raise_user_error("invalid_date")
        Exemplary = Pool().get("library.book.exemplary")
        to_create = []
        while len(to_create) < self.parameters.number_of_exemplaries:
            exemplary = Exemplary()
            exemplary.book = self.paramaters.book
            exemplary.acquisition_date = self.parameters.acquisition_date
            exemplary.acquisition_price = self.parameters.acquisition_price
            exemplary.identifier = self.parameters.identifier_start + str(
                len(to_create) + 1
            )
            to_create.append(exemplary)
        Exemplary.save(to_create)
        self.parameters.exemplaries = to_create
        return "open_exemplaries"

    def do_open_exemplaries(self, action):
        action["pyson_domain"] = PYSONEncoder().encode(
            [("id", "in", [x.id for x in self.parameters.exemplaries])]
        )
        return action, {}


class CreateExemplariesParameters(ModelView):
    "Create Exemplaries Parameters"
    __name__ = "library.book.create_exemplaries.parameters"

    book = fields.Many2One("library.book", "Book", readonly=True)
    number_of_exemplaries = fields.Integer(
        "Number of exemplaries",
        required=True,
        domain=[("number_of_exemplaries", ">", 0)],
        help="The number of exemplaries that will be created",
    )
    identifier_start = fields.Char(
        "Identifier Start",
        required=True,
        help="The starting point of exemplaries identifiers",
    )
    acquisition_date = fields.Date("Acquisition Date")
    acquisition_price = fields.Numeric(
        "Acquisition Price",
        digits=(16, 2),
        domain=[("acquisition_price", ">=", "0")],
        help="The price that was paid per exemplary bought",
    )
    exemplaries = fields.Many2Many("library.book.exemplary", None, None, "Exemplaries")


class FuseBooks(Wizard):
    'Fuse books'
    __name__ = "library.book.fuse_books"
    start_state = "check_authors"
    check_authors = StateTransition()
    select_main = StateView('library.book.fuse_books.select_main',
        'library.fuse_books_select_main_view_form',[
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Preview', 'check_compatibility', 'tryton-go-next')
        ])
    check_compatibility = StateTransition()
    preview = StateView('library.book.fuse_books.preview',
    'library.fuse_books_preview_view_form', [
        Button('Previous', 'select_main', 'tryton-go-previous'),
        Button('Cancel', 'end', 'tryton-cancel'),
        Button('Merge', 'merge', 'tryton-go-next', default=True)
    ])
    merge = StateTransition()

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update(
            {
                "invalid_model": "This action should be started from a book",
                "multiple_author": "Books you chose have to be from the same author",
                "bad_matches": "The following fields will not be a perfect match: %(fields)s"
            }
        )

    def default_select_main(self, name):
        if self.select_main._default_values:
            return self.select_main._default_values
        Book = Pool().get('library.book')
        books = Book.browse(Transaction().context.get('active_ids'))
        if Transaction().context.get("active_model", "") != "library.book":
            self.raise_user_error("invalid_model")
        return {
            'selected_books': [x.id for x in books],
            'number_of_exemplaries': sum(x.number_of_exemplaries for x in books),
            'main_book': Transaction().context.get("active_id"),
        }

    def default_preview(self, name):
        book = {k: v for k, (v, _) in self._get_merge_values().items()}
        for fname in ['editor', 'genre', 'author']:
            book[fname] = book[fname].id if book[fname] else None
        book['title'] = self.select_main.main_book.title
        return {
            'final_book': [book],
            'number_of_exemplaries': self.select_main.number_of_exemplaries,
        }

    def transition_check_authors(self):
        if Transaction().context.get('active_model', '') != "library.book":
            self.raise_user_error('invalid_model')
        Book = Pool().get('library.book')
        books = Book.browse(Transaction().context.get('active_ids'))
        if len({x.author for x in books}) != 1:
            self.raise_user_error('multiple_authors')
        return 'select_main'

    def transition_check_compatibility(self):
        values = self._get_merge_values()
        bad_matches = [k for k, v in values.items() if not v[1]]
        if bad_matches:
            self.raise_user_warning('bad_matches_warning' + str(
                self.select_main.main_book.id), 'bad_matches',
                {'fields': ', '.join(bad_matches)})
        return 'preview'
    
    def transition_merge(self):
        pool = Pool()
        Book = pool.get('library.book')
        Exemplary = pool.get('library.book.exemplary')
        book = self.select_main.main_book
        for fname, (value, _) in self._get_merge_values().items():
            setattr(book, fname, value)
        book.save()
        other_books = [x for x in self.select_main.selected_books if x != book]
        Exemplary.write(sum([list(x.exemplaries) for x in other_books], []), 
            {'book': book.id})
        Book.delete(other_books)
        return 'end'

    def end(self):
        return 'reload'
    def _get_merge_fields(self):
        return ['isbn', 'editor', 'genre', 'summary', 'description',
            'publishing_date', 'cover', 'page_count', 'edition_stopped',
            'author']
    
    def _get_merge_values(self):
        result = {}
        for fname in self._get_merge_fields():
            main_value = getattr(self.select_main.main_book, fname, None)
            for book in self.select_main.selected_books:
                book_value = getattr(book, fname, None)
                if book_value is None:
                    continue
                if main_value is None:
                    main_value = book_value
                    continue
                result[fname] = (main_value, False)
                break
            else:
                result[fname] = (main_value, True)
        return result
        



class FuseBooksSelectMain(ModelView):
    'Fuse books select main'
    __name__ = "library.book.fuse_books.select_main"
    main_book = fields.Many2One('library.book', 'Main book', required=True,
        domain=[('id', 'in', Eval('selected_books'))])
    selected_books = fields.Many2Many('library.book', None, None, 'Selected books', readonly=True)
    number_exemplaries = fields.Integer('Number of exemplaries', readonly=True)


class FuseBooksPreview(ModelView):
    'Fuse books preview'
    __name__ = "library.book.fuse_books.preview"

    final_book = fields.One2Many('library.book', None, "Final book", 
        readonly=True)
    number_of_exemplaries = fields.Integer('Number of exemplaries',
        readonly=True)