Title: 在Python中如何使用Linux的epoll
Date: 2017-04-14 21:20
Tags: python, linux
Category: 并发编程


[文档出自这里](https://docs.google.com/document/pub?id=1kH6JKRgAo6BDC3voKInN4TrSgqC0VVs9Op80xl5xGxw&pli=1#h.jaxt035lm50)

从2.6开始，[Python](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Fwww.python.org%252F%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNEP7etIfXhra1IhmVJRuJJxa6wRxQ&sa=D&ust=1492174612025000&usg=AFQjCNE-rZG5tzCHiQTrmFdLvZX32GChRw)包含了访问Linux epoll库的API。这篇文章用几个简单的python 3例子来展示下这个API。欢迎大家质疑和[反馈](http://scotdoyle.com)。

阻塞socket编程示例
================
示例1
----
* 用python3.0搭建了一个简单的服务：在8080端口监听HTTP请求，把它打印到控制台，并返回一个HTTP响应消息给客户端。

* 第9行：创建服务器socket。

* 第10行：允许在11行使用bind()来监听指定端口，即使这个端口最近被其他程序监听。没有这个设置的话，服务不能运行，直到一两分钟后，这个端口不再被之前的程序使用。

* 第11行：监听这台机器所有可用的IPv4地址上面的8080端口。

* 第12行：通知服务端socket开始接受来自客户端的连接。

* 第14行：这行代码直到接收到一个客户端连接才会完成。这时，服务端socket会在服务端机器上面创建一个新的socket，用来和客户端通信。这个新的socket在代码里面就是accept()调用返回的clientconnection 对象。返回的address对象代表着客户端的IP和端口。

* 第15-17行：组装从客户端传输过来的数据，直到HTTP请求完成。HTTP协议可以参考[这里](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Fwww.jmarshall.com%252Feasy%252Fhttp%252F%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNH8eRESrpc9ojWqF2YSsIPP1_oRDw&sa=D&ust=1492174612032000&usg=AFQjCNFpPTnjdlpCWoP-zbtXRB8gTak09w)。

* 第18行：把请求打印到控制台，验证操作是否正确。

* 第19行：发送响应回客户端。

* 第20-22行：关闭和客户端的连接以及服务端监听socket。
官方[howto](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Fdocs.python.org%252F3.0%252Fhowto%252Fsockets.html%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNGiML8p3XYTS0kgoO5ZGNk5Cfav5A&sa=D&ust=1492174612035000&usg=AFQjCNHIq6WJpkYDajCO520KRoHi_VYfYw)中对python socket编程有更详细的描述。

*Example 1 (All examples use Python 3)*
    
    :::python
    import socket

    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'
    response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    response += b'Hello, world!'

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('0.0.0.0', 8080))
    serversocket.listen(1)

    connectiontoclient, address = serversocket.accept()
    request = b''
    while EOL1 not in request and EOL2 not in request:
       request += connectiontoclient.recv(1024)
    print(request.decode())
    connectiontoclient.send(response)
    connectiontoclient.close()
  
    serversocket.close()
示例2
----
* 在15行增加了一个循环来不断的处理来自客户端的连接，直到用户中断（比如键盘中断）。这个例子更清楚的说明服务端socket从不和客户端交换数据。相反的，它接收客户端的连接，然后在这台服务器上面创建一个新的socket用来和客户端通信。
* 在23-24行的finally语句，可以确保服务端负责监听的socket会关闭，即使有异常发生。

*Example 2*

    :::python
    import socket
    
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'
    response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    response += b'Hello, world!'

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('0.0.0.0', 8080))
    serversocket.listen(1)
  
    try:
       while True:
          connectiontoclient, address = serversocket.accept()
          request = b''
          while EOL1 not in request and EOL2 not in request:
              request += connectiontoclient.recv(1024)
          print('-'*40 + '\n' + request.decode()[:-2])
          connectiontoclient.send(response)
          connectiontoclient.close()
    finally:
       serversocket.close()

异步socket的好处以及Linux epoll

