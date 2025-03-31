from bson import ObjectId

class Website:
    def __init__(self, name, url, category_id, description=None, icon=None, tags=None, order=0, _id=None):
        self._id = _id if _id else ObjectId()
        self.name = name
        self.url = url
        self.category_id = category_id
        self.description = description
        self.icon = icon  # 网站图标URL或Base64编码
        self.tags = tags or []  # 网站标签列表
        self.order = order  # 添加order字段
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name'),
            url=data.get('url'),
            category_id=data.get('category_id'),
            description=data.get('description'),
            icon=data.get('icon'),
            tags=data.get('tags', []),
            order=data.get('order', 0),  # 添加order字段，默认为0
            _id=data.get('_id')
        )
    
    def to_dict(self):
        return {
            '_id': self._id,
            'name': self.name,
            'url': self.url,
            'category_id': self.category_id,
            'description': self.description,
            'icon': self.icon,
            'tags': self.tags,
            'order': self.order  # 添加order字段
        }
    
    def __str__(self):
        return f"Website(id={self._id}, name={self.name}, url={self.url})"