Title: 测试文档 
Date: 2016-11-25 18:52
Category: Linux技巧
Tags: python


###单独获取当前目录名
    :::python
    import os
    def name():
        return os.path.split(os.getcwd())[-1]

###WIN关闭一个进程
    :::python
    import ctypes
    def kill(pid):
        """kill function for Win32"""
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, pid)
        
        #使用termina函数结束进程
        return (0 != kernel32.TerminateProcess(handle, 0))