* 示例2中的socket叫做阻塞socket，因为python程序会停止运行，直到一个event发生。16行的accept()调用会阻塞，直到接收到一个客户端连接。
* 19行的recv()调用会阻塞，直到这次接收客户端数据完成（或者没有更多的数据要接收）。21行的send()调用也会阻塞，直到将这次需要返回给客户端的数据都放到Linux的发送缓冲队列中。
* 当一个程序使用阻塞socket时，常常使用一个线程（甚至是一个专门的程序）来进行各个socket之间的通信。主程序线程会包含接收客户端连接的服务端监听socket。这个socket一次接收一个客户端连接，把连接传给另外一个线程新建的socket去处理。因为这些线程每个只和一个客户端通信，所以处理时即便在某几个点阻塞也没有关系。这种阻塞并不会对其他线程的处理造成任何影响。
使用多线程、阻塞socket来处理的话，代码会很直观，但是也会有[不少缺陷](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Fwww.virtualdub.org%252Fblog%252Fpivot%252Fentry.php%253Fid%253D62%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNEzhYSGdfy0SaEOET0JEkaPIllLAg&sa=D&ust=1492174612059000&usg=AFQjCNGT4CyNaNIIMRX5bblF1nMFTnnUzA)。它很难确保线程共享资源没有问题。而且这种编程风格的程序在只有一个CPU的电脑上面效率更低。
* [C10K](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Fwww.kegel.com%252Fc10k.html%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNGtTLrM31SPGEYBDjpjSU6tVYQYKA&sa=D&ust=1492174612060000&usg=AFQjCNFOT7yGjoq_nUnk1Ipi5OYre6TqUA)问题探讨了一些替代选择，其一是使用异步socket。这种socket只有在一些event触发时才会阻塞。相反，程序在异步socket上面执行一个动作，会立即被告知这个动作是否成功。程序会根据这个信息决定怎么继续下面的操作由于异步socket是非阻塞的，就没有必要再来使用多线程。所有的工作都可以在一个线程中完成。这种单线程模式有它自己的挑战，但可以成为很多方案不错的选择。它也可以结合多线程一起使用：单线程使用异步socket用于处理服务器的网络部分，多线程可以用来访问其他阻塞资源，比如数据库。
* Linux的2.6内核有一系列机制来管理异步socket，其中3个有对应的Python的API：select、poll和epoll。epoll和pool比select更好，因为Python程序不需要检查每一个socket感兴趣的event。相反，它可以依赖操作系统来告诉它哪些socket可能有这些event。epoll比pool更好，因为它不要求操作系统每次都去检查python程序需要的所有socket感兴趣的event。而是Linux在event发生的时候会跟踪到，并在Python需要的时候返回一个列表。
* 因此epoll对于大量（成千上万）并发socket连接，是更有效率和可扩展的机制，可以看这里的[图片](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Flse.sourceforge.net%252Fepoll%252Findex.html%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNHqYx09zrHtpvJUvGOWYvYFkDpR4g&sa=D&ust=1492174612061000&usg=AFQjCNGsNbxMBuAJjWFKo5qTQepkVwkOOA)。

带epoll的异步socket编程示例
------------------------

程序中使用epoll的顺序大都如下:

* 创建一个epoll对象
* 告诉epoll对象监控指定socket的指定event
* 询问epoll对象自从上次查询以后有哪些socket可能有指定的event发生
* 在这些socket上面执行一些动作
* 告诉epool对象去修改socket列表和（或者）event监控
* 重复步骤3到5，直到完成
* 销毁epoll对象

