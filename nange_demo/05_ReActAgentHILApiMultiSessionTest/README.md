是在以上功能之上再新增功能:

支持动态调整会话的过期时间
支持用户登录到系统后自动打开最近一次使用的会话，若无则新建会话
支持历史会话管理和历史会话恢复
支持修剪短期记忆中的聊天历史以满足上下文对token数量或消息数量的限制
支持读取和写入长期记忆(如用户偏好设置等)


4.2 功能测试
进入05_ReActAgentHILApiMultiSessionTest文件夹下运行脚本进行测试，支持多用户访问
首先运行后端服务 python 01_backendServer.py
再运行前端服务 python 02_frontendServer.py

4.2.1 测试HIL 对工具请求进行人类反馈
使用python实现的一个模拟酒店预订的工具book_hotel
其需传入的参数为:{hotel_name}
使用python实现的一个计算两个数的乘积的工具multiply
其需传入的参数为:{a:float, b:float}
测试流程:
(1)输入 'yes' 接受工具调用
调用工具预定如家酒店(软件园店)
(2)输入 'no' 拒绝工具调用
调用工具预定桔子酒店(软件园店)
(3)输入 'edit' 修改工具参数后调用工具
调用工具预定全季酒店
{"hotel_name": "全季酒店(软件园店)"}
(4)输入 'response' 不调用工具直接反馈信息
调用工具预定汉庭酒店
把酒店名称换为：汉庭酒店(软件园店)，再调用工具预定

