Title: Openstack mitaka升级ocata
Date: 2017-05-10 18:56
Tags: python, openstack, 私有云
Category: 私有云

Openstack mitaka升级ocata
===========================

环境介绍
------------

* Openstack Controller： ubuntu 16.04
* Openstack Compute：	centos 7.3
* 组件包括：Keystone，glance，neutron，nova，cinder

*本次升级openstack不是在线热升级，升级期间某些服务不可用，没具体测试*

预先准备
------------
备份mitaka数据库和配置文件,还有apache2的wsgi配置文件

    :::bash
    mkdir -p /tmp/openstack_mitaka_backup/config/
    
    mysqldump --single-transaction --all-databases -uroot -p > \
    	/tmp/openstack_mitaka_backup/openstack_db_mitaka_backup.sql
    	
    for i in "nova glance cinder neutron keystone openstack-dashboard apache2"; \
    	do cp -a /etc/${i} /tmp/openstack_mitaka_backup/config/ ;done
    
    # 安装ocata源
    apt install software-properties-common
    add-apt-repository cloud-archive:ocata
    apt update && apt install python-openstackclient -y


keystone
-----------

	:::bash
	# 升级keystone的时候一定要安装oslo.middleware，否则会出现rpc调用问题
	apt-get install python-oslo.middleware keystone
	# 新版本和旧版本的wsgi配置文件名为keystone.conf,需要删除旧的配置，否则启动apache出错
	rm -f /etc/apache2/sites-enabled/wsgi-keystone.conf
	# 和安装一样执行数据库同步
	su -s /bin/sh -c "keystone-manage db_sync" keystone
	
	# 新版本默认使用fernet模式的token，如果更改为新格式需要执行下面的操作
	keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
	keystone-manage credential_setup --keystone-user keystone --keystone-group keystone
	
	# 执行keystone-manage doctor无输出即为正常
	systemctl restart apache2
	
*当前的情况基本上keystone是可用的，不会影响其他服务*

glance
------------

    :::bash
    apt install glance -y
    #glance依赖netifaces的最新版，需要pip更新，测试会出错
    pip install -U netifaces    # No module named netifaces

    su -s /bin/sh -c "glance-manage db_sync" glance
    su -s /bin/sh -c "glance-manage db_upgrade" glance
    su -s /bin/sh -c "glance-manage db_migrate" glance

    service glance-registry restart
    service glance-api restart
    
    #source OS配置环境变量进行测试
    . ~/admin-openrc
    openstack image create "cirros" --file cirros-0.3.4-x86_64-disk.img --disk-format qcow2 --container-format bare --public
    openstack image show <Image ID>
    
*glance升级完成*

