class RBProduct:
    def __init__(self, id: str | None = None,
                 name: str | None = None):
        self.id = id
        self.name = name

        
    def to_dict(self) -> dict:
        data = {'id': self.id, 'name': self.name}
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data