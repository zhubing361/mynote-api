# elasticsearch

---

## 说明

 - eg

    index: index_name index_name1 索引名称

    field: field1 field2 field3 field4 字段名称

---

## 导入包 import

    ```python
    from elasticsearch import Elasticsearch
    from elasticsearch import helpers
    ```

---

## 连接(connect)

    ```python
    es = Elasticsearch(
        hosts={'127.0.0.1:9200'},  # 地址
        timeout=3600  # 超时时间
    )
    ```

---

## 接口(api)

- 分词测试

    post http://127.0.0.1:9200/_analyze {"analyzer":"ik_smart","text":"进口红酒"} # ['进口', '红酒']


- 索引操作

    - 创建索引
    
        put http://127.0.0.1:9200/index_name

        创建时指定分片数量

            指定三个主分片、1个副本分片

            {
                "settings" : {
                    "number_of_shards" : 3,
                    "number_of_replicas" : 1
                }
            }

        创建后修改副本分片数量

            修改副本分片数为2个

            put http://127.0.0.1:9200/index_name/_settings
            {
                "settings" : {
                    "number_of_replicas" : 2
                }
            }

    - 删除索引

        delete http://127.0.0.1:9200/index_name

    - 获取索引信息

        多个用逗号隔开

        get http://127.0.0.1:9200/index_name

    - 获取索引指定信息

        aliases、mappings、settings

        get http://127.0.0.1:9200/index_name/_settings

    - 获取全部索引信息

        get http://127.0.0.1:9200/_all

    - 打开、关闭索引

        _open、_close

        post http://127.0.0.1:9200/_open

    - 清空索引

        post http://127.0.0.1:9200/_delete_by_query

        {
            "query": {
                "match_all": {}
            }
        }

---

## 字段类型

- 字符串类型

    - text 

        支持分词，不用于排序

    - keyword

        数据不会分词建立索引

- 数值类型

    long、integer、short、byte、double、float、half_float、scaled_float

- 日期类型

- 布尔类型

- Range类型

    integer_range、float_range、long_range、double_range、date_range、ip_range

- 二进制类型

- 数组类型

    每个元素类型必须相同

- 对象类型

    json对象，索引用"."连接

- 嵌套类型(Nested)

    对象数组

- 地理类型(Geo)

- 地理坐标(Geo-points)

    https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-point.html

- 地理图形(Geo-Shape)

    https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-shape.html

- 其他类型

---

## 分词器

- standard

    默认分词器

- ik_smart、ik_max_word

    ik_smart: 做最粗粒度的拆分
    ik_max_word: 做最细粒度的拆分
    
    中文分词

        https://github.com/medcl/elasticsearch-analysis-ik

    安装：

        ./bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v6.3.0/elasticsearch-analysis-ik-6.3.0.zip

    自定义词库

        1、 ./plugins/ik/config/custom/zz_keyword.dic
            一行一个词

        2、远程词库
            ./plugins/ik/config/IKAnalyzer.cfg.xml
                ```xml
                <?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
                <properties>
                        <comment>IK Analyzer 扩展配置</comment>
                        <!--用户可以在这里配置自己的扩展字典 -->
                        <entry key="ext_dict">custom/zz_keyword.dic</entry>
                        <!--用户可以在这里配置自己的扩展停止词字典-->
                        <entry key="ext_stopwords"></entry>
                        <!--用户可以在这里配置远程扩展字典 -->
                        <!-- <entry key="remote_ext_dict">words_location</entry> -->
                        <!--用户可以在这里配置远程扩展停止词字典-->
                        <!-- <entry key="remote_ext_stopwords">words_location</entry> -->
                </properties>
                ```

            eg: words_location => http://xxx.com/remote_keyword.txt
                
                一行一个词，使用 "\n"

                返回两个header： Last-Modified、ETag 这两个header发生变化，将使用新的词更新词库

---

