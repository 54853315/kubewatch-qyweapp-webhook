# kubewatch-qyweapp-webhook

这是一个可以让 kubewatch 推送 webhook 给 **企业微信群机器人** 的 Python3 脚本。

![example](https://www.crazyphper.com/tools/qywechat-demo.png)

## 特性

- 支持 kubewatch 接收到 POD 状态变更为 `created` 或 `updated` 时，进行企业微信群机器人 markdown 消息发送
- 还会发一条世界经典格言

## 文件目录介绍

```shell
.
├── README.md                       # 本文件
├── Dockerfile                      # Kubernetes 服务部署配置脚本
├── deployment.yaml                 # 部署配置文件
├── requirements.txt                # 所需资源文本
├── main.py                         # 主运行程序脚本
```

## 使用方法

### 1. 在 main.py 中指定 Kubernetes 命名空间

Kubernetes 的 namespaces 应该具有命名规范，例如一个叫做 `趣味畅玩` 的游戏项目，有验收环境 (staging) 和正式生产环境 (production)，那么 namespaces 可以是 `fun-game-staging` 和 `fun-game-production`。

> 识别环境字符串所使用的是 `string.split('-')[-1]`

这样做的好处是脚本能够识别出各个环境的演示网址，并拼接在 markdown 中进行企业微信机器人消息推送。

请修改 main.py 中的 `projects` 变量：
```python
projects = {
    # 结构是常规 (string) => dict
    'projectA-namespace': {
        # 企业微信群聊机器人 token
        'token': 'AAAAAA-1234-7890-000-123456789000',
        # 环境演示项目的地址
        'staging_url': 'https://staging.exampleA.com',
        'production_url': 'https://www.exampleA.com'
    },
    'projectB-namespace': {
        'token': 'BBBBBB-1234-7890-000-123456789000',
        'testing_url': 'https://testing.exampleB.com',
        'other_url': 'https://other.exampleC.com'
    }
}
```

### 2. 设置格言 API Key

修改 main.py 中的 `tianApiKey`。

这里使用 [天行数据](https://www.tianapi.com/apiview/26) 的名言警句接口，每天有 100 次免费 API 额度。

如果不需要格言功能，可以修改 `getMotto()` 方法返回你需要的文本内容。

### 3. 部署服务

```shell
docker build -t webhook/qyweapp-kubewatch:latest . 

docker push webhook/qyweapp-kubewatch:latest # 建议推送到自己的私有镜像中心

vim deployment.yaml # 请先修改脚本中的镜像地址

kubectl apply -f deployment.yaml
```

> M1 芯片必须使用 [docker buildx build](https://betterprogramming.pub/how-to-actually-deploy-docker-images-built-on-a-m1-macs-with-apple-silicon-a35e39318e97) 和参数 `--platforms linux/amd64`

### 4. 测试运行效果

测试用 kube-watch 格式 JSON：

```json
{"eventmeta": {"kind": "pod", "name": "project-example-com-staging/backend-xxxx-yyy", "namespace": "project-example-com-staging", "reason": "created"}, "text": "A `pod` in namespace `project-example-com-staging` has been `created`:\n`project-example-com-staging/backend-xxxx-yyy`", "time": "2021-02-26T08:12:08.758617965Z"}
```

使用 curl 发送：
```shell
curl -H "Content-Type: application/json" -X POST -d '{"eventmeta": {"kind": "pod", "name": "project-example-com-staging/backend-xxxx-yyy", "namespace": "project-example-com-staging", "reason": "created"}, "text": "A `pod` in namespace `project-example-com-staging` has been `created`:\n`project-example-com-staging/backend-xxxx-yyy`", "time": "2021-02-26T08:12:08.758617965Z"}' "http://wechat-webhook:8080"
```

## 修改 markdown 内容

参考 [企业微信机器人配置说明](https://developer.work.weixin.qq.com/document/path/91770)

## 调整 kube-watch 内容

参考 [Go webhook](https://github.com/bitnami-labs/kubewatch/blob/master/pkg/handlers/webhook/webhook.go) 和 [代码](https://github.com/bitnami-labs/kubewatch/blob/master/pkg/handlers/webhook/webhook.go)

## 参与贡献

1. Fork 本仓库
2. 新建 `Feat_xxx` 分支
3. 提交代码
4. 新建 Pull Request