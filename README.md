# 技术文档
github:https://github.com/ndce1041/secondhandwebsite

## 后端框架相关

### 1. 后端框架整体设计思路


主循环所在文件`runtime.py`
最终目标为创造一个轻量级，强拓展性，高性能高并发的高通用性后端框架

2.0以后对代码结构进行重构,引入协程,结合响应器模式和生成者消费者模式,极大提高了并发性.

#### 主要运行逻辑：
（1）.读取配置文件`xweb.conf`初始化原始socket后,记录其文件描述符并投入套接字队列`selector`中设置对应回调等待响应
（2）.同时注册路由`url`在路由中写入`默认无效路径回调函数`和`默认静态资源回调函数`。并且创建任务队列。
（3）.实例化响应器`reactor`和指定个数的处理器`handler`都按协程要求编写，开始执行协程loop。
（4）.`reactor`:  管理`selector`套接字池中的套接字接收到前端请求进入可读状态后交由`recv_data`接收数据，首先对比文件描述符，如果为原始套接字则表示将接收的为新套接字，接收后投入`selector`中；如果不是表示有可读的前端请求。将前端请求放入任务队列供处理器接取
（5）.`handler`:接收前端请求，每次接收1024字节数据，循环接收直至读空（需要用select判断是否读空否则协程中会持续堵塞，如果断开连接了会读取到0）。接收完毕交给`AnalysisRequest`对象解析，首先解析是否为http请求，如果是则返回请求路径,交给路由`url`寻找对应地址的回调函数，如果找到则将解析后的请求传入，否则执行默认无效路径回调函数。
（6）.请求完成后抛弃此socket或根据需要再次投入`selector`，完成此次http请求。获取下一个任务。

##### 注意事项：
* 一个应用应该具有至少一个回调函数，否则只会返回404。


一个最小系统应具有如下内容
```python
import runtime
import response_maker as rm

server = runtime.Server()

def index(request,key,rest):
    return rm.ResponseMaker().set_body("Hello World".encode("utf-8"))

server.url.add("/",index)
server.start()
```


### 2. 路由相关

路由系统的设计思路为高可读性，强拓展性，请求连接可以通过更深的路径传递参数
路由组件对应文件 `url_manage.py` 创建对象后执行 `url.add(path,func)` 即可创建对应节点，回调函数需要满足一定格式：

```python
def func(request,key,rest=[]):
    return response: bytes
```



其中`request`包含请求的所有信息；`key`中包含套接字本身，用来给回调函数更高级自由度，如果函数返回`False`则内核将不再管理此套接字，交由函数自行处理；`rest`为寻找到最深处回调后剩余的路径参数，例如只申请了`/index`节点，那么当请求为`/index/2/3`时`rest=[2,3]`;`response` 对象为构建响应的工具对象。

路由对象本身是在维护一个树状字典，每当添加路径时根据路径建立路径，通过递归将建立的路径更新到树状字典中。

##### 路由提供的API：

* 注意：后端路由位于`Server.url`
* `__init__(unfound=func)` 
* `.get(url)` 通过传入的路径获取对应回调
* `.add(url,func)` 生成路由节点
* `server.unfound` 该参数储存了unfound回调，为未找到可用回调时的默认回调函数 如果不设置将使用内部默认回调，修改此项可变更为自定义的回调函数
* 路由由内核自动创建，应用中一般只使用内核中的路由`server.url.add(url,func)`

### 3. 中间件

依靠python自带的装饰器语法编写，目前可用功能为在Content-Type确定时主动解析请求负载`body`，和验证`cookie`自动拦截非法请求

### 4. 默认静态回调

设计为忠诚的返回对应文件,匹配不同文件对应的`Content-Type`,可以时进行压缩处理

对应文件`static_resources_manager.py`

初始化时读取配置文件中`static_path`条目，初始化时自动注册到配置文件`static_url`条目对应路径，当请求为对应静态路径时，剩余参数（子文件路径）会传入函数`rest`参数中，如果文件为文本类型会自动调用`gzip`压缩。如果没有对应文件会返回`404`

例如`static_url="/static"`时，请求为`/static/img/a.css`,则根据路由规则`rest=["img","a.css"]`。随后此回调就会寻找`static_path`子目录下的`/img/a.css`文件，将此文件进行`gzip`压缩后添加请求头`'Content-Encoding = gzip'`并返回发送。

### 5. 响应构建工具

设计思路为简单易用可以在一行内完成响应构建，实现常用功能
对应文件`response_maker.py`提供链式调用快速生成响应。
<img src="doc/ar1.png">

##### `response`对象提供API：
* `__init__(code=200)` 设置状态码（默认200） 并设置基础字段 
* `set_body(byte) `可以设置body内容,需要是byte类型数据，为了兼容其他文件的传输
* `set_cookie(key,value)` 可以设置响应头`set_cookie`字段，可多次设置，也可以传入列表，字典等，另外有参数控制cookie行为
* `set_head(key,value)` 设置响应头其他字段
* `quick_jump(url)` 返回一段用于跳转的网页
* `content()` 只在内核内调用，组装网页并返回二进制数据

所有开放的API都支持链式调用

### 6. 配置文件

包含配置端口，ip，静态文件地址，网页协议等
由`read_config.py`文件读取，import后会将其中参数读出保存为全局参数

### 7. 日志功能(目前暂时取消，之后会做异步日志)

根据日期命名文件保存在根目录当中，记录内核活动，请求处理情况
应用中可以通过

* `server.DEBUG()`
* `server.INFO()`
* `server.WARNING()`
* `server.ERROR()`

借用内核日志功能写入日志
设置`sever.LOG = False` 可以将日志等级提高到WARNING (默认为True，等级为DEBUGE)

日志格式如下
```python
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s-%(asctime)s - %(filename)s[line:%(lineno)d]:%(message)s\r\n',
                        filename='%s.txt' % time.strftime('%Y-%m-%d'),
                        filemode='w',
                        encoding='utf-8')
```
<img src="doc/log1.png">

### 8. 请求解析

设计思路为：只进行简单的请求头分解，但提供进阶解析函数，在只要简单检查请求头时提供更快的速度，又保证需要复杂数据时的便捷性
对应文件`analysis_request.py`

其中提供了对请求头的全面解析，会将head中所有键值对储存，重载了中括号使读取更方便。部分值为列表或字典字符串形式的键值对需要用专门函数读取。

提供的接口包括：
* `value = request[key]` 重载了`__getter__` 方便读取
* `request[key] = value` 重载了 `__setter__` 方便写入更改
* `request.cookie()` 用来进一步解析cookie数据并返回，多次运行不会重复解析
* `request.accept()` 用来解析accept条目（通常是一大串附带附加参数的多个值组成的字符串）
* `print(request)` 重载了`__str__` 单纯方便debug

注意：现在还不能根据Content-Type自动处理负载，需要中间件进行处理


# 只对接口和运行逻辑做基本解释