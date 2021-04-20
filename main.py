from flask import Flask, request
import requests
import json
import os
import logging
import re
import time

app = Flask(__name__)

# 格言API的Key，接口文档地址：https://www.tianapi.com/apiview/26
tianApiKey= ''

#------------Config part-----------------
projects = {
    # struct is regular(string) => dict
    'projectA-exmaple-com':{
        # 企业微信群聊机器人token
        'token':'AAAAAA-1234-7890-000-123456789000',
        # 各个环境演示项目的地址：对应命名空间后缀，比如“api-baidu-com-staging”，如果你还有更多环境，可以继续追加
        'staging_url':'https://staging.example.com',
        'production_url':'https://www.example.com'
    },
    'projectB-example-com':{
        'token':'',
        'testing_url':''
    }
}
api = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='

#------------Config part end-----------------

class WebhookMessage:
    def __init__(self):
        self.EventMeta = {}
        self.Text = ''
        self.Project = [i for i in projects.values()][0]
        self.Time = ''

    def __str__(self):
        return self.toString()

    def toString(self):
        #根据namespace后缀判断环境
        env = self.EventMeta['namespace'].split('-')[-1]
        motto = getMotto()
        result = "创建" if self.EventMeta['reason'] != 'created' else "更新"
        return ('# <font color=\"info\">'+self.getProgramName()+'</font>程序已部署 \n '
                '> 运行环境：['+env.capitalize()+']('+self.Project[env+'_url']+') \n '
                '> 构建结果：<font color=\"comment\">'+result+'</font> \n '
                '> '+motto+' .' )

    def getProgramName(self):
        fullName = self.EventMeta['name'].split('/')[-1]
        return fullName.split('-')[0]


def getMotto():
    apiUrl = 'http://api.tianapi.com/txapi/dictum/index?key='+tianApiKey+'&num=1'
    result = requests.get(apiUrl)
    try:
        content = json.loads(result.text)['newslist'][0]
        return content['content'] + ' --- ' + content['mrname']
    except Exception as e:
        pass
    return 'have fun'

def sendMessage(message):
    if message['eventmeta']['kind'] == 'pod' and message['eventmeta']['reason'] != 'deleted':
        for namespace in projects:
            if re.match(namespace,message['eventmeta']['namespace']):
                playground = WebhookMessage()
                playground.Time = message['time']
                playground.Text = message['text']
                playground.EventMeta = message['eventmeta']
                playground.Project = projects[namespace]
                headers = {'Content-Type': 'application/json;charset=utf-8'}
                body = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": playground.toString()
                    }
                }
                webhook = api+projects[namespace]['token']
                # 睡它个半分钟再发送
                logging.warning("=========开始沉睡==========")
                time.sleep(30)
                requests.post(webhook, json.dumps(body), headers=headers)
                logging.warning("==========发送成功==========")


@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'GET':
        return ('wow,"GET"? realy?',200,None)
    else:
        message = json.loads(request.data)
        sendMessage(message)
        return ('你的骚话我已经帮你发送出去了...', 200, None)

if __name__ == '__main__':
    # 打印运行配置
    print(app.config)
    app.run(port=8080,host="0.0.0.0")
