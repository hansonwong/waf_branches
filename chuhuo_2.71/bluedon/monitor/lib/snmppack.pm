package snmppack;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(snmpinit get_curtime);
use strict;
use DBI;
use Crypt::DES;
use Net::SNMP qw(snmp_dispatcher oid_lex_sort);


use vars qw/
%snmpparms @snmpvar $session $error $user @mlist
$sql $dbh $sth $rows $starttime $currenttime
$nowsec $nowmin $nowhour $nowday $nowmonth $nowyear $nowwday $nowyday
/;
@snmpvar = ('User','Version','Port','Community','HostName',
            'UserName','AuthPassWord','AuthProtocol','TimeOut');

sub snmpinit
{
    my ($snmpconf, $monitor, $dcur) = @_;
    $dbh = $dcur;
    my $flag = 0;
    undef %snmpparms;
    $user = ${$snmpconf}[0];
    $snmpparms{$snmpvar[8]} = 2;
    $snmpparms{$snmpvar[1]} = ${$snmpconf}[4];
    $snmpparms{$snmpvar[2]} = ${$snmpconf}[3];
    $snmpparms{$snmpvar[4]} = ${$snmpconf}[1];
    if($snmpparms{$snmpvar[1]} eq "3"){
        $snmpparms{$snmpvar[5]} = ${$snmpconf}[6];
        $snmpparms{$snmpvar[6]} = ${$snmpconf}[7];
        $snmpparms{$snmpvar[7]} = ${$snmpconf}[8];
    }else{
        $snmpparms{$snmpvar[3]} = ${$snmpconf}[5];
    }
    
    &get_curtime;
    ($session, $error) = Net::SNMP->session(%snmpparms);
    if(!defined $session){
        #printf "ERROR: %s.\n", $error;
        for(my $id = 0; $id < @$monitor; $id++){
            update_warning(${$monitor}[$id], 1);
        }
        return 1;
    }

    foreach my $line (@$monitor){
        if($line == 1){
            $flag = &Get_LoadUsage();
        }
        elsif($line == 2){
            $flag = &Get_CpuUsage();            
        }
        elsif($line == 3){
            $flag = &Get_DiskIO();            
        }
        elsif($line == 4){
            $flag = &Get_Diskusage();
        }
        elsif($line == 5){
            $flag = &Get_MemUsage();
        }
        elsif($line == 6){
            $flag = &Get_Process();
        }
        elsif($line == 7){
            $flag = &Get_Traffic();
        }
        &update_warning($line,$flag);

    }
    $session->close();
    return 0;
}

sub error
{
    print "Error: $_[0]\n";
    return 1;
}

sub select_data
{
    $sth = $dbh->prepare($sql);
    $sth->execute();
    my @data = $sth->fetchrow_array();
    $sth->finish();
    return @data;
}

sub update_data
{
    $rows = $dbh->do($sql);
    if(!$rows){
        error("We can't update a rows to the '$_[0]' table ".
              "in the database\n $DBI::err ($DBI::errstr)");
        return 1;
    }
    return 0;
}

sub update_warning
{
    my @object = @_;   
    $sql = "SELECT `status` FROM tbl_mobject WHERE ".
           "snmpip='$snmpparms{$snmpvar[4]}' AND mlistid='$object[0]'";
    my @data = &select_data();

    if($object[1] != $data[0]){
        $sql = "INSERT INTO tbl_wmsg (user,snmpip,typeid,timed,mlistid,message) VALUES ".
        "('$user', '$snmpparms{$snmpvar[4]}', '1', '$currenttime', '$object[0]', ";
        if($object[1] == 1){
            $sql = $sql."'无法通过SNMP获取数据');";
        }else{
            $sql = $sql."'SNMP已恢复正常');";
        }
        &update_data("tbl_wmsg");

        $sql = "UPDATE `tbl_mobject` SET `status`='$object[1]' WHERE ".
               "snmpip='$snmpparms{$snmpvar[4]}' and mlistid='$object[0]'";
        &update_data("tbl_mobject");
    }   
}

