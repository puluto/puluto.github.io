Title: Ubuntu 14.04配置Windows域访问openvpn
Date: 2017-05-09 10:04
Tags: linux, vpn
Category: Linux技巧


安装openvpn和openvpn ldap 插件
---------------------

	:::bash
	
	sudo apt-get install openvpn-auth-ldap easy-rsa -y
	sudo cp /usr/share/doc/openvpn-auth-ldap/examples/auth-ldap.conf /etc/openvpn/
	sudo cp /usr/share/doc/openvpn/examples/sample-config-files/* /etc/openvpn/
	cd /etc/openvpn
	sudo gunzip server.conf.gz
	sudo cp server.conf server.conf.bak 

	# 进入/etc/openvpn/easy-rsa目录配置服务器证书
	source ./vars						# vars可以配置证书信息，也可以用默认的
	./clean-all
	./build-dh						# 生成dh pem文件
	./pkitool --initca				# 生成ca根证书
	./pkitool --server myserver	# 生成server证书
	./pkitool client1				# 生成客户端证书，这里可以不需要，LDAP为密码认证
	./pkitool --pass client2		# 签名客户端证书


按下面的内容配置server.conf

	:::

	port 1195
	dev tun
	mode server
	tls-server
	ca keys/ca.crt
	cert keys/server.crt
	key keys/server.key
	dh keys/dh1024.pem
	ifconfig 10.9.0.1 10.9.0.2
	ifconfig-pool 10.9.0.4 10.9.0.255
	push "route 10.9.0.1 255.255.255.255"
	push "route 10.16.16.0 255.255.255.0"
	keepalive 10 60
	inactive 600
	route 10.9.0.0 255.255.255.0
	user openvpn
	group openvpn
	persist-tun
	persist-key
	verb 4
	plugin /usr/lib/openvpn/plugin/lib/openvpn-auth-ldap.so "/etc/openvpn/auth/ldap.conf"
	client-cert-not-required


根据下面示例配置AD认证 /etc/openvpn/auth/ldap.conf
------------------------

	:::
	
	# 一般使用AD访问的时候可以不用配置TLS加密，所以TLS相关的项目都可以注释掉，保留TLS关闭项
	<LDAP>
	# LDAP server URL
	URL ldap://dc-test-1.test.com:389
	# Bind DN (If your LDAP server doesn't support anonymous binds)
	#BindDN uid=admin,ou=Users,dc=test,dc=com
	BindDN admin@test.com

	# Bind Password
	Password humus

	# Network timeout (in seconds)
	Timeout 15

	# Enable Start TLS
	# If not use TLS，please keep this.
	TLSEnable no

	# Follow LDAP Referrals (anonymously)
	FollowReferrals yes

	# TLS CA Certificate File
	TLSCACertFile /usr/local/etc/ssl/ca.pem

	# TLS CA Certificate Directory
	TLSCACertDir /etc/ssl/certs

	# Client Certificate and key
	# If TLS client authentication is required
	TLSCertFile /usr/local/etc/ssl/client-cert.pem
	TLSKeyFile /usr/local/etc/ssl/client-key.pem

	# Cipher Suite
	# The defaults are usually fine here
	# TLSCipherSuite ALL:!ADH:@STRENGTH
	</LDAP>

	<Authorization>
	# Base DN
	#BaseDN "CN=Users,DC=test,DC=com"
	BaseDN "CN=Users,DC=test,DC=com"

	# User Search Filter
	#SearchFilter "(&(uid=%u)(accountStatus=active))"
	#SearchFilter "(&(sAMAccountName=%u)(msNPAllowDialin=TRUE))"
	SearchFilter "(&(sAMAccountName=%u))"

	# Require Group Membership
	RequireGroup true

	# Add non-group members to a PF table (disabled)
	#PFTable ips_vpn_users

	<Group>
	BaseDN "CN=Users,DC=test,DC=com"
	SearchFilter "(cn=vpn-users)"
	MemberAttribute "member"
	# Add group members to a PF table (disabled)
	#PFTable ips_vpn_eng
	</Group>
	</Authorization>

开启openvpn server服务

    :::bash
	
	# 编辑/etc/default/openvpn文件，添加AUTOSTART="server"，openvpn服务器配置为server.conf
	# 就可以使用服务管理来控制openvpn服务器了
	
	service openvpn start
	

客户端配置文件，需要下载服务器的ca.crt到配置文件同一目录
------------------------------
	:::
	
	float
	port 1195
	dev tun
	remote 127.43.22.12
	ping 10
	persist-tun
	persist-key
	ca ca.crt
	auth-user-pass
	client
	verb 4