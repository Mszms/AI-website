import json
import os
from pymongo import MongoClient
from bson import ObjectId

class DatabaseManager:
    def __init__(self):
        # 加载示例数据
        self.data = self._load_example_data()
        self.websites = self.data.get('websites', [])
        self.categories = self.data.get('categories', [])

    def _get_user_data_dir(self):
        """获取用户数据目录，用于在打包为exe后保存数据"""
        # 在Windows上使用AppData/Local目录
        app_data = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'AI网站导航系统')
        # 确保目录存在
        if not os.path.exists(app_data):
            try:
                os.makedirs(app_data)
            except Exception as e:
                print(f"创建用户数据目录失败: {e}")
        return app_data

    def _load_example_data(self):
        # 从JSON文件加载示例数据
        data = {'websites': [], 'categories': []}
        
        # 首先尝试从用户数据目录加载
        try:
            user_data_dir = self._get_user_data_dir()
            user_json_path = os.path.join(user_data_dir, 'user_data.json')
            if os.path.exists(user_json_path):
                with open(user_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"从用户数据目录加载数据成功: {user_json_path}")
                    return data
        except Exception as e:
            print(f"从用户数据目录加载数据失败: {e}")
        
        # 如果用户数据目录没有数据，尝试从原始位置加载
        try:
            # 使用绝对路径加载示例数据
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(current_dir, 'example_data.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"从原始位置加载数据成功: {json_path}")
        except Exception as e:
            print(f"从原始位置加载数据失败: {e}")
            
        return data
    
    def _convert_id(self, id_str):
        # 将字符串ID转换为ObjectId或保持原样
        try:
            return ObjectId(id_str)
        except:
            return id_str
            
    def add_website(self, website_data):
        # 确保website_data包含_id字段
        if '_id' not in website_data:
            website_data['_id'] = str(ObjectId())
        
        # 确保关键字段为正确的类型
        if 'name' in website_data:
            website_data['name'] = str(website_data['name'])
        if 'url' in website_data:
            website_data['url'] = str(website_data['url'])
        if 'description' in website_data:
            website_data['description'] = str(website_data['description']) if website_data['description'] is not None else None
            
        # 添加网站数据到内存
        self.websites.append(website_data)
        
        # 将更新后的数据保存到JSON文件，实现持久化存储
        self._save_data_to_json()
        
        return website_data['_id']
        
    def _save_data_to_json(self):
        """将当前数据保存到JSON文件，实现数据持久化"""
        # 准备数据，确保ObjectId被转换为字符串
        data = {
            'categories': [self._convert_id_to_str(cat) for cat in self.categories],
            'websites': [self._convert_id_to_str(site) for site in self.websites]
        }
        
        # 首先尝试保存到用户数据目录
        try:
            user_data_dir = self._get_user_data_dir()
            user_json_path = os.path.join(user_data_dir, 'user_data.json')
            with open(user_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"数据成功保存到用户数据目录: {user_json_path}")
            return True
        except Exception as e:
            print(f"保存到用户数据目录失败: {e}")
        
        # 如果保存到用户数据目录失败，尝试保存到原始位置
        try:
            # 获取JSON文件路径
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            json_path = os.path.join(current_dir, 'example_data.json')
            
            # 写入JSON文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"数据成功保存到原始位置: {json_path}")
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
            
    def _convert_id_to_str(self, data):
        """将数据中的ObjectId转换为字符串"""
        result = {}
        for key, value in data.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            else:
                result[key] = value
        return result

    def get_website(self, website_id):
        website_id = self._convert_id(website_id)
        for website in self.websites:
            if str(website.get('_id')) == str(website_id):
                return website
        return None

    def get_websites_by_category(self, category_id):
        category_id = self._convert_id(category_id)
        websites = [w for w in self.websites if str(w.get('category_id')) == str(category_id)]
        # 按order字段排序
        return sorted(websites, key=lambda x: x.get('order', 0))
        
    def get_websites_by_category_recursive(self, category_id):
        """获取指定分类及其所有子分类下的网站"""
        category_id = self._convert_id(category_id)
        
        # 获取直接属于该分类的网站
        websites = self.get_websites_by_category(category_id)
        
        # 获取所有子分类
        child_categories = []
        for category in self.categories:
            if category.get('parent_id') and str(category.get('parent_id')) == str(category_id):
                child_id = str(category.get('_id'))
                child_categories.append(child_id)
                # 递归获取子分类的网站
                websites.extend(self.get_websites_by_category_recursive(child_id))
        
        return websites

    def get_all_websites(self):
        # 按order字段排序返回所有网站
        return sorted(self.websites, key=lambda x: x.get('order', 0))

    def update_website(self, website_id, website_data):
        website_id = self._convert_id(website_id)
        
        # 确保更新的字段为正确的类型
        if 'name' in website_data:
            website_data['name'] = str(website_data['name'])
        if 'url' in website_data:
            website_data['url'] = str(website_data['url'])
        if 'description' in website_data:
            website_data['description'] = str(website_data['description']) if website_data['description'] is not None else None
            
        for i, website in enumerate(self.websites):
            if str(website.get('_id')) == str(website_id):
                self.websites[i].update(website_data)
                # 将更新后的数据保存到JSON文件，实现持久化存储
                self._save_data_to_json()
                return True
        return False

    def delete_website(self, website_id):
        website_id = self._convert_id(website_id)
        for i, website in enumerate(self.websites):
            if str(website.get('_id')) == str(website_id):
                del self.websites[i]
                # 将更新后的数据保存到JSON文件，实现持久化存储
                self._save_data_to_json()
                return True
        return False

    def add_category(self, category_data):
        # 确保category_data包含_id字段
        if '_id' not in category_data:
            category_data['_id'] = str(ObjectId())
        
        self.categories.append(category_data)
        # 将更新后的数据保存到JSON文件，实现持久化存储
        self._save_data_to_json()
        return category_data['_id']

    def get_category(self, category_id):
        category_id = self._convert_id(category_id)
        for category in self.categories:
            if str(category.get('_id')) == str(category_id):
                return category
        return None

    def get_all_categories(self):
        # 按order字段排序返回所有分类
        return sorted(self.categories, key=lambda x: x.get('order', 0))

    def update_category(self, category_id, category_data):
        category_id = self._convert_id(category_id)
        for i, category in enumerate(self.categories):
            if str(category.get('_id')) == str(category_id):
                self.categories[i].update(category_data)
                # 将更新后的数据保存到JSON文件，实现持久化存储
                self._save_data_to_json()
                return True
        return False

    def delete_category(self, category_id):
        """删除分类及其下的所有网站和子分类"""
        try:
            category_id = self._convert_id(category_id)
            
            # 查找要删除的分类
            category_found = False
            for i, category in enumerate(self.categories):
                if str(category.get('_id')) == str(category_id):
                    # 删除分类
                    del self.categories[i]
                    category_found = True
                    break
            
            if not category_found:
                return False
            
            # 查找并删除所有子分类及其网站
            child_categories = []
            for category in list(self.categories):
                if category.get('parent_id') and str(category.get('parent_id')) == str(category_id):
                    child_id = str(category.get('_id'))
                    child_categories.append(child_id)
                    # 递归删除子分类
                    self.delete_category(child_id)
            
            # 删除该分类下的所有网站
            self.websites = [w for w in self.websites if str(w.get('category_id')) != str(category_id)]
            
            # 将更新后的数据保存到JSON文件，实现持久化存储
            self._save_data_to_json()
            
            return True
        except Exception as e:
            print(f"删除分类时出错: {e}")
            return False

    def search_websites(self, keyword):
        keyword = keyword.lower()
        results = []
        for website in self.websites:
            if (keyword in website.get('name', '').lower() or 
                keyword in website.get('description', '').lower() or 
                any(keyword in tag.lower() for tag in website.get('tags', []))):
                results.append(website)
        return results