
1. Attention:

(1)If the new disk is not sda such as sdb, you must change all sda to sdb in the mkosb.sh and mksdb.sh.

(2)in mksdb.sh : 
d
1
d
2
d
It means that the dest disk has already fdisk(3 partitions), so must delete them firstly and then fdisk new partitions.

=====================================================================================================================

2. Procedure

(1) put the folder which is called "clone_disk" into "/root"

(2) change the shell scripts' permission like this :
chmod 777 gen.sh
chmod 777 mkosb.sh
chmod 777 mksdb.sh

(3) execute
./gen.sh

