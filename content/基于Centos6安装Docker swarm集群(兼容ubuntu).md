Title: 基于Centos6安装docker swarm集群
Date: 2015-12-09 18:52
Category: 容器技术
Tags: linux, docker, 命令

###升级内核到3.8以上
    rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org

    rpm -ivh http://www.elrepo.org/elrepo-release-6-5.el6.elrepo.noarch.rpm

    #安装3.10长期支持内核kernel-lt (lt=long-term)
    yum --enablerepo=elrepo-kernel install kernel-lt -y

    #或者安装主线kernel-ml (ml=mainline)
    yum --enablerepo=elrepo-kernel install kernel-ml -y

###Install Docker Service.

    :::bash
    curl -sSL https://get.docker.com/ | sh
    #国内安装，daocloud加速
    curl -sSL https://get.daocloud.io/docker | sh
    #检查安装结果
    sudo service docker status
安装docker的更多内容请参见: [Docker官方安装文档](http://docs.docker.com/engine/installation/)
###修改docker配置

    :::bash
    #默认情况下docker守护进程是不会绑定tcp端口的，使用swarm需要开启tcp端口
    > vim /etc/sysconfig/docker
    #默认配置
    other_args=""
    #修改后的配置
    other_args="-H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock"
    > sudo service docker restart
    #检查2375端口是否存在
    > netstat -nltp ｜ grep 2375

###配置swarm
Swarm支持多种发现节点的模式，在此介绍本地发现(hosted discovery service)和consul发现两种模式
####本地发现模式
本地模式的原理是提交这个token到docker公司的服务器，然后运行swarm时去查询docker公司的服务器，
因为众所周知的原因，连接docker hub都很慢，所以这种方式不稳定，使用也不够灵活，只适用于测试以
及体验swarm的功能，当然好处是简单，不用引入其他技术。

    :::bash
    #执行swarm获得一个机群token，后续节点的加入均需要这个token
    > sudo docker run swarm create
    be1d6ac91667632d6635ee53b1f8caed
    #在每台需要加入同一swarm机群的节点上运行下面的命令
    > docker run -d swarm join --addr=<swarm_node_ip:2375> token://be1d6ac91667632d6635ee53b1f8caed
    #之后在任意一台节点上运行swarm的管理节点
    > docker run -d -p 2376:2375 swarm manage token://be1d6ac91667632d6635ee53b1f8caed
    #执行docker的查询命令获得以下信息 
    > docker -H tcp://<swarm_manage_ip:2376> info

    Containers: 4
    Images: 3
    Role: primary
    Strategy: spread
    Filters: health, port, dependency, affinity, constraint
    Nodes: 2
     dh1: <swarm_node1_ip:2375>
      └ Containers: 2
      └ Reserved CPUs: 0 / 4
      └ Reserved Memory: 0 B / 4.061 GiB
      └ Labels: executiondriver=native-0.2, kernelversion=3.10.93-1.el6.elrepo.x86_64, operatingsystem=<unknown>, storagedriver=devicemapper
     dh2: <swarm_node2_ip:2375>
      └ Containers: 2
      └ Reserved CPUs: 0 / 4
      └ Reserved Memory: 0 B / 4.061 GiB
      └ Labels: executiondriver=native-0.2, kernelversion=3.10.93-1.el6.elrepo.x86_64, operatingsystem=<unknown>, storagedriver=devicemapper
    CPUs: 8
    Total Memory: 8.121 GiB
    Name: ca539e6846b8
更多信息请参见 [Swarm官方文档]([https://docs.docker.com/v1.5/swarm/discovery/#using-the-hosted-discovery-service)
####Consul发现模式配置
此文档为了方便统一管理使用docker方式安装Consul，其他方式请参见 [Consul官方文档](https://www.consul.io/docs/guides/index.html)

    :::bash
    #运行consul镜像，因为consul是关键服务而且很多地方可以用到网络使用host模式，直接端口绑定到主机
    #-bootstrap表示初始化一个consul机群，ui参数可以启动consul自带的webui
    > docker run --net=host -P -d --name=consul-1 progrium/consul -server -bootstrap -ui-dir /ui
    #启动更多的consul节点，与zookeeper和etcd类似，此类服务都应该启动单数个节点便于仲裁
    > docker run --net=host -P -d --name=consul-2 progrium/consul -server -join <first_node_ip>
    > docker run --net=host -P -d --name=consul-3 progrium/consul -server -join <first_node_ip>
    #使用consul启动swarm集群
    > docker run -d swarm join --addr=<swarm_node1_ip:2375> consul://<consul_node_ip:8500>/swarm
    #启动第二个swarm节点，启动更多操作方式完全一样
    > docker run -d swarm join --addr=<swarm_node2_ip:2375> consul://<consul_node_ip:8500>/swarm
    #启动管理节点
    > docker run -d -p 2376:2375 swarm manage consul://<consul_node_ip:8500>/swarm
    > docker -H tcp://<swarm_manage_ip:2376> info
    
    Containers: 5
    Images: 4
    Role: primary
    Strategy: spread
    Filters: health, port, dependency, affinity, constraint
    Nodes: 2
     dh1: <swarm_node1_ip:2375>
      └ Containers: 2
      └ Reserved CPUs: 0 / 4
      └ Reserved Memory: 0 B / 4.061 GiB
      └ Labels: executiondriver=native-0.2, kernelversion=3.10.93-1.el6.elrepo.x86_64......
     dh2: <swarm_node2_ip:2375>
      └ Containers: 3
      └ Reserved CPUs: 0 / 4
      └ Reserved Memory: 0 B / 4.061 GiB
      └ Labels: executiondriver=native-0.2, kernelversion=3.10.93-1.el6.elrepo.x86_64......
    CPUs: 8
    Total Memory: 8.121 GiB
    Name: ca539e6846b8

####顺带配置一个Shipyard webui来管理docker
Shipyard本身自带一套安装swarm的流程，但是我们前面已经做过很多准备工作了所以不需要更多工作
感兴趣的请参考 [Shipyard官方文档](http://shipyard-project.com/docs/deploy/automated/)
我们这里只需要安装Shipyard依赖的rethinkdb和他的webui

    :::bash
    #通过docker安装rethinkdb
    docker run -ti -d --restart=always --name shipyard-rethinkdb rethinkdb
    #安装webui，需要link到rethinkdb，也就是说这两个服务需要安装到同一个docker node.
    docker run -ti -d --restart=always --name shipyard-controller --link shipyard-rethinkdb:rethinkdb \
    -p 8080:8080 shipyard/shipyard:latest server -d tcp://<swarm_manage_ip:2376>
#####到现在这个部署流程已经完成的差不多了，更详细的内容请查看各个组件的官方文档，在使用某个开源产品时建议第一件事就是详细阅读官方文档。
####后记：
由于目前官方docker对rhel6系列支持有限，官方只支持rhel6系列上安装1.7版本，所以一些高级功能不能使用，所以建议使用ubuntu 14.04以上或者rhel7系列发行版进行安装，我们目前使用的是ubuntu14.04，前面的教程除了docker守护进程配置文件为/etc/default/docker与centos6不同以及ubuntu14.04不用安装额外内核支持，其他操作均一摸一样。
