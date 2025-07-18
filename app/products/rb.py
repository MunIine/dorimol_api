class RBProductsByCategory:
    def __init__(self, category_id: int, sorting: str | None = None):
        self.category_id = category_id
        self.sorting = sorting

    def to_dict(self) -> dict:
        return {'category_id': self.category_id, 'sorting': self.sorting}
    
class RBProducts:
    def __init__(self, id: str | None = None, name: str | None = None, category_id: int | None = None, sorting: str | None = None):
        self.id = id
        self.name = name
        self.category_id = category_id
        self.sorting = sorting

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'sorting': self.sorting
        }