from typer import Typer

from . import auth
from . import calendar
from . import event
from . import sharing
from . import user


def create_app():
    """Inicializa o aplicativo."""

    app = Typer(
        help="Markit CLI",
        name="markit",
        add_completion=False,
        no_args_is_help=True,
        rich_markup_mode="rich",
    )

    app.add_typer(event.app, name="event")
    app.add_typer(user.app, name="user")
    app.add_typer(calendar.app, name="calendar")
    app.add_typer(sharing.app, name="sharing")
    app.add_typer(auth.app)

    return app