## 索引(index)

 - 创建 - eg： index_name
    ```python
    body = {
        'mappings': {
            "notes": {
                "properties": {
                    "note_id": {
                        "type": "long"
                    },
                    "updated_at": {
                        "type": "float"
                    },
                    "created_at": {
                        "type": "float"
                    },
                    "title": {
                        "type": "text",
                        "search_analyzer": "ik_smart",
                        "analyzer": "ik_max_word",
                        "fields": {
                            "keyword": {
                                "ignore_above": 256,
                                "type": "keyword"
                            }
                        }
                    },
                    "content": {
                        "type": "text",
                        "search_analyzer": "ik_smart",
                        "analyzer": "ik_max_word",
                        "fields": {
                            "keyword": {
                                "ignore_above": 256,
                                "type": "keyword"
                            }
                        }
                    }
                }
            }
            
        }
    }
    res = es.index(index="index_name", body = body)
    ```

 - 重建索引 https://elasticsearch-py.readthedocs.io/en/latest/helpers.html
    ```python
    host_src = '127.0.0.1:9200'
    host_des = '127.0.0.1:9200'
    es_src=Elasticsearch(host_src)   #原索引所在ES集群的host
    es_des=Elasticsearch(host_des)   #新索引所在ES集群的host

    body={"query":{"match_all":{}}}  #遍历原索引

    helpers.reindex(client=es_src,source_index='index_name',target_index='index_name1',target_client=es_des,query=body,chunk_size=1000) #重建索引
    ```

 - 查看

    es.cat.indices()

 - 删除

    es.indices.delete("index_name")

---
## 数据
---
## 搜索(Search) DSL语法

- 基本查询

    es.search(index='index_name') # 默认返回前10条数据

- 过滤字段

    filter_path =['hits.hits._source.field1','hits.hits._source.field2']
    es.search(index='index_name', filter_path=filter_path) 

