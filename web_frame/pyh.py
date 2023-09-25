# @file: pyh.py
# @purpose: a HTML tag generator
# @author: Emmanuel Turlay <turlay@cern.ch>

__doc__ = """The pyh.py module is the core of the PyH package. PyH lets you
generate HTML tags from within your python code.
See http://code.google.com/p/pyh/ for documentation.
"""
__author__ = "Emmanuel Turlay <turlay@cern.ch>"
__version__ = '$Revision$'
__date__ = '$Date$'

from sys import stdout, modules  # , _getframe, version

nOpen = {}

nl = '\n'
doctype = '<!DOCTYPE html>\n'
charset = '<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />\n'

tags = ['html', 'body', 'head', 'link', 'meta', 'div', 'p', 'form', 'legend',
        'input', 'select', 'span', 'b', 'i', 'option', 'img', 'script',
        'table', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'fieldset', 'a', 'title', 'body', 'head', 'title', 'script', 'br', 'table',
        'ul', 'li', 'ol', 'tbody' 'style']

selfClose = ['input', 'img', 'link', 'br', 'meta']

# 标签class 是关键字  用cl


class Tag(list):  # 标签对象
    tagname = ''

    def __init__(self, *arg, **kw):
        self.attributes = kw
        if self.tagname:
            name = self.tagname
            self.isSeq = False
        else:
            name = 'sequence'
            self.isSeq = True
        self.id = kw.get('id', name)
        # self.extend(arg)
        for a in arg: self.addObj(a)

    def __iadd__(self, obj):
        if isinstance(obj, Tag) and obj.isSeq:
            for o in obj: self.addObj(o)
        else:
            self.addObj(obj)
        return self

    def addObj(self, obj):
        if not isinstance(obj, Tag): obj = str(obj)
        id = self.setID(obj)
        setattr(self, id, obj)
        self.append(obj)

    def setID(self, obj):
        if isinstance(obj, Tag):
            id = obj.id
            n = len([t for t in self if isinstance(t, Tag) and t.id.startswith(id)])
        else:
            id = 'content'
            n = len([t for t in self if not isinstance(t, Tag)])
        if n: id = '%s_%03i' % (id, n)
        if isinstance(obj, Tag): obj.id = id
        return id

    def __add__(self, obj):
        if self.tagname: return Tag(self, obj)
        self.addObj(obj)
        return self

    def __lshift__(self, obj):
        self += obj
        if isinstance(obj, Tag): return obj

    def render(self):
        result = ''
        if self.tagname:
            result = '<%s%s%s>' % (self.tagname, self.renderAtt(), self.selfClose() * ' /')
        if not self.selfClose():
            for c in self:
                if isinstance(c, Tag):
                    result += c.render()
                else:
                    result += c
            if self.tagname:
                result += '</%s>' % self.tagname
        result += '\n'
        return result

    def renderAtt(self):
        result = ''
        for n, v in self.attributes.items():
            if n != 'txt' and n != 'open':
                if n == 'cl': n = 'class'
                result += ' %s="%s"' % (n, v)
        return result

    def selfClose(self):
        return self.tagname in selfClose


def TagFactory(name):
    class f(Tag):
        tagname = name

    f.__name__ = name
    return f

'''
sys.nodules是当前加载的所有模块构成的字典,键值"__main__" 对应自己
'''
thisModule = modules[__name__]

for t in tags:
    setattr(thisModule, t, TagFactory(t))
'''
setattr 与 getattr(获取对象里的对象) 对应,用来设置对象中的对象,这里的对象可以是对象属性或者实例属性,也可以是一整个类或对象,如果对象不存在会新建一个

这里获取自身后thisModule = modules[__name__]  
利用这个方法不断添加类,可以批量命名相似的类(功能一样但是需要名字不同的类)
而不进行实例化
'''

'''
def ValidW3C():
    out = a(img(src='http://www.w3.org/Icons/valid-xhtml10', alt='Valid XHTML 1.0 Strict'), href='http://validator.w3.org/check?uri=referer')
    return out
'''


class PyH(Tag):
    tagname = 'html'  # 用 html 标签作为模板

    def __init__(self, name='index'):
        self += head()
        self += body(topmargin="0")
        self.attributes = dict(xmlns='', lang='')  # 这里插入了 <html> 标签属性
        self.head += title(name)

    def __iadd__(self, obj):
        if isinstance(obj, head) or isinstance(obj, body):
            self.addObj(obj)
        elif isinstance(obj, meta) or isinstance(obj, link):  # 特别规定mate 和 link 标签在head里
            self.head += obj
        else:
            self.body += obj
            id = self.setID(obj)
            setattr(self, id, obj)
        return self

    def addJS(self, *arg):
        for f in arg: self.head += script(type='text/javascript', src=f)

    def addCSS(self, *arg):
        for f in arg: self.head += link(rel='stylesheet', type='text/css', href=f)

    def export(self):
        # 返回已经编码的目标内存地址
        html = doctype.encode('utf-8') + self.render().encode('utf-8')
        return html

    def printOut(self, file=''):
        if file:
            f = open(file, 'wb')
        else:
            f = stdout
        f.write(doctype.encode('utf-8'))
        f.write(self.render().encode('utf-8'))
        f.flush()
        if file: f.close()