sub get_curtime
{
    $starttime=time();
    ($nowsec,$nowmin,$nowhour,$nowday,$nowmonth,$nowyear,$nowwday,$nowyday) = localtime($starttime);
    if ($nowyear < 100) { $nowyear += 2000; }
    else { $nowyear += 1900; }
    if (++$nowmonth < 10) { $nowmonth = "0$nowmonth"; }
    if ($nowday < 10) { $nowday = "0$nowday"; }
    if ($nowhour < 10) { $nowhour = "0$nowhour"; }
    if ($nowmin < 10) { $nowmin = "0$nowmin"; }
    if ($nowsec < 10) { $nowsec = "0$nowsec"; }
    $currenttime = "$nowyear-$nowmonth-$nowday $nowhour:$nowmin:$nowsec";
}

sub Get_LoadUsage
{
    my $load1 = '.1.3.6.1.4.1.2021.10.1.3.1';
    my $load5 = '.1.3.6.1.4.1.2021.10.1.3.2';
    my $load15 = '.1.3.6.1.4.1.2021.10.1.3.3';
    my $result = $session->get_request(
                     -varbindlist => [$load1, $load5, $load15]);
    if(!defined $result){
        return 1;
    }
    
    $sql = "INSERT INTO monitorload (hostip,timed,laload1,laload5,laload15) ".
           "VALUES ('$snmpparms{$snmpvar[4]}','$currenttime','$result->{$load1}',".
           "'$result->{$load5}','$result->{$load15}');";
    if(&update_data("monitorload")){
        return 1;
    }

    $sql = "SELECT * FROM cur_cpuload WHERE SnmpIp='$snmpparms{$snmpvar[4]}'";
    my @data = &select_data();
    $sql = "`cur_cpuload` SET `CurTime`='$starttime',`SnmpIp`='$snmpparms{$snmpvar[4]}',".
           "`Usage1`='$result->{$load1}',`Usage5`='$result->{$load5}',`Usage15`='$result->{$load15}'";
    if(!@data){
        $sql = "INSERT INTO ".$sql.";";
    }
    else{
        $sql = "UPDATE ".$sql." WHERE SnmpIp='$snmpparms{$snmpvar[4]}';";
    }
    &update_data("cur_cpuload");
    
    return 0;
}

sub Get_CpuUsage
{
    my $CpuUser = '.1.3.6.1.4.1.2021.11.50.0';
    my $nice = '.1.3.6.1.4.1.2021.11.51.0';
    my $CpuSystem = '.1.3.6.1.4.1.2021.11.52.0';
    my $idle = '.1.3.6.1.4.1.2021.11.53.0';
    my $iowait = '.1.3.6.1.4.1.2021.11.54.0';
    my $irq = '.1.3.6.1.4.1.2021.11.56.0',
    my $softirq = '.1.3.6.1.4.1.2021.11.59.0';
    my $result = $session->get_request(
                     -varbindlist => [$CpuUser, $nice, 
                     $CpuSystem, $idle, $iowait, $irq, $softirq]);
    if(!defined $result){
        return 1;
    }

    $sql = "SELECT * FROM cur_cpuusage WHERE SnmpIp='$snmpparms{$snmpvar[4]}'";
    my @data = &select_data();
    $sql = "`cur_cpuusage` SET `CurTime`='$starttime',".
           "`SnmpIp`='$snmpparms{$snmpvar[4]}',`CpuUser`='$result->{$CpuUser}',".
           "`Nice`='$result->{$nice}',`CpuSystem`='$result->{$CpuSystem}',".
           "`Idle`='$result->{$idle}',`IOWait`='$result->{$iowait}',".
           "`IRQ`='$result->{$irq}',`SoftIRQ`= '$result->{$softirq}'";
    if(!@data){
        $sql = "INSERT INTO ".$sql.";";
        return &update_data("cur_cpuusage");
    }

    my @buf;
    my $total_time = $result->{$CpuUser} + $result->{$nice} + $result->{$CpuSystem} +
                     $result->{$idle} + $result->{$iowait} +$result->{$irq} + $result->{$softirq} - 
                     $data[2] - $data[3] - $data[4] - $data[5] - $data[6] - $data[7] - $data[8];
    $buf[0] = sprintf("%.2f", 100*($result->{$CpuUser}-$data[2])/$total_time);
    $buf[1] = sprintf("%.2f", 100*($result->{$CpuSystem}-$data[4])/$total_time);
    $buf[2] = sprintf("%.2f", 100*($result->{$iowait}-$data[6])/$total_time);
    $buf[3] = sprintf(100-$buf[0]-$buf[1]-$buf[2]);
    $buf[4] = $buf[0]+$buf[1]+$buf[2];
    $sql = "UPDATE ".$sql.",`Usage`='$buf[4]' WHERE SnmpIp='$snmpparms{$snmpvar[4]}';";
    if(&update_data("cur_cpuusage")){
        return 1;
    }
    
    $sql = "INSERT INTO monitorcpu (hostip,timed,user,system,iowait,idle) VALUES ".
           "('$snmpparms{$snmpvar[4]}','$currenttime','$buf[0]','$buf[1]','$buf[2]','$buf[3]');";
    if(&update_data("monitorcpu")){
        return 1;
    }

    return 0;
}

