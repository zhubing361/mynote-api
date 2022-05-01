# coding:utf8
import os
import time
from pymongo import MongoClient
from pymongo.database import Database, Collection
from datetime import datetime
import argparse


class NoteSync(object):
    """
    列出文件夹中的文件, 深度遍历
    :param root_dir: 根目录
    :param ext: 后缀名
    :param is_sorted: 是否排序，耗时较长
    :return: [文件路径列表, 文件名称列表]
    """

    def traverse_dir_files(self, root_dir, ext=None):
        files_list = []
        for parent, _, files in os.walk(root_dir):
            for name in files:
                if name.startswith('.'):  # 去除隐藏文件
                    continue
                if ext:  # 根据后缀名搜索
                    if name.endswith(ext):
                        files_list.append(
                            {'name': name, 'path': os.path.join(parent, name)})
                else:
                    files_list.append(
                        {'name': name, 'path': os.path.join(parent, name)})
        return files_list

    def parse_md_file(self, file_data):

        data = {
            'title': '',
            'content': '',
        }
        file_path = file_data.get('path')
        if not file_path:
            return None

        try:
            # with open(file_path, mode='r', encoding='utf-8') as file_obj:
            #     lines = file_obj.readlines()
            #     if len(lines) != 0:
            #         data['title'] = file_data['name']
            #     else:
            #         data['title'] = lines[0].replace('# ', '')
            #     if not data['title']:
            #         data['title'] = file_data['name']
            with open(file_path, mode='r', encoding='utf-8') as file_obj:
                data['content'] = file_obj.read()
        except IndexError as err:
            print(err)
            print(file_data)
            return None
        else:
            data['title'] = file_data['name']
            return data
        finally:
            file_obj.close()

    def add_data(self, note):
        client = MongoClient(
            host='127.0.0.1',
            port=30001,
            document_class=dict,
            tz_aware=False,
            connect=True,
        )
        db_notes = Collection(Database(client, 'flask'), 'notes')
        old_note = db_notes.find_one({'title': note['title']})
        if old_note is not None:
            return False

        dt = datetime.today().timestamp()
        now_timestamp = self.get_now_timestamp()
        note['note_id'] = now_timestamp
        note['created_at'] = dt
        note['updated_at'] = dt
        _id = db_notes.insert_one(note).inserted_id
        if _id is not None:
            return True
        return False

    def get_now_timestamp(self):
        return int(round(time.time() * 1000))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='markdown 文件扫描录入到mongodb')
    parser.add_argument('--path', type=str,
                        default='./', help='扫描的文件夹路径')
    args = parser.parse_args()

    notesync = NoteSync()
    result = notesync.traverse_dir_files(
        r'' + args.path, '.md')
    # print(result)
    count = 0
    for value in result:
        note_data = notesync.parse_md_file(value)
        if note_data is not None:
            notesync.add_data(note_data)
            count += 1
    print(count)
