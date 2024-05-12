import runtime


server = runtime.Server()


def index(request,key,rest):
    return runtime.ResponseMaker(code=200).set_body(b'Hello World!').content()

server.url.add('/',index)

server.start()