sub Get_DiskIO
{
    my $result;
    my $total_time = 0;
    my (@num, @Device, @Reads, @Writes, @NReadX, @NWrittenX) = ();
    my @diskio = ('.1.3.6.1.4.1.2021.13.15.1.1.2',
                  '.1.3.6.1.4.1.2021.13.15.1.1.5',
                  '.1.3.6.1.4.1.2021.13.15.1.1.6',
                  '.1.3.6.1.4.1.2021.13.15.1.1.12',
                  '.1.3.6.1.4.1.2021.13.15.1.1.13');
    for(my $id = 0; $id < @diskio; $id++){
        $result = $session->get_table(-baseoid => $diskio[$id]);
        if(!defined $result){
            return 1;
        }
        my $count = 0;
        foreach(oid_lex_sort(keys(%{$result}))){
            if($id == 0){
                if($result->{$_} =~ /sd/ || $result->{$_} =~ /hd/){
                    ($num[$count]) = $_ =~ /\.([^\.]+)$/;
                    $Device[$count++] = $result->{$_};
                }
            }
            else{
                my ($flag) = $_ =~ /\.([^\.]+)$/;
                if($flag == $num[$count] && $id == 1){
                    $Reads[$count++] = $result->{$_};
                }
                elsif($flag == $num[$count] && $id == 2){
                    $Writes[$count++] = $result->{$_};
                }
                elsif($flag == $num[$count] && $id == 3){
                    $NReadX[$count++] = $result->{$_};
                }
                elsif($flag == $num[$count] && $id == 4){
                    $NWrittenX[$count++] = $result->{$_};
                }
            }
        }
    }
    
    for(my $id = 0; $id < @Device; $id++){
        $sql = "SELECT * FROM cur_diskio WHERE ".
               "SnmpIp='$snmpparms{$snmpvar[4]}' AND `Device`='$Device[$id]'";
        my @data = &select_data();
        $sql = "`cur_diskio` SET `CurTime`='$starttime',`SnmpIp`='$snmpparms{$snmpvar[4]}',".
               "`Device`='$Device[$id]',`Reads`='$Reads[$id]',`Writes`='$Writes[$id]',".
               "`NReadX`='$NReadX[$id]',`NWrittenX`='$NWrittenX[$id]'";
        if(!@data){
            $sql = "INSERT INTO ".$sql.";";
            &update_data("cur_diskio");
            next;
        }
        
        $total_time = $starttime - $data[0];
        $Reads[$id] = sprintf("%.2f", ($Reads[$id]-$data[3])/$total_time);
        $Writes[$id] = sprintf("%.2f", ($Writes[$id]-$data[4])/$total_time);
        $NReadX[$id] = sprintf("%.2f", ($NReadX[$id]-$data[5])/(1024*$total_time));
        $NWrittenX[$id] = sprintf("%.2f", ($NWrittenX[$id]-$data[6])/(1024*$total_time));
        my $MaxReads = ($Reads[$id] > $data[7]) ? $Reads[$id] : $data[7];
        my $MaxWrites = ($Writes[$id] > $data[8]) ? $Writes[$id] : $data[8];
        my $MaxNReadX = ($NReadX[$id] > $data[9]) ? $NReadX[$id] : $data[9];
        my $MaxNWrittenX = ($NWrittenX[$id] > $data[10]) ? $NWrittenX[$id] : $data[10];
        $sql = "UPDATE ".$sql.",`MaxReads`='$MaxReads',`MaxWrites`='$MaxWrites',".
               "`MaxNReadX`='$MaxNReadX',`MaxNWrittenX`='$MaxNWrittenX',".
               "`SpeedReads`='$NReadX[$id]',`SpeedWrites`='$NWrittenX[$id]' ".
               "WHERE SnmpIp='$snmpparms{$snmpvar[4]}' AND Device='$Device[$id]';";
        &update_data("cur_diskio");
    
        $sql = "INSERT INTO monitordiskio (hostip,timed,device,reades,writes,".
               "readbite,writebite) VALUES ('$snmpparms{$snmpvar[4]}',".
               "'$currenttime','$Device[$id]','$Reads[$id]','$Writes[$id]',".
               "'$NReadX[$id]','$NWrittenX[$id]');";
        if(&update_data("monitordiskio")){
            return 1;
        }
    }
    return 0;
}

