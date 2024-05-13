import runtime



server = runtime.Server()


def index(request,key,rest):
    # print('runtime: index')
    return runtime.ResponseMaker(code=200).set_body(b'Hello World!')

server.url.add('/',index)

server.start()