示例3
-------
* 重复了示例2的功能，同时使用异步socket。这个程序更为复杂，因为一个线程要交错与多个客户端通信。
* 第1行：select模块包含epoll功能。
* 第13行：因为socket默认是阻塞的，所以需要使用非阻塞（异步）模式。
* 第15行：创建一个epoll对象。
* 第16行：在服务端socket上面注册对读event的关注。一个读event随时会触发服务端socket去接收一个socket连接。
* 第19行：字典connections映射文件描述符（整数）到其相应的网络连接对象。
* 第21行：查询epoll对象，看是否有任何关注的event被触发。参数“1”表示，我们会等待1秒来看是否有event发生。如果有任何我们感兴趣的event发生在这次查询之前，这个查询就会带着这些event的列表立即返回。
* 第22行：event作为一个序列（fileno，event code）的元组返回。fileno是文件描述符的代名词，始终是一个整数。
* 第23行：如果一个读event在服务端sockt发生，就会有一个新的socket连接可能被创建。
* 第25行：设置新的socket为非阻塞模式。
* 第26行：为新的socket注册对读（EPOLLIN）event的关注。
* 第31行：如果发生一个读event，就读取从客户端发送过来的新数据。
* 第33行：一旦完成请求已收到，就注销对读event的关注，注册对写（EPOLLOUT）event的关注。写event发生的时候，会回复数据给客户端。
* 第34行：打印完整的请求，证明虽然与客户端的通信是交错进行的，但数据可以作为一个整体来组装和处理。
* 第35行：如果一个写event在一个客户端socket上面发生，它会接受新的数据以便发送到客户端。
* 第36-38行：每次发送一部分响应数据，直到完整的响应数据都已经发送给操作系统等待传输给客户端。
* 第39行：一旦完整的响应数据发送完成，就不再关注读或者写event。
* 第40行：如果一个连接显式关闭，那么socket shutdown是可选的。本示例程序这样使用，是为了让客户端首先关闭。shutdown调用会通知客户端socket没有更多的数据应该被发送或接收，并会让功能正常的客户端关闭自己的socket连接。
* 第41行：HUP（挂起）event表明客户端socket已经断开（即关闭），所以服务端也需要关闭。没有必要注册对HUP event的关注。在socket上面，它们总是会被epoll对象注册。
* 第42行：注销对此socket连接的关注。
* 第43行：关闭socket连接。
* 第18-45行：使用try-catch，因为该示例程序最有可能被KeyboardInterrupt异常中断。
* 第46-48行：打开的socket连接不需要关闭，因为Python会在程序结束的时候关闭。这里显式关闭是一个好的代码习惯。

*Example 3*

    :::python
    import socket, select
  
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'
    response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    response += b'Hello, world!'
 
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('0.0.0.0', 8080))
    serversocket.listen(1)
    serversocket.setblocking(0)
 
    epoll = select.epoll()
    epoll.register(serversocket.fileno(), select.EPOLLIN)

    try:
       connections = {}; requests = {}; responses = {}
       while True:
          events = epoll.poll(1)
          for fileno, event in events:
             if fileno == serversocket.fileno():
                connection, address = serversocket.accept()
                connection.setblocking(0)
                epoll.register(connection.fileno(), select.EPOLLIN)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = response
             elif event & select.EPOLLIN:
                requests[fileno] += connections[fileno].recv(1024)
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                   epoll.modify(fileno, select.EPOLLOUT)
                   print('-'*40 + '\n' + requests[fileno].decode()[:-2])
             elif event & select.EPOLLOUT:
                byteswritten = connections[fileno].send(responses[fileno])
                responses[fileno] = responses[fileno][byteswritten:]
                if len(responses[fileno]) == 0:
                   epoll.modify(fileno, 0)
                   connections[fileno].shutdown(socket.SHUT_RDWR)
             elif event & select.EPOLLHUP:
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
    finally:
       epoll.unregister(serversocket.fileno())
       epoll.close()
       serversocket.close()

* epoll有两种操作模式，称为边沿触发和水平触发 。在边沿触发模式中，epoll.poll（）在读或者写event在socket上面发生后，将只会返回一次event。调用epoll.poll()的程序必须处理所有和这个event相关的数据，随后的epoll.poll()调用不会再有这个event的通知。当一个特定event的数据耗尽时，进一步尝试操作socket将导致一个异常。相反，在水平触发模式下，重复调用epoll.poll（）会重复通知关注的event，直到与该event有关的所有数据都已被处理。在水平模式下通常没有异常。
* 例如，假设一个服务端socket已经为一个epoll对象注册了读event。在边沿触发模式下，程序需要一直accept()新的socket连接，直到一个socket.error的异常发生。而在水平触发模式下，一个accept()调用后，epoll对象会被服务端socket再次询问是否有新的event，以确定下一个accept()是否应该被调用。
* 示例3使用水平触发模式，这是操作的默认模式。示例4演示了如何使用边沿触发模式。
* 在示例4中，第25，36和45行引入循环，直到出现异常才退出（或者所有其他已知的数据都被处理）。
* 第32，38和48行捕获预期的socket异常。
* 第16，28，41和51行添加EPOLLET掩码，用来设置为边沿触发模式。