sub Get_Diskusage
{
    my $result;
    my (@num, @StorageDescr, @StorageSize, @blocksize, @StorageUsed) = ();
    my @diskusage = ('.1.3.6.1.2.1.25.2.3.1.3',
                     '.1.3.6.1.2.1.25.2.3.1.5',
                     '.1.3.6.1.2.1.25.2.3.1.4',
                     '.1.3.6.1.2.1.25.2.3.1.6');
    for(my $id = 0; $id < @diskusage; $id++){
        $result = $session->get_table(-baseoid => $diskusage[$id]);
        if(!defined $result){
            return 1;
        }
        my $count = 0;
        foreach(oid_lex_sort(keys(%{$result}))){
            if($id == 0){
                if($result->{$_} =~ /\//){
                    ($num[$count]) = $_ =~ /\.([^\.]+)$/;
                    $StorageDescr[$count++] = $result->{$_};
                }
            }
            else{
                my ($flag) = $_ =~ /\.([^\.]+)$/;
                if($flag == $num[$count] && $id == 1){
                    $StorageSize[$count++] = $result->{$_};
                }
                elsif($flag == $num[$count] && $id == 2){
                    $blocksize[$count++] = $result->{$_};
                }
                elsif($flag == $num[$count] && $id == 3){
                    $StorageUsed[$count++] = $result->{$_};
                }
            }
        }
    }
    
    for(my $id = 0; $id < @StorageDescr; $id++){
        my $diskusage = sprintf("%.2f", 100*$StorageUsed[$id]/$StorageSize[$id]);
        $StorageSize[$id] = sprintf("%.2f", $StorageSize[$id]*$blocksize[$id]/(1024*1024*1024));
        $StorageUsed[$id] = sprintf("%.2f", $StorageUsed[$id]*$blocksize[$id]/(1024*1024*1024));
        $sql = "INSERT INTO monitordiskusage (hostip,timed,diskname,".
                "totalsize,usesize) VALUES ('$snmpparms{$snmpvar[4]}',".
                "'$currenttime','$StorageDescr[$id]','$StorageSize[$id]',".
                "'$StorageUsed[$id]');";
        if(&update_data("monitordiskusage")){
            return 1;
        }
        
        $sql = "SELECT * FROM cur_diskusage WHERE ".
               "SnmpIp='$snmpparms{$snmpvar[4]}' AND ".
               "`StorageDescr`='$StorageDescr[$id]'";
        my @data = &select_data();
        $sql = "`cur_diskusage` SET `CurTime`='$starttime',`SnmpIp`='$snmpparms{$snmpvar[4]}',".
               "`StorageDescr`='$StorageDescr[$id]',`Usage`='$diskusage' ";
        if(!@data){
            $sql = "INSERT INTO ".$sql.";";
        }
        else{
            $sql = "UPDATE ".$sql."WHERE SnmpIp='$snmpparms{$snmpvar[4]}' ".
               "AND StorageDescr='$StorageDescr[$id]';";
        }
        &update_data("cur_diskusage");
    }
    return 0;
}

