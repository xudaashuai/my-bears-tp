 # 计网作业2

 ## 实现了哪些功能

 - 丢包处理
 - 超时重传
 - 动态重试时间

 ## 修改了一些文件
 - BasicSender.py
    
    将读取文件方式改为二进制读取，原来的文本读取方式会出现奇怪的问题
    在22行
 - Receicer.py
    
    同样，将文件写入方式改为二进制
    在16行
 - TestHarness.py
 
    对偶尔出现的 socket error 添加异常处理
    在167 行
    
