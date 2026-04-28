class RBProducts:
    def __init__(self, id: str | None = None, name: str | None = None, category_id: int | None = None, similar: str | None = None, sorting: str | None = None):
        self.id = id
        self.name = name
        self.category_id = category_id
        self.similar = similar
        self.sorting = sorting

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            "similar": self.similar,
            'sorting': self.sorting
        }