sub Get_MemUsage
{
    my $TotalSwap = '.1.3.6.1.4.1.2021.4.3.0';
    my $AvailSwap = '.1.3.6.1.4.1.2021.4.4.0';
    my $TotalReal = '.1.3.6.1.4.1.2021.4.5.0';
    my $AvailReal = '.1.3.6.1.4.1.2021.4.6.0';
    my $MemBuffer = '.1.3.6.1.4.1.2021.4.14.0';
    my $MemCached = '.1.3.6.1.4.1.2021.4.15.0';
    my $result = $session->get_request(
                     -varbindlist => [$TotalSwap, $AvailSwap,
                     $TotalReal, $AvailReal, $MemBuffer, $MemCached]);
    if(!defined $result){
        return 1;
    }
    
    my $swapusage = $result->{$TotalSwap}-$result->{$AvailSwap};
    $swapusage = sprintf("%.2f", 100*$swapusage/$result->{$TotalSwap});
    my $realusage = $result->{$TotalReal}-$result->{$AvailReal}-
                    $result->{$MemBuffer}-$result->{$MemCached};
    $realusage = sprintf("%.2f", 100*$realusage/$result->{$TotalReal});
    $result->{$TotalSwap} = sprintf("%.2f", $result->{$TotalSwap}/1024);
    $result->{$AvailSwap} = sprintf("%.2f", $result->{$AvailSwap}/1024);
    $result->{$TotalReal} = sprintf("%.2f", $result->{$TotalReal}/1024);
    $result->{$AvailReal} = sprintf("%.2f", $result->{$AvailReal}/1024);
    $result->{$MemBuffer} = sprintf("%.2f", $result->{$MemBuffer}/1024);
    $result->{$MemCached} = sprintf("%.2f", $result->{$MemCached}/1024);
    $sql = "INSERT INTO monitormemory (hostip,timed,totalswap,availswap,totalreal,".
           "availreal,buffercache,pagecache) VALUES ('$snmpparms{$snmpvar[4]}',".
           "'$currenttime','$result->{$TotalSwap}','$result->{$AvailSwap}',".
           "'$result->{$TotalReal}','$result->{$AvailReal}','$result->{$MemBuffer}',".
           "'$result->{$MemCached}');";
    if(&update_data("monitormemory")){
        return 1;
    }
    
    $sql = "SELECT * FROM cur_memory WHERE SnmpIp='$snmpparms{$snmpvar[4]}'";
    my @data = &select_data();
    $sql = "`cur_memory` SET `CurTime`='$starttime',".
           "`SnmpIp`='$snmpparms{$snmpvar[4]}',`UsageM`='$realusage',`UsageS`='$swapusage'";
    if(!@data){
        $sql = "INSERT INTO ".$sql.";";
    }
    else{
        $sql = "UPDATE ".$sql." WHERE SnmpIp='$snmpparms{$snmpvar[4]}';";
    }
    &update_data("cur_memory");
    
    return 0;
}

sub Get_Process
{
    my $Processes = '.1.3.6.1.2.1.25.1.6.0';
    my $result = $session->get_request(-varbindlist => [$Processes]);
    if(!defined $result){
        return 1;
    }
    
    $sql = "INSERT INTO monitorprocess (hostip,timed,number) VALUES ".
           "('$snmpparms{$snmpvar[4]}','$currenttime','$result->{$Processes}');";
    if(&update_data("monitorprocess")){
        return 1;
    }
    
    $sql = "SELECT * FROM cur_process WHERE SnmpIp='$snmpparms{$snmpvar[4]}'";
    my @data = &select_data();
    $sql = "`cur_process` SET `CurTime`='$starttime',".
           "`SnmpIp`='$snmpparms{$snmpvar[4]}',`Number`='$result->{$Processes}'";
    if(!@data){
        $sql = "INSERT INTO ".$sql.";";
    }
    else{
        $sql = "UPDATE ".$sql." WHERE SnmpIp='$snmpparms{$snmpvar[4]}';";
    }
    &update_data("cur_process");
    
    return 0;
}

