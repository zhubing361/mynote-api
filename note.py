# coding:utf8
from elasticsearch import Elasticsearch
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_restful import Api, Resource
from flask import Flask, request
import math
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['MONGO_URI'] = 'mongodb://mongo_rs1:30001/flask'

api = Api(app)
mongo = PyMongo(app)
db_notes = mongo.db.notes

# 时间格式化


def show_date_time(data):
    data['created_at'] = datetime.utcfromtimestamp(
        data['created_at']+28800).strftime("%Y-%m-%d %H:%M:%S")
    data['updated_at'] = datetime.utcfromtimestamp(
        data['updated_at']+28800).strftime("%Y-%m-%d %H:%M:%S")

    return data

# 备份到本地


def backup_to_local(data):
    file_path = "./docs/backup/" + str(data['title']) + ".md"
    with open(file_path, mode='w+', encoding='utf-8') as file_obj:
        content = file_obj.read()
        new_content = str(data['content'])
        if(content != new_content and new_content != ""):
            file_obj.write(data['content'])


class Note(Resource):
    def get(self, note_id):
        note = db_notes.find_one({'note_id': int(note_id)})
        if note is not None:
            note.pop('_id')
            note = show_date_time(note)
            return dict(result='success', data=note)
        return dict(result='error', message='未找到相关记录')

    def delete(self, note_id):
        result = db_notes.delete_one({'note_id': int(note_id)})
        count = result.deleted_count
        if count > 0:
            return dict(result='success', message='%d 条记录被删除' % count)
        return dict(result='error', message='删除失败')

    def put(self, note_id):
        old_note = db_notes.find_one({'note_id': int(note_id)})
        if old_note is None:
            return dict(result='error', message='数据不存在')
        dt = datetime.today().timestamp()
        note = request.get_json()
        note['created_at'] = old_note['created_at']
        note['updated_at'] = dt
        result = db_notes.replace_one({'note_id': int(note_id)}, note)
        count = result.modified_count
        if count > 0:
            backup_to_local(note)
            return dict(result='success', message='%d 条记录被修改' % count)
        return dict(result='error', message='修改失败')


class NoteList(Resource):
    def get(self):
        api_source = 'es'  # mongo es
        if(api_source == 'mongo'):
            return self.get_list_from_mongo()
        else:
            return self.get_list_from_es()

    def post(self):
        note = request.get_json()
        old_note = db_notes.find_one({'note_id': int(note['note_id'])})
        if old_note is not None:
            return dict(result='error', message='id重复')

        dt = datetime.today().timestamp()
        note['created_at'] = dt
        note['updated_at'] = dt
        note_id = db_notes.insert_one(note).inserted_id
        if note_id is not None:
            backup_to_local(note)
            return dict(result='success', message='添加成功')
        return dict(result='error', message='添加失败')

    def get_list_from_mongo(self):
        inputs = request.args.to_dict()
        page = int(inputs.get('page', 1))
        page_size = int(inputs.get('page_size', 10))
        fillter_keyword = inputs.get('keyword', '')

        if(page_size < 10):
            page_size = 10
        fillter_dict = {}
        if(len(fillter_keyword) > 0):
            fillter_dict = {'title': fillter_keyword}
        notes = db_notes.find(fillter_dict).limit(
            page_size).skip(page_size * (page - 1))
        note_list = []
        for note in notes:
            note.pop('_id')
            note = show_date_time(note)
            note_list.append(note)

        total = db_notes.count_documents({})
        total_page = math.ceil(total/page_size)
        return dict(result='success', data={'items': note_list, 'pagination': {'total': total, 'currentPage': page, 'perPage': page_size, 'totalPage': total_page}})

    def get_list_from_es(self):
        inputs = request.args.to_dict()
        page = int(inputs.get('page', 1))
        page_size = int(inputs.get('page_size', 10))
        fillter_keyword = inputs.get('keyword', '')

        if(page_size < 10):
            page_size = 10

        es = Elasticsearch(
            hosts={'elasticsearch:9200'},  # 地址
            timeout=3600  # 超时时间
        )
        # https://www.zhihu.com/column/c_1385286066535071744
        # body指定查询条件 https://blog.csdn.net/sinat_38682860/article/details/107693969
        body = {
            'sort': [
                {
                    'updated_at': {
                        'order': 'desc'
                    }
                },
                "_score"
            ],
            'from': page_size * (page - 1),
            'size': page_size,
            "highlight": {  # 全字段高亮
                "require_field_match": False,
                "fields": {
                    "*": {
                        "pre_tags": [
                            "<strong><font color='red'>"
                        ],
                        "post_tags": [
                            "</font></strong>"
                        ]
                    }
                }
            }
        }
        if(len(fillter_keyword) > 0):
            body['query'] = {
                "bool": {
                    "should": [
                        {
                            'multi_match': {
                                'query': fillter_keyword,
                                "fields": ["title", "content"]
                            }
                        },
                        {
                            "match": {
                                "tags": fillter_keyword
                            }
                        }
                    ]
                }
            }

        result = es.search(index='flask', body=body)
        result_arr = []
        for value in result['hits']['hits']:
            result_arr += [value]
        note_list = []
        for note in result_arr:
            note.pop('_id')
            note['_source'] = show_date_time(note['_source'])
            temp_note = note['_source']
            if(note.get('highlight', None) is not None):
                title = note['_source']['title']
                content = note['_source']['content']
                if(note['highlight'].get('title', None) is not None):
                    title = note['highlight']['title'][0]
                if(note['highlight'].get('content', None) is not None):
                    content = note['highlight']['content'][0]

                highlight_item = {
                    "title": title, "content": content}
                temp_note = dict(note['_source'], **highlight_item)
            note_list.append(temp_note)

        # note_list = result
        total = result['hits']['total']['value']
        total_page = math.ceil(total/page_size)
        return dict(result='success', data={'items': note_list, 'pagination': {'total': total, 'currentPage': page, 'perPage': page_size, 'totalPage': total_page}})


api.add_resource(NoteList, '/notes')
api.add_resource(Note, '/notes/<note_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


# gunicorn note:app -c gunicorn.conf.py
