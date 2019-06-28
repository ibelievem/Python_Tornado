
from bson.objectid import ObjectId

# 生成objectid
def create_objectid(self, str=None):
    try:
        object_id = ObjectId(str)
    except:
        object_id = ''
    return object_id