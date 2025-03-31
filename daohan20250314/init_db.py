from bson import ObjectId
import json
import os

# 模拟数据库的内存存储
class MockDatabase:
    def __init__(self):
        self.categories = []
        self.websites = []
    
    def insert_one(self, collection, data):
        if collection == 'categories':
            self.categories.append(data)
        elif collection == 'websites':
            self.websites.append(data)
        return data['_id']
    
    def save_to_json(self):
        # 将数据保存到JSON文件
        data = {
            'categories': [self._convert_objectid(cat) for cat in self.categories],
            'websites': [self._convert_objectid(site) for site in self.websites]
        }
        
        with open('example_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f'示例数据已保存到 {os.path.abspath("example_data.json")}')
    
    def _convert_objectid(self, data):
        # 将ObjectId转换为字符串以便JSON序列化
        result = {}
        for key, value in data.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            else:
                result[key] = value
        return result

def init_database():
    # 创建模拟数据库
    mock_db = MockDatabase()
    
    # 添加分类
    categories = [
        {
            '_id': ObjectId(),
            'name': 'AI模型官网',
            'description': '各大AI模型的官方网站',
            'icon': 'fa5s.robot',
            'order': 1
        },
        {
            '_id': ObjectId(),
            'name': 'AI工具',
            'description': '实用的AI工具和应用',
            'icon': 'fa5s.tools',
            'order': 2
        },
        {
            '_id': ObjectId(),
            'name': 'AI学习资源',
            'description': 'AI学习和教程网站',
            'icon': 'fa5s.graduation-cap',
            'order': 3
        },
        {
            '_id': ObjectId(),
            'name': 'AI新闻资讯',
            'description': 'AI行业新闻和资讯网站',
            'icon': 'fa5s.newspaper',
            'order': 4
        },
        {
            '_id': ObjectId(),
            'name': 'AI研究机构',
            'description': '全球顶尖AI研究机构和实验室',
            'icon': 'fa5s.flask',
            'order': 5
        },
        {
            '_id': ObjectId(),
            'name': 'AI社区论坛',
            'description': 'AI开发者和爱好者社区',
            'icon': 'fa5s.users',
            'order': 6
        }
    ]
    
    # 插入分类数据
    category_ids = {}
    for category in categories:
        result = mock_db.insert_one('categories', category)
        category_ids[category['name']] = category['_id']
    
    # 添加网站数据
    websites = [
        # AI模型官网
        {
            '_id': ObjectId(),
            'name': 'ChatGPT',
            'url': 'https://chat.openai.com',
            'description': 'OpenAI开发的对话式AI模型',
            'category_id': category_ids['AI模型官网'],
            'icon': 'https://chat.openai.com/favicon.ico',
            'tags': ['对话模型', 'OpenAI', 'GPT']
        },
        {
            '_id': ObjectId(),
            'name': 'Claude',
            'url': 'https://claude.ai',
            'description': 'Anthropic开发的AI助手',
            'category_id': category_ids['AI模型官网'],
            'icon': 'https://claude.ai/favicon.ico',
            'tags': ['对话模型', 'Anthropic']
        },
        # AI工具
        {
            '_id': ObjectId(),
            'name': 'Midjourney',
            'url': 'https://www.midjourney.com',
            'description': 'AI图像生成工具',
            'category_id': category_ids['AI工具'],
            'icon': 'https://www.midjourney.com/favicon.ico',
            'tags': ['AI绘画', '图像生成']
        },
        {
            '_id': ObjectId(),
            'name': 'Copy.ai',
            'url': 'https://www.copy.ai',
            'description': 'AI文案写作助手',
            'category_id': category_ids['AI工具'],
            'icon': 'https://www.copy.ai/favicon.ico',
            'tags': ['写作助手', '营销文案']
        },
        # AI学习资源
        {
            '_id': ObjectId(),
            'name': 'Fast.ai',
            'url': 'https://www.fast.ai',
            'description': '实用深度学习课程',
            'category_id': category_ids['AI学习资源'],
            'icon': 'https://www.fast.ai/favicon.ico',
            'tags': ['深度学习', '教程', '课程']
        },
        {
            '_id': ObjectId(),
            'name': 'Kaggle',
            'url': 'https://www.kaggle.com',
            'description': '数据科学和机器学习社区',
            'category_id': category_ids['AI学习资源'],
            'icon': 'https://www.kaggle.com/favicon.ico',
            'tags': ['数据科学', '比赛', '教程']
        },
        # AI新闻资讯
        {
            '_id': ObjectId(),
            'name': 'AI News',
            'url': 'https://artificialintelligence-news.com',
            'description': 'AI行业新闻和分析',
            'category_id': category_ids['AI新闻资讯'],
            'icon': 'https://artificialintelligence-news.com/favicon.ico',
            'tags': ['新闻', '资讯', '分析']
        },
        {
            '_id': ObjectId(),
            'name': 'Synced',
            'url': 'https://syncedreview.com',
            'description': 'AI技术新闻和深度报道',
            'category_id': category_ids['AI新闻资讯'],
            'icon': 'https://syncedreview.com/favicon.ico',
            'tags': ['新闻', '深度报道', '评论']
        }
    ]
    
    # 插入网站数据
    for website in websites:
        mock_db.insert_one('websites', website)
        
    # 保存数据到JSON文件
    mock_db.save_to_json()

if __name__ == '__main__':
    init_database()
    print('数据库初始化完成！')