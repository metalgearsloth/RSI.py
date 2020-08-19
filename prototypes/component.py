class PrototypeComponent:
    def __init__(self,
                 ptype,
                 **kwargs):
        self.ptype = ptype
        self.kwargs = kwargs

    def to_dict(self) -> dict:
        result = {"type": self.ptype}
        result.update(self.kwargs)
        return result