sub Get_Traffic
{
    my $result;
    my $total_time = 0;
    my (@ifName, @InOctets, @InUcastPkts, @OutOctets, @OutUcastPkts) = ();
    my @traffic = ('.1.3.6.1.2.1.31.1.1.1.1',
                  '.1.3.6.1.2.1.31.1.1.1.6',
                  '.1.3.6.1.2.1.31.1.1.1.7',
                  '.1.3.6.1.2.1.31.1.1.1.10',
                  '.1.3.6.1.2.1.31.1.1.1.11');
    for(my $id = 0; $id < @traffic; $id++){
        $result = $session->get_table(-baseoid => $traffic[$id]);
        if(!defined $result){
            return 1;
        }
        my $count = 0;
        foreach(oid_lex_sort(keys(%{$result}))){
            if($id == 0){
                $ifName[$count++] = $result->{$_};
            }
            elsif($id == 1){
                $InOctets[$count++] = $result->{$_};
            }
            elsif($id == 2){
                $InUcastPkts[$count++] = $result->{$_};
            }
            elsif($id == 3){
                $OutOctets[$count++] = $result->{$_};
            }
            elsif($id == 4){
                $OutUcastPkts[$count++] = $result->{$_};
            }
        }
    }
   
    for(my $id = 0; $id < @ifName; $id++){
        $sql = "SELECT * FROM cur_traffic WHERE ".
               "SnmpIp='$snmpparms{$snmpvar[4]}' AND `ifName`='$ifName[$id]'";
        my @data = &select_data();
        $sql = " `cur_traffic` SET `CurTime`='$starttime',`SnmpIp`='$snmpparms{$snmpvar[4]}',".
               "`ifName`='$ifName[$id]',`InOctets`='$InOctets[$id]',`InUcastPkts`='$InUcastPkts[$id]',".
               "`OutOctets`='$OutOctets[$id]',`OutUcastPkts`='$OutUcastPkts[$id]',";
        if(!@data){
            $sql = "INSERT INTO ".$sql."`CurDate`='$nowday',".
                   "`FInOctets`='$InOctets[$id]',`FOutOctets`='$OutOctets[$id]';";
            &update_data("cur_traffic");
            next;
        }
       
        $total_time = $starttime - $data[0];
        my $FInOctets = $InOctets[$id];
        my $FOutOctets = $OutOctets[$id];
        $InOctets[$id] = sprintf("%.2f", ($InOctets[$id]-$data[3])/(1024*$total_time));
        $InUcastPkts[$id] = sprintf("%.2f", ($InUcastPkts[$id]-$data[4])/$total_time);
        $OutOctets[$id] = sprintf("%.2f", ($OutOctets[$id]-$data[5])/(1024*$total_time));
        $OutUcastPkts[$id] = sprintf("%.2f", ($OutUcastPkts[$id]-$data[6])/$total_time);
        my $MaxInOctets = ($InOctets[$id] > $data[7]) ? $InOctets[$id] : $data[7];
        my $MaxInUcastPkts = ($InUcastPkts[$id] > $data[8]) ? $InUcastPkts[$id] : $data[8];
        my $MaxOutOctets = ($OutOctets[$id] > $data[9]) ? $OutOctets[$id] : $data[9];
        my $MaxOutUcastPkts = ($OutUcastPkts[$id] > $data[10]) ? $OutUcastPkts[$id] : $data[10];
        $sql = "UPDATE ".$sql."`MaxInOctets`='$MaxInOctets',`MaxInUcastPkts`='$MaxInUcastPkts',".
               "`MaxOutOctets`='$MaxOutOctets',`MaxOutUcastPkts`='$MaxOutUcastPkts',".
               "`SpeedInOctets`='$InOctets[$id]',`SpeedOutOctets`='$OutOctets[$id]'";
        if($nowday ne $data[11]){
            my $yesterdayin = $FInOctets-$data[12];
            my $yesterdayout = $FOutOctets-$data[13];
            $sql = $sql.",`CurDate`='$nowday',`FInOctets`='$FInOctets',`FOutOctets`='$FOutOctets',".
                   "`InOctetsed`='$yesterdayin',`OutOctetsed`='$yesterdayout'";
        }
        $sql = $sql." WHERE SnmpIp='$snmpparms{$snmpvar[4]}' AND ifName='$ifName[$id]';";
        update_data("cur_traffic");
        
        $sql = "INSERT INTO monitortraffic (hostip,timed,ifname,inoctets,".
               "inpkts,outoctets,outpkts) VALUES ('$snmpparms{$snmpvar[4]}',".
               "'$currenttime','$ifName[$id]','$InOctets[$id]','$InUcastPkts[$id]',".
               "'$OutOctets[$id]','$OutUcastPkts[$id]');";
        if(&update_data("monitortraffic")){
            return 1;
        }
    }
    return 0;
}

1;
