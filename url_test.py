import url_manager


url = url_manager.url_manager()

url.add('/', '/')
url.add('/a/b', '/a/b')
url.add('/a/b/c', '/a/b/c')
url.add('/a/b/d', '/a/b/d')


print(url.get('/a'))

