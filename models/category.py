from bson import ObjectId

class Category:
    def __init__(self, name, icon=None, description=None, order=0, parent_id=None, _id=None):
        self._id = _id if _id else ObjectId()
        self.name = name
        self.icon = icon  # 图标名称，使用Font Awesome图标
        self.description = description
        self.order = order  # 排序顺序
        self.parent_id = parent_id  # 父分类ID，如果为None则为顶级分类
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name'),
            icon=data.get('icon'),
            description=data.get('description'),
            order=data.get('order', 0),
            parent_id=data.get('parent_id'),
            _id=data.get('_id')
        )
    
    def to_dict(self):
        return {
            '_id': self._id,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'order': self.order,
            'parent_id': self.parent_id
        }
    
    def __str__(self):
        return f"Category(id={self._id}, name={self.name})"