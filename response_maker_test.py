from response_maker import ResponseMaker


maker  = ResponseMaker()
maker.set_head('Content','text')
maker.set_body(b'hello world')
maker.set_cookie('key','value',path='/',domain="localhost")
maker.set_cookie({'key1':'value1','key2':'value2'},httponly=True)
maker.set_cookie([['key1','value1'],['key2','value2']],max_age='100')


print(maker.content().decode('utf-8'))


print(ResponseMaker(code=304).set_body(b'hello world').content().decode('utf-8'))