nova
------------
NOVA在这次升级中是最复杂的，因为增加了Placement服务和Cellv2，并且是强制的

    :::bash
    apt install nova-api nova-conductor nova-consoleauth \
    	nova-spiceproxy nova-scheduler nova-placement-api -y
    
    # 创建cellv2需要的数据库，每个nova节点以及instance都需要映射到相应的cell才能使用
	 CREATE DATABASE nova_cell0;
	 GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'localhost' IDENTIFIED BY 'NOVA_DBPASS';
	 GRANT ALL PRIVILEGES ON nova_cell0.* TO 'nova'@'%' IDENTIFIED BY 'NOVA_DBPASS';
    
    # 创建placement服务和用户
    . ~/admin-openrc
    openstack user create --domain default --password-prompt placement
    openstack role add --project service --user placement admin
    openstack service create --name placement --description "Placement API" placement
    openstack endpoint create --region RegionOne placement public http://controller:8778
    openstack endpoint create --region RegionOne placement internal http://controller:8778
    openstack endpoint create --region RegionOne placement admin http://controller:8778

    #Ocata版本更改了连接消息队列的方式，设置新的参数来连接，旧的相关配置全部注释或删除
    [DEFAULT]
    transport_url = rabbit://openstack:'RABBITMQ_PASS'@controller

    # 添加placement服务连接
    [placement]
    os_region_name = RegionOne
    project_domain_name = Default
    project_name = service
    auth_type = password
    user_domain_name = Default
    auth_url = http://controller:35357/v3
    username = placement
    password = PLACEMENT_PASS
    
    # 创建cell
    su -s /bin/sh -c "nova-manage cell_v2 map_cell0" nova
    su -s /bin/sh -c "nova-manage cell_v2 create_cell --name=cell1 --verbose" nova
    # 同步数据库
    su -s /bin/sh -c "nova-manage api_db sync" nova
    su -s /bin/sh -c "nova-manage db sync" nova
    su -s /bin/sh -c "nova-manage db online_data_migrations" nova
    su -s /bin/sh -c "nova-manage db sync" nova

    service nova-api restart
    service nova-consoleauth restart
    service nova-scheduler restart
    service nova-conductor restart
    service nova-spiceproxy restart

    # 顺便更新了controller的compute节点
    apt install nova-compute
    service nova-compute restart
    # 新的compute节点需要使用cell api进行发现才能使用
    su -s /bin/sh -c "nova-manage cell_v2 discover_hosts --verbose" nova
    # 配置schedule周期性进行节点的扫描
    [scheduler]
	 discover_hosts_in_cells_interval = 300
	 
	 # 在dashboard可以看到instance，不能查看详情，需要cell映射
	 # cell0是默认没有进行映射的instance所属，所以需要使用前面创建的cell1进行映射
	 nova-manage cell_v2 list_cells	# 找到cell1的uuid
	 nova-manage cell_v2 map_instances --cell_uuid CELL1_UUID

*现在可以升级其他compute节点了，就是直接安装nova-compute后，添加plancement服务配置后重启*

neutron
---------

    :::bash
    apt install neutron-server neutron-plugin-ml2 \
    neutron-linuxbridge-agent neutron-dhcp-agent neutron-metadata-agent
    
    # 配置只修改rabbitmq连接的方式
    su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf \
    	--config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
    
    # 重启所有neutron的服务，可以用service也可以用systemctl
    service neutron-server restart
    service neutron-linuxbridge-agent restart
    service neutron-dhcp-agent restart
    service neutron-metadata-agent restart
    service neutron-l3-agent restart
    
*升级compute节点的agent然后修改rabbitmq连接重启，网络升级完成*

cinder
---------

    :::bash
    apt install cinder-api cinder-scheduler cinder-volume
    # 修改rabbitmq配置后执行
    su -s /bin/sh -c "cinder-manage db sync" cinder
    su -s /bin/sh -c "cinder-manage db online_data_migrations" cinder
    
    # 重启cinder服务
    systemctl restart cinder-scheduler.service
    systemctl restart cinder-volume.service
    systemctl restart apache2
    
    # 检测cinder服务状态
    cinder-manage service list
    
    # 如果日志有rpcversion相关的错误是因为有未使用的旧版cinder-volume服务存在数据库中，需要删除
    cinder-manage service remove cinder-volume HOST@SERVICE_NAME
    
*cinder服务升级完成*

dashboard
-----------

    :::bash
    # dashboard的升级需要先删除旧版再安装新版，否则可能出现莫名的情况
    apt remove openstack-dashboard* -y
    rm -rf /var/lib/openstack-dashboard
    
    apt install openstack-dashboard -y
    # 由于openstack-dashboard涉及的变更较多，配件项建议使用新版的然后迁移旧版的配置
    # 重启apache2
    systemctl restart apache2
    
*至此整个升级过程完成*

后记
------------

整个升级过程是参照官方的安装文档进行版本对比后操作的，openstack最近几个版本的升级操作还是比较稳定的
如果需要更好的升级流程，请参照官网的无停机或者短时停机的方式去升级，本次升级基于公司内部云平台进行。
