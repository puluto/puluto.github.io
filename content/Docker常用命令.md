Title: Docker常用命令
Date: 2015-11-26 18:52
Category: 容器技术
Tags: linux, docker, 命令

####容器安装操作(Linux内核需大于3.10)

    :::bash
    #原始安装
    curl -sSL https://get.docker.com/ | sh
    #国内安装，daocloud加速
    curl -sSL https://get.daocloud.io/docker | sh
    #检查安装结果
    sudo service docker status
安装docker的更多内容请参见: [Docker官方安装文档](http://docs.docker.com/engine/installation/)


####容器运行操作

    :::bash
    #列出正在运行的容器
    docker ps

    #列出所有的容器
    docker ps -a

    #下载一个镜像到本地，并不运行
    docker pull ubuntu

    #运行一个容器，如果镜像不存在会自动进行pull
    docker run -i -t ubuntu /bin/bash

    #运行容器并做端口转发至主机的3306，-e传入环境变量设置mysql的root密码
    docker run --name test-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d -p 3306:3306 daocloud.io/library/mysql:latest
    #运行一个tinyproxy代理
    docker run -i -t -p :8888 dannydirect/tinyproxy:latest ANY

    #以bash进入到运行中的容器
    sudo docker exec -it <CONTAINER ID> /bin/bash

    #删除所有容器
    docker rm `docker ps -a -q` 

####容器镜像操作

    :::bash
    #列出所有镜像(images)
    docker images

    #通过Dockerfile构建一个映像文件，Dockerfile的每一行指令都会创建一个临时的Container
    #–rm 选项是告诉Docker在构建完成后删除临时的Container，
    docker build --rm=true -t mytest/tinyproxy .

    #提交你的变更，并且把容器保存成镜像，命名为 mynewimage.<CONTAINER ID>为容器的ID.
    docker commit <CONTAINER ID> mynewimage

    #把 mynewimage 镜像保存成 tar 文件
    docker save mynewimage | bzip2 -9 -c > /home/mynewimage.tar.bz2
    
    #加载 mynewimage 镜像
    bzip2 -d -c < /home/mynewimage.tar.bz2 | docker load
    
    #删除镜像
    docker rmi [image-id]

    #导出正在运行的容器为Image
    docker export <CONTAINER ID> > /home/export.tar

    #导入Image镜像
    cat /home/export.tar | sudo docker import - mynewimage
