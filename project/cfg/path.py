# 中心端产品线
center_host = "http://10.87.22.2:8000"
list_systems = "{}/api/compliance/systems".format(center_host)  # 获取业务系统列表
list_devices = "{}/api/compliance/devices".format(center_host)  # 获取接入设备列表

# 发布任务
task_host = ""
task = "{}/api/compliance/tasks".format(task_host)

# Web 端认证, 用来实现中心端产品线到等保中心端的单点登录认证
web_auth_host = ""
web_auth_api = "{}/api/compliance/web_auth".format(web_auth_host)

# request 超时时长
timeout = 1
