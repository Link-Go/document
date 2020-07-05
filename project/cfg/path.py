# Web 端认证, 用来实现中心端产品线到等保中心端的单点登录认证
web_auth_host = ""
web_auth_api = "{}/api/compliance/web_auth".format(web_auth_host)
web_auth_host = "http://127.0.0.1:8080"
test_web_auth_api = "http://127.0.0.1:8080/sangfor/auth"  # 自测使用

# 中心端产品线
center_host = "http://10.87.22.2:8000"
list_systems = "{}/api/compliance/systems".format(center_host)  # 获取业务系统列表
list_devices = "{}/api/compliance/devices".format(center_host)  # 获取接入设备列表

test_center_host = "http://127.0.0.1:8080"
test_list_systems = "{}/sangfor/systems".format(test_center_host)
test_list_devices = "{}/sangfor/devices".format(test_center_host)

# 产品线客户端登录路径
client_logging = ""
test_client_logging = "http://127.0.0.1:8080/"

# 发布任务
task_host = ""
task = "{}/api/compliance/tasks".format(task_host)

# request 超时时长
TIMEOUT = 1
