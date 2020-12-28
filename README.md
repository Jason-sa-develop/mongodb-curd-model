# mongodb-curd-model

# 1.前言
我们都知道python中有一个很强大mongodb orm框架就是mongoengine，他可以运用到django、flask 等框架中
但是很多时候，该框架可能不太适合我们，我们可能需要更加灵活，自定义的mongodb数据库模型

当前project就是基于pymongo，封装一层类，即自定义数据库模型类：CRUDMixin



# 2.使用
1.创建一个集合类（一个集合对应一个类）
```
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
```
# 插入单个文档
## 方法一
obj1 = User(name="Jack", age=30, sex="M").save()


## 方法二
user1 = {
    "name": "Eric",
    "age": 25,
    "sex": "M"
}
obj2 = User(**user1).save()

# 插入多个文档
user2 = [
    {"name": "Xander", "age": 27, "sex": "M"},
    {"name": "Koko", "age": 20, "sex": "F"},
    {"name": "Gigi", "age": 17, "sex": "F"},
]
for u in user2:
    t2 = User(**u).save()
```

3.查询数据
```
# 查询单条数据（返回对象）
u1 = User.find_one(name="Jack")
print(u1.id, u1.name)

# 查询单条数据（返回字典）
u2 = User.find_one(name="Jack").to_dict()
print(u2.get("id"), u2.get("name"))

# 查询多条数据
u3 = User.find(sex="F")
for i in u3:
    print(i.id, i.name, i.age)
```

4.更新数据
```
u1 = User.find_one(name="Koko")
u1.age = 30  # 更新数据
u1.save()    # 保存更新
```

5.删除数据
```
# 删除单条数据
u1 = User.find_one(name="Jack").delete()
print(t4)
```

6.聚合查询
```
pipeline = [{
    "$match": {"name": "Eric"}
}]
res = User.aggregate(pipeline)
print(res)
```

7.分页查询
```
# query：查询条件、page：当前页数、limit：每页显示数据条目数
r = User.query_paginate(query={}, page=1, limit=10)
print(r)
```