*Example 4*

    :::python
    import socket, select
    
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'
    response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    response += b'Hello, world!'

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('0.0.0.0', 8080))
    serversocket.listen(1)
    serversocket.setblocking(0)

    epoll = select.epoll()
    epoll.register(serversocket.fileno(), select.EPOLLIN | select.EPOLLET)
  
    try:
       connections = {}; requests = {}; responses = {}
       while True:
          events = epoll.poll(1)
          for fileno, event in events:
             if fileno == serversocket.fileno():
                try:
                   while True:
                      connection, address = serversocket.accept()
                      connection.setblocking(0)
                      epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
                      connections[connection.fileno()] = connection
                      requests[connection.fileno()] = b''
                      responses[connection.fileno()] = response
                except socket.error:
                   pass
             elif event & select.EPOLLIN:
                try:
                   while True:
                      requests[fileno] += connections[fileno].recv(1024)
                except socket.error:
                   pass
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                   epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                   print('-'*40 + '\n' + requests[fileno].decode()[:-2])
             elif event & select.EPOLLOUT:
                try:
                   while len(responses[fileno]) > 0:
                      byteswritten = connections[fileno].send(responses[fileno])
                      responses[fileno] = responses[fileno][byteswritten:]
                except socket.error:
                   pass
                if len(responses[fileno]) == 0:
                   epoll.modify(fileno, select.EPOLLET)
                   connections[fileno].shutdown(socket.SHUT_RDWR)
             elif event & select.EPOLLHUP:
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
    finally:
       epoll.unregister(serversocket.fileno())
       epoll.close()
       serversocket.close()

* 这两种模式是类似的，水平触发模式常被用在移植使用select或者poll机制的应用程序时，而边沿触发模式可以用在当程序员不需要或不想要操作系统协助管理event状态时。
* 除了这两种操作模式，epoll对象也可以注册socket使用EPOLLONESHOTevent掩码。当使用这个选项时，注册的event只适用于一个epoll.poll()调用，调用之后它会自动从被监视的socket注册列表中移除。

性能注意事项

监听缓冲区队列大小

在示例1-4中:

* 第12行都调用了serversocket.listen()方法。此方法的参数就是监听缓冲区队列的大小。它告诉操作系统可以接收多少TCP/IP连接，并放到缓冲区队列中等待Pytohn程序接收。Python程序每次在服务端socket上面调用accept()，就会有一个连接从缓冲区队列中移除，一个新的连接可以进入缓冲区队列。如果队列已满，新的连接都会被忽略，这会对网络连接的客户端造成不必要的延迟。在生产服务器上，通常要处理几十或几百个并发连接，所以值1通常是不够的。比如，当使用ab模拟100个并发HTTP 1.0客户端，对上面的几个示例进行负载测试，如果缓冲区队列的值小于50，就会引起性能下降。

TCP选项

* [TCP_CORK](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Fwww.baus.net%252Fon-tcp_cork%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNGj99pcsG7FWuggh3EzvssrQ7QRDA&sa=D&ust=1492174612151000&usg=AFQjCNEeO0I3AO1H0LCdeJrFSrjSESOR4g)选项可以用来“封存”消息，直到他们准备好发送。
* 如示例5的第34行和第40行所示，这个选项对于使用[HTTP/1.1流水线技术](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Fen.wikipedia.org%252Fwiki%252FHTTP_pipelining%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNHC_dwCO2hlYoxtao0o8Q6_BhY3gw&sa=D&ust=1492174612151000&usg=AFQjCNGZL-Ju6rdPXXydcSBV2-ANQap0lA)的HTTP服务端来说，可能是一个很好的选择。

