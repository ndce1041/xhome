import main_rebuild as main
import response_maker as rm


server = main.Server()

def application(request,key,rest):
    # 响应生成 链式调用
    new_response = rm.ResponseMaker().set_head("success","true").set_cookie("key","value",max_age="1000").set_body("hello ss world".encode('utf-8'))
    
    # 只有执行.path()才会解析url
    print(request["path"])
    print(request.path())
    print(rest)

    # 返回的是ResponseMaker对象
    return new_response

server.url.add('/main/test',application) # 路由注册 中间以/分割即可

server.loop()