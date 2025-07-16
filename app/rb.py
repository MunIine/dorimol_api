class RBProductsByCategory:
    def __init__(self, category_id: int, sorting: str | None = None):
        self.category_id = category_id
        self.sorting = sorting

    def to_dict(self) -> dict:
        data = {'category_id': self.category_id, 'sorting': self.sorting}
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data
class RBProductsByIdOrName:
    def __init__(self, id_or_name: str, category_id: int | None = None, sorting: str | None = None):
        self.arg = id_or_name
        self.category_id = category_id
        self.sorting = sorting

    def to_dict(self) -> dict:
        data = {'arg': self.arg, 'category_id': self.category_id, 'sorting': self.sorting}
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data