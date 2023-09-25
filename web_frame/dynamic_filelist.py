import os
from pyh import *
import sys

ArgumentsError = 'ArgumentsError - input wrong arguments'
FilePathError = 'FilePathError - target file was not exist'


class Dynamiclist:
    def __init__(self, rootpath='file'):
        self.__name__ = 'dynamicpage'
        self.rootpath = rootpath
        self.file_list = None
        self.get_file_list()
        self.page = PyH('File Station - Download')  # pyh是第三方轻量级html生成库
        self.build()

    def get_file_list(self):
        for root, dirs, files in os.walk(self.rootpath):
            self.file_list = files

    def reorder(self):
        # 排序功能,等以后加吧
        pass

    def file_list_build(self, file_list_obj):
        turn = 1
        for file_obj in self.file_list:
            if turn == 1:
                file_piece = file_list_obj << tr(bgcolor="#ffffff")
                turn = 0
            else:
                file_piece = file_list_obj << tr(bgcolor="#f0f0f0")
                turn = 1
            file_piece << td()
            file_piece << td(file_obj, height="46")
            file_piece << td(align="center") << a("下载", href="../file/" + file_obj, cl="download", download=file_obj)

    def build(self):


        # 更改开头声明
        self.page.attributes['xmlns'] = "http://www.w3.org/1999/xhtml"
        self.page.attributes['lang'] = "zh-cn"

        # head部分标签
        self.page << meta(charset="utf-8")
        self.page.addCSS('../static/filelist.css')

        # body部分标签框架

        main_table = self.page << table(width="1000", border="0", align="center", cellpadding="0", cellspacing="0")
        main_list = main_table << tr()

        # 网页末尾声明
        main_table << tr() << td(height='5')
        main_table << tr() << td("这是个学习用测试下载站,请勿上传和下载违禁内容", colspan="3", bgcolor="#4d4d4d", height="100",
                                 align="center", style="color:#ffffff;")

        # 实时生成部分
        side_button = main_list << td(width="25%", align="center", valign="top", bgcolor="#f2f2f2") << table(
            cellpadding="0",
            cellspacing="0",
            border="0", width="80%")  # 侧边按钮

        side_button << tr() << td(height="50")
        side_button << tr(align="center", valign="middle") << td() << img(src="../static/logo.png", width="100",
                                                                          cl="ico", draggable="false")
        side_button << tr() << td(height="40")
        side_button << tr() << td(height="2", bgcolor="000000")
        block = "&nbsp;" * 30
        side_button << tr() << td(cl="side_button", height="40") << a(block + "首页&nbsp;&nbsp;&nbsp;", href="../static/welcome.html")
        side_button << tr() << td(cl="side_button", height="40") << a(block + "评论&nbsp;&nbsp;&nbsp;", href="", cl="disble")
        side_button << tr() << td(cl="side_button", height="40") << a(block + "打赏&nbsp;&nbsp;&nbsp;", href="", cl="disble")
        side_button << tr() << td(cl="side_button", height="40") << a(block + "无&nbsp;&nbsp;&nbsp;", href="", cl="disble")
        ####################################################
        main_list << td(width="1%")  # 中间间隙
        #####################################################
        file_list = main_list << td(width="74%", align="center", valign="top") << table(border="0", width="100%",
                                                                                        cellpadding="0",
                                                                                        cellspacing="0")

        # 包含了上传按钮
        list_head = file_list << tr(bgcolor="#f0f0f0")
        list_head << th("文件列表:", height="80", width="80", align="left")
        list_head << td(align="center", valign="middle") << a("上传", href="", cl="upload disable")  # 上传按钮
        list_head << td(width="120")
        file_list << tr() << td(colspan="3", bgcolor="#000000", height="3")
        # 这里的file_list 是html模板
        self.file_list_build(file_list)
        # 真正文件列表部分

    def read(self):
        return self.pag.expeort()

    def save_copy(self):
        self.page.printOut(file='temporary/filelist.html')
