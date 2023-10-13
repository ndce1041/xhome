
from analysis_request import AnalysisRequest
import os

path = os.path.dirname(__file__)
print(path)

with open(path+'/html_test.txt','r',encoding="utf-8") as f:
    recv_data = f.read()
    data = AnalysisRequest(recv_data)
    print(data['method'])
    print(data['path'])
    print(data['protocol'])
    print(data.cookie())
    print(data.accept())
    print(data.cookie())
    print(data.path())
