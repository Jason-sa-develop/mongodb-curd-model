# mongodb-curd-model

# 1.前言
我们都知道python中有一个很强大mongodb orm框架就是mongoengine，他可以运用到django、flask 等框架中
但是很多时候，该框架可能不太适合我们，我们可能需要更加灵活，自定义的mongodb数据库模型

当前project就是基于pymongo，封装一层类，即自定义数据库模型类：CRUDMixin



# 2.使用
1.创建一个集合类（一个集合对应一个类）
```python
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
```

2.插入文档
```python
# 插入单个文档
t1 = User(name="Jack", age=30, sex="M").save()

user1 = {
    "name": "Eric",
    "age": 25,
    "sex": "M"
}
t2 = User(**user1).save()

# 插入多个文档
user2 = [
    {"name": "Xander", "age": 27, "sex": "M"},
    {"name": "Koko", "age": 20, "sex": "F"},
    {"name": "Gigi", "age": 17, "sex": "F"},
]
for u in user2:
    t2 = User(**u).save()
```
