Title: Linux下SCSI磁盘热插拔
Date: 2015-11-25 18:52
Category: Linux技巧
Tags: linux, hotplug

###ESXi5中对Linux热添加磁盘时发现不生效，下文为临时解决方案
 
转载：[技术写真 » Linux下SCSI磁盘热插拔](http://www.anrip.com/post/1295)

维护服务器时，有可能需要热插拔硬盘，但是Linux好像并不买单，不会自动检测磁盘的装卸，为此热插拔后，我们需要通知Linux服务磁盘状态。
  
###添加磁盘，其中 2 0 1 0 分别对应 HOST CHAN DEV LUN
    echo "scsi add-single-device 2 0 1 0" > /proc/scsi/scsi
###查看磁盘
    > cat /proc/scsi/scsi
    Attached devices:
    Host: scsi0 Channel: 00 Id: 00 Lun: 00
    Vendor: NECVMWar Model: VMware IDE CDR00 Rev: 1.00
    Type:   CD-ROM                           ANSI  SCSI revision: 05
    Host: scsi2 Channel: 00 Id: 00 Lun: 00
    Vendor: VMware   Model: Virtual disk     Rev: 1.0
    Type:   Direct-Access                    ANSI  SCSI revision: 02
    Host: scsi2 Channel: 00 Id: 01 Lun: 00
    Vendor: VMware   Model: Virtual disk     Rev: 1.0
    Type:   Direct-Access                    ANSI  SCSI revision: 02
   
参数解析：

* HOST 是硬盘所在SCSI控制器号(本例中，磁盘所在通道为2);
* CHAN 是硬盘所在SCSI通道的编号(一般单通道的就是0，多通道的要看是哪个通道了);
* DEV 是硬盘的SCSI ID号(可以通过具体插入的硬盘插槽来判断);
* LUN 是硬盘的lun号(默认情况都是0)
