#!/usr/bin/perl

use strict;

my $SiteDomain;
my $err_out     = ' > /dev/null 2>&1';
my $logdir      = '/usr/local/bdwaf/logs_proxy/access/';
my $logconf     = '/usr/local/bluedon/awstats/etc/';
my $logsite     = '/usr/local/bluedon/monitor/etc/lastread';
my $sqlcmd      = '/usr/local/bluedon/awstats/tools/aw2sql.pl';
my $defaultconf = '/usr/local/bluedon/awstats/etc/default.conf';
my $datacmd     = '/usr/local/bluedon/awstats/wwwroot/cgi-bin/awstats.pl -update -config=';

sub get_curtime
{
    my $starttime=time();
    my ($nowsec,$nowmin,$nowhour,$nowday,$nowmonth,$nowyear,$nowwday,$nowyday) = localtime($starttime);
    if ($nowyear < 100) { $nowyear += 2000; }
    else { $nowyear += 1900; }
    if (++$nowmonth < 10) { $nowmonth = "0$nowmonth"; }
    if ($nowday < 10) { $nowday = "0$nowday"; }
    if ($nowhour < 10) { $nowhour = "0$nowhour"; }
    if ($nowmin < 10) { $nowmin = "0$nowmin"; }
    if ($nowsec < 10) { $nowsec = "0$nowsec"; }
    my $filename = $nowyear.$nowmonth."/access_".$nowday.".log";

    open(FILE, "+>$logsite") or dir("can not open file $logsite");
    chomp(my ($line) = <FILE>);
    my $buf = $filename;
    my @data = split(/ /, $line);
    if($data[0] && ($data[0] ne $filename)){
        $filename = $data[0];
        $sqlcmd = "$sqlcmd -year=$data[1] -month=$data[2] -config=";
    }
    else{
        $sqlcmd = "$sqlcmd -config=";
    }

    seek(FILE, 0, 0);
    printf FILE "$buf $nowyear $nowmonth\n";    
    close(FILE);
    return $filename;
}

opendir(DIR, $logdir) || die "Can't open directory $logdir";
my @dots = readdir(DIR);
closedir DIR;

my $flag = 0;
my $logpath = &get_curtime();
foreach my $line (@dots){ 
    print $line;
    if($line eq "." || $line eq '..' || $line eq 'error'){
        next;
    }
    
    print $line;
    $line =~ s/ //g;
    $SiteDomain = $line;
    $line = $logconf."awstats.".$line.".conf";
    if(-f $line){
        unlink($line);
    }

    my $LogFile = "$logdir/$SiteDomain /$logpath";
    if(! -f $LogFile){
        next;
    }
    `cp $defaultconf $line > /dev/null 2>&1`;
    `echo SiteDomain="$SiteDomain" >> $line`;
    `echo LogFile="$LogFile" >> $line`;
    `echo HostAliases="$SiteDomain www.$SiteDomain 127.0.0.1 localhost" >> $line`;
    #system($datacmd.$SiteDomain.$err_out);
    #system($sqlcmd.$SiteDomain.$err_out);
    system($datacmd.$SiteDomain);
    system($sqlcmd.$SiteDomain);
    printf $sqlcmd.$SiteDomain;
    $flag = 1;
}
if($flag == 1){
    system("rm /usr/local/bluedon/awstats/etc/awstats*");
    system("rm ".$logdir."/* -rf");
}