*Example 5*

    :::python
    import socket, select
 
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'
    response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    response += b'Hello, world!'
 
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('0.0.0.0', 8080))
    serversocket.listen(1)
    serversocket.setblocking(0)
  
    epoll = select.epoll()
    epoll.register(serversocket.fileno(), select.EPOLLIN)
  
    try:
        connections = {}; requests = {}; responses = {}
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if fileno == serversocket.fileno():
                    connection, address = serversocket.accept()
                    connection.setblocking(0)
                    epoll.register(connection.fileno(), select.EPOLLIN)
                    connections[connection.fileno()] = connection
                    requests[connection.fileno()] = b''
                    responses[connection.fileno()] = response
                elif event & select.EPOLLIN:
                    requests[fileno] += connections[fileno].recv(1024)
                    if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                        epoll.modify(fileno, select.EPOLLOUT)
                        connections[fileno].setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 1)
                        print('-'*40 + '\n' + requests[fileno].decode()[:-2])
                elif event & select.EPOLLOUT:
                    byteswritten = connections[fileno].send(responses[fileno])
                    responses[fileno] = responses[fileno][byteswritten:]
                    if len(responses[fileno]) == 0:
                        connections[fileno].setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 0)
                        epoll.modify(fileno, 0)
                        connections[fileno].shutdown(socket.SHUT_RDWR)
                 elif event & select.EPOLLHUP:
                     epoll.unregister(fileno)
                     connections[fileno].close()
                     del connections[fileno]
    finally:
        epoll.unregister(serversocket.fileno())
        epoll.close()
        serversocket.close()

另一方面， [TCP_NODELAY](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Farticles.techrepublic.com.com%252F5100-10878_11-1050878.html%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNGFnQxhZ9P4LjSiE2OpY3PA6dNsjQ&sa=D&ust=1492174612166000&usg=AFQjCNHMp_FQGZdNm-OcnGx9Mud6mdQxsw)选项可以用来告诉操作系统，任何传递给socket.send()的数据，不再缓存，要立即发送给客户端。
如示例6的14行所示，这个选项对于使用一个SSH客户端或其他“实时”应用来说，可能是一个很好的选择。

*Example 6*

    :::python
    import socket, select
 
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'
    response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
    response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
    response += b'Hello, world!'
  
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('0.0.0.0', 8080))
    serversocket.listen(1)
    serversocket.setblocking(0)
    serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
  
    epoll = select.epoll()
    epoll.register(serversocket.fileno(), select.EPOLLIN)
  
    try:
       connections = {}; requests = {}; responses = {}
       while True:
          events = epoll.poll(1)
          for fileno, event in events:
             if fileno == serversocket.fileno():
                connection, address = serversocket.accept()
                connection.setblocking(0)
                epoll.register(connection.fileno(), select.EPOLLIN)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = response
             elif event & select.EPOLLIN:
                requests[fileno] += connections[fileno].recv(1024)
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                   epoll.modify(fileno, select.EPOLLOUT)
                   print('-'*40 + '\n' + requests[fileno].decode()[:-2])
             elif event & select.EPOLLOUT:
                byteswritten = connections[fileno].send(responses[fileno])
                responses[fileno] = responses[fileno][byteswritten:]
                if len(responses[fileno]) == 0:
                   epoll.modify(fileno, 0)
                   connections[fileno].shutdown(socket.SHUT_RDWR)
             elif event & select.EPOLLHUP:
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
    finally:
       epoll.unregister(serversocket.fileno())
       epoll.close()
       serversocket.close()

此页面上的示例不受版权限制，这里提供[下载](https://www.google.com/url?q=http://www.google.com/url?q%3Dhttp%253A%252F%252Fscotdoyle.com%252Fpython-epoll-examples.tar.gz%26sa%3DD%26sntz%3D1%26usg%3DAFQjCNGj_7emPC51_la_-A-aXVXjlf-smw&sa=D&ust=1492174612183000&usg=AFQjCNHpaApFNrHLzYWBQ5FBsBrOt8KcYg) 。

[文档出自这里](https://docs.google.com/document/pub?id=1kH6JKRgAo6BDC3voKInN4TrSgqC0VVs9Op80xl5xGxw&pli=1#h.jaxt035lm50)