4.2.2 测试客户端和服务端故障恢复
(1)这个118.79815,32.01112经纬度对应的地方是哪里
(2)夫子庙的经纬度坐标是多少
(3)112.10.22.229这个IP所在位置
(4)上海的天气如何
(5)我要从上海豫园骑行到上海人民广场，帮我规划下路径
(6)我要从上海豫园步行到上海人民广场，帮我规划下路径
(7)我要从上海豫园驾车到上海人民广场，帮我规划下路径
(8)我要从上海豫园坐公共交通到上海人民广场，帮我规划下路径
(9)测量下从上海豫园到上海人民广场驾车距离是多少
(10)在上海豫园附近的中石化的加油站有哪些，需要有POI的ID
(11)POI为B00155LA8A的详细信息
(12)在上海豫园周围10公里的中石化的加油站
高德地图 MCP Server介绍:
为实现 LBS 服务与 LLM 更好的交互，高德地图 MCP Server 现已覆盖12大核心服务接口，提供全场景覆盖的地图服务
包括地理编码、逆地理编码、IP 定位、天气查询、骑行路径规划、步行路径规划、驾车路径规划、公交路径规划、距离测量、关键词搜索、周边搜索、详情搜索等
链接地址:https://lbs.amap.com/api/mcp-server/summary
具体提供的接口详情介绍:
(1)地理编码
name='maps_regeocode'
description='将一个高德经纬度坐标转换为行政区划地址信息'
inputSchema={'type': 'object', 'properties': {'location': {'type': 'string', 'description': '经纬度'}}, 'required': ['location']}
(2)逆地理编码
name='maps_geo'
description='将详细的结构化地址转换为经纬度坐标。支持对地标性名胜景区、建筑物名称解析为经纬度坐标'
inputSchema={'type': 'object', 'properties': {'address': {'type': 'string', 'description': '待解析的结构化地址信息'}, 'city': {'type': 'string', 'description': '指定查询的城市'}}, 'required': ['address']}
(3)IP 定位
name='maps_ip_location'
description='IP 定位根据用户输入的 IP 地址，定位 IP 的所在位置'
inputSchema={'type': 'object', 'properties': {'ip': {'type': 'string', 'description': 'IP地址'}}, 'required': ['ip']}
(4)天气查询
name='maps_weather'
description='根据城市名称或者标准adcode查询指定城市的天气'
inputSchema={'type': 'object', 'properties': {'city': {'type': 'string', 'description': '城市名称或者adcode'}}, 'required': ['city']}
(5)骑行路径规划
name='maps_bicycling'
description='骑行路径规划用于规划骑行通勤方案，规划时会考虑天桥、单行线、封路等情况。最大支持 500km 的骑行路线规划'
inputSchema={'type': 'object', 'properties': {'origin': {'type': 'string', 'description': '出发点经纬度，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '目的地经纬度，坐标格式为：经度，纬度'}}, 'required': ['origin', 'destination']}
(6)步行路径规划
name='maps_direction_walking'
description='步行路径规划 API 可以根据输入起点终点经纬度坐标规划100km 以内的步行通勤方案，并且返回通勤方案的数据'
inputSchema={'type': 'object', 'properties': {'origin': {'type': 'string', 'description': '出发点经度，纬度，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '目的地经度，纬度，坐标格式为：经度，纬度'}}, 'required': ['origin', 'destination']}
(7)驾车路径规划
name='maps_direction_driving'
description='驾车路径规划 API 可以根据用户起终点经纬度坐标规划以小客车、轿车通勤出行的方案，并且返回通勤方案的数据。'
inputSchema={'type': 'object', 'properties': {'origin': {'type': 'string', 'description': '出发点经度，纬度，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '目的地经度，纬度，坐标格式为：经度，纬度'}}, 'required': ['origin', 'destination']}
(8)公交路径规划
name='maps_direction_transit_integrated'
description='公交路径规划 API 可以根据用户起终点经纬度坐标规划综合各类公共（火车、公交、地铁）交通方式的通勤方案，并且返回通勤方案的数据，跨城场景下必须传起点城市与终点城市'
inputSchema={'type': 'object', 'properties': {'origin': {'type': 'string', 'description': '出发点经度，纬度，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '目的地经度，纬度，坐标格式为：经度，纬度'}, 'city': {'type': 'string', 'description': '公共交通规划起点城市'}, 'cityd': {'type': 'string', 'description': '公共交通规划终点城市'}}, 'required': ['origin', 'destination', 'city', 'cityd']}
(9)距离测量
name='maps_distance'
description='距离测量 API 可以测量两个经纬度坐标之间的距离,支持驾车、步行以及球面距离测量'
inputSchema={'type': 'object', 'properties': {'origins': {'type': 'string', 'description': '起点经度，纬度，可以传多个坐标，使用分号隔离，比如120,30;120,31，坐标格式为：经度，纬度'}, 'destination': {'type': 'string', 'description': '终点经度，纬度，坐标格式为：经度，纬度'}, 'type': {'type': 'string', 'description': '距离测量类型,1代表驾车距离测量，0代表直线距离测量，3步行距离测量'}}, 'required': ['origins', 'destination']}
(10)关键词搜索
name='maps_text_search'
description='关键词搜，根据用户传入关键词，搜索出相关的POI'
inputSchema={'type': 'object', 'properties': {'keywords': {'type': 'string', 'description': '搜索关键词'}, 'city': {'type': 'string', 'description': '查询城市'}, 'types': {'type': 'string', 'description': 'POI类型，比如加油站'}}, 'required': ['keywords']}
(11)周边搜索
name='maps_search_detail'
description='查询关键词搜或者周边搜获取到的POI ID的详细信息'
inputSchema={'type': 'object', 'properties': {'id': {'type': 'string', 'description': '关键词搜或者周边搜获取到的POI ID'}}, 'required': ['id']}
(12)详情搜索
name='maps_around_search'
description='周边搜，根据用户传入关键词以及坐标location，搜索出radius半径范围的POI'
inputSchema={'type': 'object', 'properties': {'keywords': {'type': 'string', 'description': '搜索关键词'}, 'location': {'type': 'string', 'description': '中心点经度纬度'}, 'radius': {'type': 'string', 'description': '搜索半径'}}, 'required': ['location']})]