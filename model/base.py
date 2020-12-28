"""
    MongoDB 数据库模型的基类，该基类封装了所有MongoDB的CURD操作

"""
import time
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure,
    WriteConcernError,
    CollectionInvalid,
    ServerSelectionTimeoutError,
)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.devops


class CRUDMixin(object):
    @classmethod
    def find(cls, query=None, objects=True, **kwargs):
        """
        查询多条数据
        :param query: 查询条件（传入字典）
        :param objects: 是否将查询的数据转换为对象，True：是、False：否
        :param kwargs: 查询条件
        :return: 对象 or 字典
        """
        query = query or {}
        query.update(kwargs)

        col = cls.get_collection_name()

        try:
            result = list(col.find(query))
        except (ConnectionFailure, ServerSelectionTimeoutError):
            return Exception("mongodb：数据库连接失败")

        # 查询的数据必须为列表
        if not isinstance(result, list):
            raise TypeError("查询的数据不为列表，查询错误")

        if objects:
            return [cls(r) for r in result]

        return result

    @classmethod
    def find_one(cls, query=None, objects=True, **kwargs):
        """
        查询单条数据
        :param query: 查询条件（传入字典）
        :param objects: 是否将查询的数据转换为对象，True：是、False：否
        :param kwargs: 查询条件
        :return: 对象 or 字典
        """
        query = query or {}
        query.update(kwargs)

        col = cls.get_collection_name()
        try:
            result = col.find_one(query)
        except (ConnectionFailure, ServerSelectionTimeoutError):
            return Exception("mongodb：数据库连接失败")

        if objects:
            return cls(result)

        return result

    @classmethod
    def count(cls, query) -> int:
        """
        数据统计
        :param query: 查询条件
        :return: 统计数
        """
        col = cls.get_collection_name()
        return col.count_documents(query)

    @classmethod
    def get_collection_name(cls):
        return cls.__get_collection_name()

    @classmethod
    def __get_collection_name(cls):
        """
        获取派生类的集合名称
        派生类中定义集合名：__collection__ = "集合名"
        """
        attr_name = "__collection__"

        is_exist = hasattr(cls, attr_name)
        # 如果集合名不存在，则抛异常
        if not is_exist:
            raise CollectionInvalid("当前操作的类没有指定集合名：__collection__")

        # 获取集合名
        col = getattr(cls, attr_name)
        return db[col]

    @classmethod
    def aggregate(cls, pipeline, retry=False):
        """
        聚合查询
        :param pipeline: 查询条件
        :param retry: 是否重试，true：是、false：否(默认)
        :return:
        """
        col = cls.get_collection_name()
        if retry:  # 默认重试5次，每次出错，停顿0.002秒
            count = 0
            for _ in range(5):
                try:
                    result = col.aggregate(pipeline)
                    return list(result)
                except Exception as e:
                    count += 1
                    time.sleep(0.002)
                    continue
            if count == 5:
                return Exception(f"mongodb: 聚合查询失败，重试次数超过{count}次")

        result = col.aggregate(pipeline)
        return list(result)

    def save(self) -> (ObjectId, Exception):
        """
        保存数据，数据存在则更新，不存在则插入数据
        :return: 返回 objectid
        """
        data = self.to_dict()
        if data:
            col = self.get_collection_name()

            try:
                # 更新数据，拿到唯一标识
                if "id" in data:
                    _id = data.pop("id")
                    if _id:  # 必须不为None 才表示数据存在
                        if not isinstance(_id, ObjectId):
                            _id = ObjectId(_id)
                            col.update_one({"_id": _id}, {"$set": data})
                            return _id

                # 插入数据
                _id = col.insert_one(data).inserted_id
                return _id
            except (WriteConcernError, ConnectionError, ValueError):
                raise Exception("mongodb: 数据保存失败")

    def delete(self):
        """
        删除单条数据
        :return:
        """
        data = self.to_dict()
        if not data:
            return

        _id = data.pop("id")
        if not _id and "_id" in data:
            _id = data.pop("_id")

        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)

        try:
            col = self.get_collection_name()
            col.delete_one({"_id": _id})
        except (ConnectionError, AttributeError):
            return Exception(f"mongodb：{_id}数据删除失败")

    def to_dict(self):
        """
        获取派生类中的所有属性，并将object id转换为str类型
        :return: 字典
        """
        data = self.__dict__
        if data and "_id" in data and data.get("_id"):
            data["id"] = str(data.pop("_id"))
        elif data and "id" in data and data.get("id"):
            data["id"] = str(data.pop("id"))

        return data

    @classmethod
    def query_paginate(cls, query, page, limit, sdate=None, edate=None):
        """
        分页/时间查询
        :param query: 查询规则
        :param page: 当前页面（第几页）
        :param limit: 每页显示的行数
        :param sdate: 开始时间
        :param edate: 结束时间
        :return:
        """
        # 匹配规则
        query = query or {}

        # 分页查询
        page = int(page) if page else 1
        skip = (page - 1) * limit

        # 时间查询
        if all([sdate, edate]):
            query.setdefault("t", {"$gte": sdate, "$lte": edate})

        pipeline = [
            {
                "$match": query
            }, {
                "$sort": {"t": -1}
            }, {
                "$skip": skip
            }, {
                "$limit": limit
            }
        ]

        # 查询数据
        datas = cls.aggregate(pipeline)

        # 数据统计
        count = cls.count(query)

        data = {"count": count, "page": page, "limit": limit, "d": datas}
        return data
