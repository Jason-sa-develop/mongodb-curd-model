from model.base import CRUDMixin

class User(CRUDMixin):
    __collection__ = "users"

    def __init__(self, data=None, **kwargs):
        data = data or {}
        data.update(kwargs)

        """ 自定义mongo文档属性 """
        self.id = data.get("_id")
        self.name = data.get("name")
        self.age = data.get("age")
        self.sex = data.get("sex")