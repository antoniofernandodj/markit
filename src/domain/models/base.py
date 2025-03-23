class DomainModel:
    def __str__(self) -> str:
        fields = ', '.join(f'{k}={v}' for k, v in vars(self).items() if not k.startswith('_'))
        return f'{self.__class__.__name__}({fields})'

    def __repr__(self) -> str:
        return self.__str__()

    def get_id(self) -> str:
        return getattr(self, 'id')
