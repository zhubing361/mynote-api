# mongodb同步到elasticsearch

## 测试环境

windows11 - mongodb-server:5.0
docker - elasticsearch:7.3.2

mongo-connector

> pip install 'mongo-connector[elastic5]'
> pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 'mongo-connector[elastic5]'

elastic2-doc-manager

> pip install elastic2-doc-manager

pymongo

> pip install -i https://pypi.tuna.tsinghua.edu.cn/simple  pymongo==2.8

## 设置镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

## mongodb环境

- PRIMARY

    5.0
        # mongod.conf

            # for documentation of all options, see:
            #   http://docs.mongodb.org/manual/reference/configuration-options/

            # Where and how to store data.
            storage:
              dbPath: C:\Program Files\MongoDB\Server\5.0\data
            journal:
              enabled: true
            #  engine:
            #  wiredTiger:

            # where to write logging data.
            systemLog:
              destination: file
              logAppend: true
              path:  C:\Program Files\MongoDB\Server\5.0\log\mongod.log

            # network interfaces
            net:
              port: 27017
              bindIp: 127.0.0.1


            #processManagement:

            #security:

            #operationProfiling:

            replication:
              replSetName: dev_repl_set
            #sharding:

            ## Enterprise-Only Options:

            #auditLog:

            #snmp:
    rs0
        port: 40001
    rs1
        port: 40002
    rs2
        port: 40003

## 使用 mongo-connector

### mongodb开启集群

mongod --replSet 'dev_repl_set'

### 副本

https://docs.mongoing.com/

https://mongoing.com/docs/replication.html

- 配置
config = {_id: 'dev_repl_set', members: [
    {_id: 0, host: '127.0.0.1:27017',priority:1},
    {_id: 1, host: '127.0.0.1:40001'},
    {_id: 2, host: '127.0.0.1:40002'},
    {_id: 3, host: '127.0.0.1:40003'}]
}

config = {_id: 'docker_dev_repl_set', members: [
    {_id: 0, host: '127.0.0.1:30001',priority:1},
    {_id: 1, host: '127.0.0.1:30002'},
    {_id: 2, host: '127.0.0.1:30003'}]
}

- 初始化
// 不指定config时默认将当前节点加入，并指定为primary
rs.initiate(config)

- 修改配置
rs.reconfig(config)

- 添加复制集
rs.add("localhost:40001")
rs.add("localhost:40002")
rs.add("localhost:40003")

rs.add("127.0.0.1:30001")

- 验证
rs.conf()

- 状态
rs.status()

- 移除
rs.remove("localhost:40003")

- 将primay降为secondary
rs.stepDown()

### 启动
cd 'C:\Program Files\MongoDB\Server\rs0\bin'
.\mongod.exe --config ..\conf\mongo.conf

### 同步

mongo-connector -m <mongodb server hostname>:<replica set port> \
                -t <replication endpoint URL, e.g. http://localhost:8983/solr> \
                -d <name of doc manager, e.g., solr_doc_manager>

explain:
    -m mongodb-uri
    -t elasticsearch-uri
    -d doc-manager
eg:

- 命令行参数

 -- mongo to es
> mongo-connector -m 127.0.0.1:40001 -t 127.0.0.1:9200 -d elastic2_doc_manager -n flask.notes

 -- mongo to mongo
 -- https://github.com/yougov/mongo-connector/wiki/Usage-with-MongoDB
> mongo-connector -m 127.0.0.1:40001 -t 127.0.0.1:30001 -d mongo_doc_manager -n flask.notes


 -- https://github.com/yougov/mongo-connector/wiki
 
mongo-connector命令常用参数：
-a     mongo数据库用户名
-p     mongo数据库密码
-m     数据源地址，这里指的是mongo地址
-t     目标地址；指的是同步数据的目的地地址（es地址）
-d     指定使用的doc-manage
-n     指定要同步的db和collection，多个之间用‘，’隔开，默认全部同步
-i     指定同步的字段，默认同步所有的字段
-x     指定要忽略的db和collection
-c     指定启动是要加载的配置文件（两种启动加载参数方式：命令参数和配置文件）
----continue-on-error   一条数据同步失败之后，记录错误日志并转储，继续数据同步。默认停止同步操作

- 使用配置文件
> mongo-connector -c ./config/mongo_to_es_config.json

- 配置文件示例
    {
        "mainAddress": "127.0.0.1:40001",
        "authentication": {
            "adminUsername": "",
            "password": ""
        },
        "oplogFile": "./oplog/oplog.timestamp",
        "logging": {
            "type": "file",
            "filename": "./oplog/mongo-connector.log",
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
            "rotationWhen": "midnight",
            "rotationInterval": 1,
            "rotationBackups": 10
        },
        "namespaces": {
            "flask.notes": {}
        },
        "docManagers": [
            {
                "docManager": "elastic2_doc_manager",
                "targetURL": "127.0.0.1:9200",
                "bulkSize": 1000,
                "autoCommitInterval": 5
            }
        ]
    }

## 错误记录

> pip install pymongo==2.9.5
    error in pymongo setup command: use_2to3 is invalid.
        降低setuptools版本

## todo 升级到最新版本
pip install --upgrade setuptools
pip install --upgrade pymongo


## 说明
数据同步操作在virtualenv执行
    - pymongo 使用2.9.5版本

cd temp
./Scripts/activate
mongo-connector -c ./config/mongo_to_es_config.json

- pip freeze > requirements.txt
- pip install -r requirements.txt