- 条件查询

    - 查询分页
    ```python
        body = {
            'from': 0,
            'size': 20 # 默认10 最大值不超过10000
        }
        es.search(index='index_name', body=body)
    ```

    - 模糊查询

        - match
            ```python
            #模糊匹配，指定字段名，对输入内容分词再匹配
            body = {
                'query': {
                    'match': {
                        'field1': '我爱你中国'
                    }
                },
            　　'size': 20
            }
            es.search(index='index_name', body=body)
            ```

        - match_phrase
            ```python
            # 对输入内容分词，但是需要结果中也包含所有的分词，而且顺序要求一样
             body = {
                'query': {
                    'match_phrase': {
                        'field1': '我爱你中国'
                    }
                },
            }
            es.search(index='index_name', body=body, size=20)
            ```

        - 多字段查询 multi_match
            ```python
            body = {
                "query":{
                    "multi_match":{
                        "query":"我爱你中国",  # 指定查询内容，注意：会被分词
                        "fields":["field1", "field2"]  # 指定字段
                    }
                }
            }
            ```
        - query_string
            ```python
            # 在所有字段中搜索， 支持通配符*、AND、OR、必须包含+ 不包含-
            body = {
                "query":{
                    "query_string":{
                        "query":"*Exception AND -*exception=null",  # 指定查询内容
                        "default_field":"field1"  # 指定字段
                    }
                }
            }

            # 指定多个字段
            body = {
                "query": {
                    "query_string": {
                        "fields": [
                            "field1",
                            "field2"
                        ],
                        "query": "查询内容"
                    }
                },
            }
            ```

    - 精准单值查询 term
        ```python
        body ={   
            'query':{
                'term':{
                    'field1.keyword': '我爱你中国'  # 查询内容等于“我爱你中国的”的数据。查询中文，在字段后面需要加上.keyword
        　　　　     'field2': 'I love China'
                }
            }
        }
        ```
    - 精准多值查询 terms
        ```python
        body ={   
            "query":{
                "terms":{
                    "field1": ["我爱你中国", "I love China"]  # 查询内容等于 “我爱你中国的” 或 "I love China" 的数据。
                }
            }
        }
        ```

    - 前缀查询 prefix
        ```python
        body = {
            'query': {
                'prefix': { 
                    'field1.keyword': '我爱你'  # 查询前缀是指定字符串的数据。查询中文，在字段后面需要加上.keyword
                }
            }
        }
        # 注：英文不需要加keyword
        ```
    
    - 通配符查询 wildcard
        ```python
        body = {
            'query': {
                'wildcard': {
                    'field1.keyword': '?爱你中*'  # ?代表一个字符，*代表0个或多个字符
                }
            }
        }
        # 注：此方法只能查询单一格式的（都是英文字符串，或者都是汉语字符串）。两者混合不能查询出来。
        ```

    - 正则查询 regexp
        ```python
        body = {
            'query': {
                'regexp': {
                    'field1': 'W[0-9].+'   # 使用正则表达式查询
                }
            }
        }
        ```

    - 多条件查询 bool

        - must：[] 各条件之间是and的关系
            ```python
            body = {
                "query":{
                    "bool":{
                        'must': [{"term":{'field1.keyword': '我爱你中国'}},
                                {'terms': {'field2': ['I love', 'China']}}]
                    }
                }
            }
            ```

        - should: [] 各条件之间是or的关系
            ```python
            body = {
                "query":{
                    "bool":{
                        'should': [{"term":{'field1.keyword': '我爱你中国'}},
                                {'terms': {'field2': ['I love', 'China']}}]
                    }
                }
            }
            ```

        - must_not：[]各条件都不满足
            ```python
            body = {
                "query":{
                    "bool":{
                        'must_not': [{"term":{'field1.keyword': '我爱你中国'}},
                                {'terms': {'field2': ['I love', 'China']}}]
                    }
                }
            }
            ```

        - bool嵌套bool
            ```python
            # field1、field2条件必须满足的前提下，field3、field4满足一个即可
            body = {
                "query":{
                    "bool":{
                        "must":[{"term":{"field1":"China"}},  #  多个条件并列  ，注意：must后面是[{}, {}],[]里面的每个条件外面有个{}
                                {"term":{"field2.keyword": '我爱你中国'}},
                                {'bool': {
                                    'should': [
                                        {'term': {'field3': 'Love'}},
                                        {'term': {'field4': 'Like'}}
                                    ]
                                }}
                        ]
                    }
                }
            }
            ```
        
        - 存在字段查询 exists
            ```python
            body = {
                'query': {
                    'exists': {'field': 'field1'}  # 查询存在field1的数据
                }
            }


            # exists、bool嵌套查询
            # 存在field1的情况下，field2的值必须为指定字段
            body = {
                "query":{
                    "bool":{
                        "must":[{'exists': {'field': 'field1'}},
                                {"term":{"field2.keyword": '我爱你中国'}},
                            ]
                    }
                }
            }
            ```

        - 大于小于查询
            ```python
            body = {
                "query": {
                    "range": {
                        "field1":{
                            "gte": 3,  # 大于
                            "lt": 20  # 小于
                        }
                    }
                }
            }
            ```

        - nest，json数据查询
            ```python
            body = {
                'query': {
                    'nested': {
                        'path': 'field1',  # 指定json数据的字段
                        'query': {  # 指定查询方式
                            'term': {'field1.field2': '我爱你中国'}  # 根据field1里面的field2数据查询
                        }
                    }
                }
            }


            # nest、bool嵌套查询
            body = {
                'query': {
                    'bool': {
                        'must': [
                            {'term':{"field3" : "I love China"}},
                            {'nested': {  # json查询
                                'path': 'field1',
                                'query': {  # 指定查询方式
                                    'term': {'field1.field2': '我爱你中国'}  # 根据field1里面的field2数据查询
                                }
                            }}
                        ]
                    }
                }
            }
            ```

- 排序
    ```python
    body = {
        "query":{  # 指定条件，可以使用以上的任何条件等查询数据。然后再对符合条件的数据进行排序
            "match_all":{}
        },
        "sort":{  # 对满足条件的数据排序
            "field1":{                 # 根据field1字段排序
                "order":"asc"       # asc升序，desc降序
            }
        }
    }

    # 多字段排序，注意顺序！写在前面的优先排序
    body = {
        "query":{
            "match_all":{}
        },
        "sort":[{
            "field1":{
                "order":"asc"      # 先根据field1升序
            }},
            {"field2":{               # 后根据field2字段升序排序
                "order":"asc"      # asc升序，desc降序
            }}],
    }
    ```


