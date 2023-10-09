class AnalysisRequest(object):
    """
    传入数据后分为请求头和请求体

    请求头简单分割为字典
    特定项需要调用对应函数进一步解析
    """

    def __init__(self,recv_data:dict):
        if "\r\n" in recv_data:
            ENTER = "\r\n"
            print('1')
        else:
            ENTER = "\n"

        # 只分割一次
        self.data_head,self.data_body = recv_data.split(ENTER*2,1)

        # 解析请求头
        self.request_head = {}
        request_head_list = self.data_head.split(ENTER)
        try:
            self.request_head['method'],self.request_head['path'],self.request_head['protocol'] = request_head_list[0].split(' ')
        except:
            #log.error('请求头解析失败')
            raise Exception('请求头首行解析失败/t%s'% str(request_head_list[0]))
        
        # 第一行解析成功说明是有效的请求头
        
        for line in request_head_list[1:]:
            if line == '':
                continue
            key,value = line.split(':',1)
            self.request_head[key] = value.strip()
        
    # read only
    def __getitem__(self,key):
        return self.request_head[key]
    


    def cookie(self):
        if 'Cookie' not in self.request_head:
            self.request_head['Cookie'] = {}
        elif type(self.request_head['Cookie']) == str:
            self.request_head['Cookie'] = dict([i.split('=',1) for i in self.request_head['Cookie'].split(';')])
        return self.request_head['Cookie']
    
    def accept(self):

        if "Accept" not in self.request_head:
            self.request_head['Accept'] = []
        elif type(self.request_head['Accept']) == str:
            self.request_head['Accept'] = self.request_head['Accept'].split(',')
            for i in range(len(self.request_head['Accept'])):
                if ";" in self.request_head['Accept'][i]:
                    temp = self.request_head['Accept'][i].split(';')
                    for j in temp:
                        if "q=" in j: # 排除除q以外其他参数
                            self.request_head['Accept'][i] = [temp[0],j.split('=')[1]]
                        else:
                            self.request_head['Accept'][i] = [temp[0],1]
                else:
                    self.request_head["Accept"][i] = [self.request_head['Accept'][i],1]
        return self.request_head['Accept']



