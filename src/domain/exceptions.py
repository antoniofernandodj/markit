class UsuarioNaoEncontradoException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EmailJaCadastradoException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class PermissaoNaoConcedidaException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CalendarioNaoEncontradoException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EventoNaoEncontradoException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CompartilhamentoJaExistenteException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CompartilhamentoNaoEncontradoException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
