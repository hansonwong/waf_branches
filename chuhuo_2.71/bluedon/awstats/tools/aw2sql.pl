#!/usr/bin/perl
# ----- aw2sql 0.1 beta (c) 2005 Miguel Angel Liebana -----
# Aw2sql comes with ABSOLUTELY NO WARRANTY. It's a free software distributed
# with a GNU General Public License (See LICENSE file for details).
# Important:
# You must configure some basic info to start using this script:
#   $DataDir = '/www/awstats' => Where do you store the awstat temp files
#   $dbuser = 'user'          => User name for mysql
#   $dbpass = 'secret'        => Password to access mysql
#   $host = 'localhost'       => Where is the mysql server
# This script creates a database for each domain you want to control.
# This database must be named like your "config file"_log. Example:
#  If you name your config file:
#         /etc/awstats/awstats.myserver.conf
#  And awstats creates temp files with the name:
#         awstats022005.myserver.txt
#  Then your database must be named "myserver_log". Easy, don't you think?
#

require 5.005;
use DBI;
use Geo::IP;
use Getopt::Long;
use Time::Local;
use strict;no strict "refs";
use Encode;
use URI::Escape;
use Encode::Detect::Detector;

use vars qw/
$VERSION $DIR $PROG $Extension $SiteConfig $DataDir $MonthConfig $YearConfig
$nowsec $nowmin $nowhour $nowday $nowmonth $nowyear $nowwday $nowyday
@data @dataname @datanumelem $logfile $flag
$dsn $dbname $dbuser $dbpass $dbhost $dbh $sth $rows $sql
%general %daily %hours %session %domain %os %unkos %browser %unkbrowser %ft
%screen %misc %worms %robot %errors %e404 %visit %pages %origin %keywordsflag
%searchref %pageref %searchwords %searchkeywords %webagent $citydat $dbconf
/;

my $line;
$dbconf = '/usr/local/bluedon/monitor/etc/main.properties';
open(FILE, $dbconf) or error("can not open $dbconf");
while(chomp($line = <FILE>)){
    my @data = split(/ /, $line);
    if($data[0] eq 'cfdbfront.name:'){
        $dbname = $data[1];
    }
    elsif($data[0] eq 'cfdbfront.user:'){
        $dbuser = $data[1];
    }
    elsif($data[0] eq 'cfdbfront.passwd:'){
        $dbpass = $data[1];
    }
}
close(FILE);
$dbhost = 'localhost';

$VERSION = "0.1"; # Version of this script
$DIR     = ''; # Path of this script
$PROG    = ''; # Name of this script without the extension (aw2db)
$Extension   = ''; # Extension of this script (pl)
$SiteConfig  = ''; # What site do you want to add to the database? Database name = $Site_Config + "_log"
$MonthConfig = ''; # If you want to save the info of a month
$YearConfig  = ''; # If you want to save the info of a year
$DataDir = '/usr/local/bdwaf/logs_proxy/data/';
$citydat = '/usr/local/bluedon/awstats/etc/GeoLiteCity.dat';
$logfile = '/usr/local/bluedon/awstats/var/aw2sql.log';

#############
# Functions #
#############

#------------------------------------------------------------------------------
# Function:   Shows an error message and exits
# Parameters: Message with the error details
# Input:    msg
# Output:   stdout logfile
# Return:   None
#------------------------------------------------------------------------------
sub error
{
    print "Error: $_[0]\n";
    if(open(LOG, ">>$logfile")){
        printf LOG "Error: $_[0]\n";
        close(LOG);
    }else{
        print "Can't find the data file:\n\t$logfile\n";
    }
    exit 1;
}

#------------------------------------------------------------------------------
# Function:   Shows a warning
# Parameters: Message with the warning details
# Input:    msg
# Output:   stdout logfile
# Return:   None
#------------------------------------------------------------------------------
sub warning
{
    print "warning: $_[0]\n";
    if(open(LOG, ">>$logfile")){
        printf LOG "warning: $_[0]\n";
        close(LOG);
    }else{
        print "Can't find the data file:\n\t$logfile\n";
    }
}

#------------------------------------------------------------------------------
# Function:   Calc the number of days in a specific month
# Parameters: Month and year
# Input:    None
# Output:   None
# Return:   None
#------------------------------------------------------------------------------
sub NumberDays
{
    my $mo = $_[0];
    my $ye = $_[1] - 1900;
    my $nextmonth;
    # how many days have this month.. first minute 
    # of the next month, minus an hour (jeje)
    if($mo eq 12){
        $nextmonth=timelocal(0,0,0,1,0,$ye+1);
    }else{
        $nextmonth=timelocal(0,0,0,1,$mo,$ye);
    }
    $nextmonth = $nextmonth - 3600;
    # translate this time into sec, min, hours, ...
    my @m = localtime($nextmonth);
    return $m[3]; # We only need the number of day
}

#------------------------------------------------------------------------------
# Function:   Reads the data of the temp awstats file and stores this info into
#             an array.
# Parameters: None
# Input:    $DataDir $SiteConfig $MonthConfig $YearConfig
# Output:   @data @dataname @datanumelem
# Return:   None
#------------------------------------------------------------------------------
sub Read_Data
{
    my $filename="awstats".$MonthConfig.$YearConfig.".".$SiteConfig.".txt";
    if(!(-s "$DataDir$filename") || 
        !(-r "$DataDir$filename") || 
        !(open(DATA, "$DataDir$filename"))){
        error("Can't find the data file:\n\t$DataDir$filename");
    }

    my $seccion;
    my $num;
    my $begin=0;  # Indicates if we are into a section
    my @temp;

    while(defined(my $line=<DATA>)){
        chomp $line; s/\r//;
        if ($line =~ /^\s*#/){
            next;
        } # Ignore the comments

        $line =~ s/\s#.*$//;
        if($line =~ /^BEGIN_([^&]+)/i){
            # We save the name and number of elements of the section
            ($seccion,$num)=split(/ /, $1);
            push(@dataname,$seccion); # The name of the section
            push(@datanumelem,$num);  # The number of elements of this section (same array index)
            $begin=1;
            next;
        }elsif(($begin == 1) && ($line=~ /^END_$seccion/)){
            $begin=0;
            push(@data, [@temp]); # Multiarray
            $#temp = -1; # Empty the temp array
            next;
        }elsif($begin == 1){
            push(@temp, $line);
            next;
        }
    }
    close(DATA);
}

#------------------------------------------------------------------------------
# Function:   Search a section and returns its index for @data
# Parameters: The name of the section you want to search
# Input:    @dataname
# Output:   None
# Return:   Index of -1 if can't be found
#------------------------------------------------------------------------------
sub Search_Sec
{
    if($#dataname == 0){
        error("Empty databame array");
    }else{
        for(my $x=0;$x<=$#dataname;$x++){
            if($dataname[$x] eq $_[0]){
                return $x;
            }
        }
    }
    warning("The section ".$_[0]." can't be found");
    return -1;
}

#------------------------------------------------------------------------------
# Function:   Search the index of an element into a section of the data array
# Parameters: Name of the section and the element
# Input:    @data @datanumelem
# Output:   None
# Return:   Index of the element, or -1 if can't be found
#------------------------------------------------------------------------------
sub Search_Elem
{
    my $sec = Search_Sec($_[0]);
    my $elem = $_[1];
    my $num= $datanumelem[$sec];
    if($#data == 0){
        error("Empty data array");
    }else{
        for(my $z=0;$z<$num;$z++){
            if($data[$sec][$z] =~ /^$elem([^&]+)/i){
                return $z;
            }
        }
    }
    #warning("The element ".$elem." of section ".$_[0]." doesn't exists.");
    return -1;
}

#------------------------------------------------------------------------------
# Function:   Returns the info of a data index
# Parameters: Name of the section and element you want to read
# Input:    @data
# Output:   None
# Return:   The content of a data element or a "0 0 0 0 0 0 ..." string
#------------------------------------------------------------------------------
sub Read_Elem
{
    my $sec = Search_Sec($_[0]);
    my $elem = Search_Elem($_[0],$_[1]);
    if($sec==-1 || $elem==-1){
        return "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0";
    }else{
        return $data[$sec][$elem];
    }
}

#------------------------------------------------------------------------------
# Function:   Adds al the values of the column and returns the result
# Parameters: Name of the section and the column you want to calculate
# Input:    @data @datanumelem
# Output:   None
# Return:   Add result
#------------------------------------------------------------------------------
sub Suma_Colum
{
    my $sec = Search_Sec($_[0]); # seccion a mirar
    my $colum = $_[1] -1;        # columna a sumar
    my $num= $datanumelem[$sec]; # numero de elementos de la seccion
    my $suma=0;
    my @value;
    if($#data == 0){
        error("Vector de datos vacio");
    }else{
        for(my $z=0;$z<$num;$z++){
            @value = split(/ /, $data[$sec][$z]);
            $suma=$suma + $value[$colum];
            $#value = -1;
        }
    }
    return $suma;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the general table
# Parameters: None
# Input:    $YearConfig $MonthConfig
# Output:   %general
# Return:   None
#------------------------------------------------------------------------------
sub Read_General
{
    %general = ();
    my $t; # valor dummy $YearConfig
    $general {'year_monthed'} = $YearConfig.$MonthConfig;
    ($t,$general{'visits'}) = split(/ /, Read_Elem("GENERAL","TotalVisits"));
    ($t,$general{'visits_unique'}) = split(/ /, Read_Elem("GENERAL","TotalUnique"));
    $general{'pages'} = Suma_Colum("DAY",2); # sumar la segunda columna
    $general{'hits'} = Suma_Colum("DAY",3);
    $general{'bandwidth'} = Suma_Colum("DAY",4);
    $general{'pages_nv'} = Suma_Colum("TIME",5);
    $general{'hits_nv'} = Suma_Colum("TIME",6);
    $general{'bandwidth_nv'} = Suma_Colum("TIME",7);
    ($t,$general{'hosts_known'}) = split(/ /, Read_Elem("GENERAL","MonthHostsKnown"));
    ($t,$general{'hosts_unknown'}) = split(/ /, Read_Elem("GENERAL","MonthHostsUnKnown"));
    $general{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the daily table
# Parameters: $tempdate => what day you want to read stats?
# Input:    $YearConfig $MonthConfig
# Output:   %daily
# Return:   None
#------------------------------------------------------------------------------
sub Read_Daily
{
    %daily = ();
    my $t; # valor dummy
    my $day = $_[0];

    $daily {'day'} = $YearConfig.$MonthConfig.$day;
    ($t, $daily{'pages'}, $daily{'hits'}, $daily{'bandwidth'}, $daily{'visits'})
        = split(/ /, Read_Elem("DAY",$daily{'day'}));
    $daily{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the hours table
# Parameters: Of what hour we want the stats
# Input:    None
# Output:   %hours
# Return:   None
#------------------------------------------------------------------------------
sub Read_Hours
{
    %hours = ();
    my $readhour = $_[0];
    ($hours{'hour'}, $hours{'pages'}, $hours{'hits'}, $hours{'bandwidth'}) 
        = split(/ /, Read_Elem("TIME",$readhour));
    $hours {'year_monthed'} = $YearConfig.$MonthConfig;
    $hours{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the Session table
# Parameters: The session element we want to read stats
# Input:    @data
# Output:   %session
# Return:   None
#------------------------------------------------------------------------------
sub Read_Session
{
    %session = ();
    my $sec = Search_Sec("SESSION");
    my $id = $_[0];
    ($session{'ranged'}, $session{'visits'}) = split(/ /, $data[$sec][$id]);
    $session {'year_monthed'} = $YearConfig.$MonthConfig;
    $session{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the domain table
# Parameters: The domain/countrie we want to read stats
# Input:    @data
# Output:   %domain
# Return:   None
#------------------------------------------------------------------------------
sub Read_Domain
{
    %domain = ();
    my $sec = Search_Sec("DOMAIN");
    my $id = $_[0];
    ($domain{'code'}, $domain{'pages'}, $domain{'hits'}, $domain{'bandwidth'}) = split(/ /, $data[$sec][$id]);
    $domain {'year_monthed'} = $YearConfig.$MonthConfig;
    $domain{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the OS table
# Parameters: The os we want to read stats
# Input:    @data $YearConfig $MonthConfig
# Output:   %os
# Return:   None
#------------------------------------------------------------------------------
sub Read_OS
{
    %os = ();
    my $sec = Search_Sec("OS");
    my $id = $_[0];
    ($os{'name'}, $os{'hits'}) = split(/ /, $data[$sec][$id]);
    $os{'year_monthed'} = $YearConfig.$MonthConfig;
    $os{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the unkos table
# Parameters: The unknown OS we want to read stats
# Input:    @data
# Output:   %unkos
# Return:   None
#------------------------------------------------------------------------------
sub Read_unkos
{
    %unkos = ();
    my $sec = Search_Sec("UNKNOWNREFERER");
    my $id = $_[0];
    ($unkos{'agent'}, $unkos{'lastvisit'}) = split(/ /, $data[$sec][$id]);
    $unkos{'agent'} =~ s/\'//g;
    $unkos{'year_monthed'} = $YearConfig.$MonthConfig;
    $unkos{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the browser table
# Parameters: The browser we want to read stats
# Input:    @data $YearConfig $MonthConfig
# Output:   %browser
# Return:   None
#------------------------------------------------------------------------------
sub Read_Browser
{
    %browser = ();
    my $sec = Search_Sec("BROWSER");
    my $id = $_[0];
    ($browser{'name'}, $browser{'hits'}) = split(/ /, $data[$sec][$id]);
    $browser{'year_monthed'} = $YearConfig.$MonthConfig;
    $browser{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the unkbrowser table
# Parameters: The unknown browser we want to read stats
# Input:    @data
# Output:   %unkbrowser
# Return:   None
#------------------------------------------------------------------------------
sub Read_unkbrowser
{
    %unkbrowser = ();
    my $sec = Search_Sec("UNKNOWNREFERERBROWSER");
    my $id = $_[0];
    ($unkbrowser{'agent'}, $unkbrowser{'lastvisit'}) = split(/ /, $data[$sec][$id]);
    $unkbrowser{'agent'} =~ s/\'//g;
    $unkbrowser{'year_monthed'} = $YearConfig.$MonthConfig;
    $unkbrowser{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the filetypes table
# Parameters: The file type we want to read stats
# Input:    @data
# Output:   %ft
# Return:   None
#------------------------------------------------------------------------------
sub Read_FileTypes
{
    %ft = ();
    my $sec = Search_Sec("FILETYPES");
    my $id = $_[0];
    ($ft{'type'}, $ft{'hits'}, $ft{'bandwidth'}, $ft{'bwwithoutcompress'}, $ft{'bwaftercompress'}) 
        = split(/ /, $data[$sec][$id]);
    $ft{'year_monthed'} = $YearConfig.$MonthConfig;
    $ft{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the screen table
# Parameters: The screen resolution we want to read stats
# Input:    @data
# Output:   %screen
# Return:   None
#------------------------------------------------------------------------------
sub Read_Screen
{
    %screen = ();
    my $sec = Search_Sec("SCREENSIZE");
    my $id = $_[0];
    ($screen{'size'}, $screen{'hits'}) = split(/ /, $data[$sec][$id]);
    $screen{'year_monthed'} = $YearConfig.$MonthConfig;
    $screen{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the misc table
# Parameters: The misc element we want to read stats
# Input:    @data
# Output:   %misc
# Return:   None
#------------------------------------------------------------------------------
sub Read_Misc
{
    %misc = ();
    my $sec = Search_Sec("MISC");
    my $id = $_[0];
    ($misc{'text'}, $misc{'pages'}, $misc{'hits'}, $misc{'bandwidth'}) = split(/ /, $data[$sec][$id]);
    $misc{'year_monthed'} = $YearConfig.$MonthConfig;
    $misc{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the worms table
# Parameters: The worms we want to read stats
# Input:    @data
# Output:   %worms
# Return:   None
#------------------------------------------------------------------------------
sub Read_Worms
{
    %worms = ();
    my $sec = Search_Sec("WORMS");
    my $id = $_[0];
    ($worms{'text'}, $worms{'hits'}, $worms{'bandwidth'}, $worms{'lastvisit'}) = split(/ /, $data[$sec][$id]);
    $worms{'year_monthed'} = $YearConfig.$MonthConfig;
    $worms{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the robots table
# Parameters: The robots we want to read stats
# Input:    @data
# Output:   %robots
# Return:   None
#------------------------------------------------------------------------------
sub Read_Robot
{
    %robot = ();
    my $sec = Search_Sec("ROBOT");
    my $id = $_[0];
    ($robot{'name'}, $robot{'hits'}, $robot{'bandwidth'}, $robot{'lastvisit'}, $robot{'hitsrobots'}) 
        = split(/ /, $data[$sec][$id]);
    $robot{'year_monthed'} = $YearConfig.$MonthConfig;
    $robot{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the errors table
# Parameters: The error id we want to read stats
# Input:    @data
# Output:   %errors
# Return:   None
#------------------------------------------------------------------------------
sub Read_Errors
{
    %errors = ();
    my $sec = Search_Sec("ERRORS");
    my $id = $_[0];
    ($errors{'code'}, $errors{'hits'}, $errors{'bandwidth'}) = split(/ /, $data[$sec][$id]);
    $errors{'year_monthed'} = $YearConfig.$MonthConfig;
    $errors{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the errors404 table
# Parameters: The error id we want to read stats
# Input:    @data
# Output:   %e404
# Return:   None
#------------------------------------------------------------------------------
sub Read_Errors404
{
    %e404 = ();
    my $sec = Search_Sec("SIDER_404");
    my $id = $_[0];
    ($e404{'url'}, $e404{'hits'}, $e404{'referer'}) = split(/ /, $data[$sec][$id]);
    $e404{'year_monthed'} = $YearConfig.$MonthConfig;
    $e404{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the visitors table
# Parameters: The visitor index we want to read stats
# Input:    @data
# Output:   %visit
# Return:   None
#------------------------------------------------------------------------------
sub Read_Visitors
{
    %visit = ();
    my $sec = Search_Sec("VISITOR");
    my $id = $_[0];
    ($visit{'host'}, $visit{'pages'}, $visit{'hits'}, $visit{'bandwidth'}, 
        $visit{'lastvisit'}, $visit{'startlastvisit'}, $visit{'lastpage'}) 
        = split(/ /, $data[$sec][$id]);
    $visit{'year_monthed'} = $YearConfig.$MonthConfig;
    $visit{'domain'} = $SiteConfig;
  
    my $gi = Geo::IP->open($citydat, GEOIP_STANDARD);
    my $record = $gi->record_by_name($visit{'host'});
    if($record){
        if($record->country_code){
            $visit{'country_code'} = $record->country_code;
        }
        if($record->country_name){
            $visit{'country_name'} = $record->country_name;
            $visit{'country_name'} =~ s/\'//g;
        }
        if($record->region_name){
            $visit{'province'} = $record->region_name;
            $visit{'province'} =~ s/\'//g;
        }
        if($record->city){
            $visit{'city'} = $record->city;
            $visit{'city'} =~ s/\'//g;
        }
    }
    if(!$visit{'country_code'}){
        $visit{'country_code'} = 'unknow';
    }
    if(!$visit{'country_name'}){
        $visit{'country_name'} = 'unknow';
    }
    if(!$visit{'province'}){
        $visit{'province'} = 'unknow';
    }
    if(!$visit{'city'}){
        $visit{'city'} = 'unknow';
    }
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the pages more visited table
# Parameters: The page index we want to read stats
# Input:    @data
# Output:   %pages
# Return:   None
#------------------------------------------------------------------------------
sub Read_Pages
{
    %pages = ();
    my $sec = Search_Sec("SIDER");
    my $id = $_[0];
    ($pages{'url'}, $pages{'pages'}, $pages{'bandwidth'}, $pages{'entry'}, 
        $pages{'exited'}) = split(/ /, $data[$sec][$id]);
    $pages{'url'} =~ s/\'//g;
    $pages{'year_monthed'} = $YearConfig.$MonthConfig;
    $pages{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data of the origin of the visits
# Parameters: The row we want to read
# Input:    @data
# Output:   %origin
# Return:   None
#------------------------------------------------------------------------------
sub Read_Origin
{
    %origin = ();
    my $sec = Search_Sec("ORIGIN");
    my $id = $_[0];
    ($origin{'fromed'}, $origin{'pages'}, $origin{'hits'}) = split(/ /, $data[$sec][$id]);
    $origin{'year_monthed'} = $YearConfig.$MonthConfig;
    $origin{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data with the search referrers
# Parameters: The engine we want to read
# Input:    @data
# Output:   %searchref
# Return:   None
#------------------------------------------------------------------------------
sub Read_Searchref
{
    %searchref = ();
    my $sec = Search_Sec("SEREFERRALS");
    my $id = $_[0];
    ($searchref{'engine'}, $searchref{'pages'}, $searchref{'hits'}) = split(/ /, $data[$sec][$id]);
    $searchref{'year_monthed'} = $YearConfig.$MonthConfig;
    $searchref{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data with referrers from other pages
# Parameters: The referrer we want to read
# Input:    @data
# Output:   %pageref
# Return:   None
#------------------------------------------------------------------------------
sub Read_Pageref
{
    %pageref = ();
    my $sec = Search_Sec("PAGEREFS");
    my $id = $_[0];
    ($pageref{'url'}, $pageref{'pages'}, $pageref{'hits'}) = split(/ /, $data[$sec][$id]);
    $pageref{'year_monthed'} = $YearConfig.$MonthConfig;
    $pageref{'domain'} = $SiteConfig;
}

#------------------------------------------------------------------------------
# Function:   Creates the data with the search words
# Parameters: The word
# Input:    @data
# Output:   %searchwords
# Return:   None
#------------------------------------------------------------------------------
sub Read_Searchwords
{
    %searchwords = ();
    my $sec = Search_Sec("SEARCHWORDS");
    my $id = $_[0];
    ($searchwords{'words'}, $searchwords{'hits'}) = split(/ /, $data[$sec][$id]);
    $searchwords{'year_monthed'} = $YearConfig.$MonthConfig;
    $searchwords{'domain'} = $SiteConfig;
  
    $searchwords{'words'} = URI::Escape::uri_unescape($searchwords{'words'});
    my $codetype = detect($searchwords{'words'});
    $codetype =~ s/Big5/gbk/;
    if($codetype){
        unless($codetype =~ /UTF/){
            $searchwords{'words'} = encode("utf-8", decode($codetype, $searchwords{'words'}));
        }
    }
}

#------------------------------------------------------------------------------
# Function:   Creates the data with the search words
# Parameters: The word
# Input:    @data
# Output:   %searchkeywords
# Return:   None
#------------------------------------------------------------------------------
sub Read_Searchkeywords
{
    %searchkeywords = ();
    my $sec = Search_Sec("KEYWORDS");
    my $id = $_[0];
    ($searchkeywords{'words'}, $searchkeywords{'hits'}) = split(/ /, $data[$sec][$id]);
    $searchkeywords{'year_monthed'} = $YearConfig.$MonthConfig;
    $searchkeywords{'domain'} = $SiteConfig;
  
    $searchkeywords{'words'} = URI::Escape::uri_unescape($searchkeywords{'words'});
    my $codetype = detect($searchkeywords{'words'});
    $codetype =~ s/Big5/gbk/;
    if($codetype){
        unless($codetype && $codetype =~ /UTF/){
            $searchkeywords{'words'} = encode("utf-8", decode($codetype, $searchkeywords{'words'}));
        }
    }
}

sub Read_Webvisit
{    
    %webagent = ();
    my $sec = Search_Sec("WEBVISIT");
    ($webagent{'miss'}, $webagent{'hit'}, $webagent{'bandwidth_miss'}, 
        $webagent{'bandwidth_hit'}) = split(/ /, $data[$sec][0]);
    $webagent{'year_monthed'} = $YearConfig.$MonthConfig;
    $webagent{'domain'} = $SiteConfig;
}
#------------------------------------------------------------------------------
# Function:   Creates the mysql table format 
# Parameters: The word
# Input:    $type, $tables, $field, %hashname
# Output:   $sql
# Return:   None
#------------------------------------------------------------------------------
sub Table_Format
{
    my $id = 0;
    my ($hashname, $type, $tables, $dated, $field, $varstr) = @_;
    
    $sql = "$type `$tables` SET ";
    if($type eq 'UPDATE'){
        while(my ($key, $value) = each %$hashname){
            if(!$value || $key eq $field || 
               $key eq $dated || 
               $key eq 'domain'){
                next;
            }
            if($id++){
                $sql .= ',';
            }
            if($key eq $varstr){
                $sql .= "`$key`='$value'";
            }else{
                $sql .= "`$key`=$key + $value";
            }
        }
        $sql .= " WHERE `$dated`='$$hashname{$dated}' ".
	              "AND `domain`='$$hashname{'domain'}'";
        if($field ne ''){
            $sql .= " AND `$field`='$$hashname{$field}'";
        }
        $sql .= " LIMIT 1;";
    }else{
        while(my ($key, $value) = each %$hashname){
            if($id++){
                $sql .= ',';
            }
            $sql .= "`$key`='$value'";
        }
        $sql .= ';';
    }
    return $id;
}


########
# Main #
########

# We save the path of the scritp and its name
($DIR=$0) =~ s/([^\/\\]+)$//; ($PROG=$1) =~ s/\.([^\.]*)$//; $Extension=$1;
$DIR||='.'; $DIR =~ s/([^\/\\])[\\\/]+$/$1/;

my $starttime=time();
($nowsec,$nowmin,$nowhour,$nowday,$nowmonth,$nowyear,$nowwday,$nowyday) = localtime($starttime);

if ($nowyear < 100) { $nowyear+=2000; } else { $nowyear+=1900; }
if (++$nowmonth < 10) { $nowmonth = "0$nowmonth"; }
if ($nowday < 10) { $nowday = "0$nowday"; }
if ($nowhour < 10) { $nowhour = "0$nowhour"; }
if ($nowmin < 10) { $nowmin = "0$nowmin"; }
if ($nowsec < 10) { $nowsec = "0$nowsec"; }

GetOptions("config=s"=>\$SiteConfig, "month=i"=>\$MonthConfig, "year=i"=>\$YearConfig);
if(!$SiteConfig){
    print "\n";
    print "----- $PROG $VERSION (c) 2005 Miguel Angel Liebana -----\n";
    print "Aw2sql is a free analyzer that parses the AWStats (copyright of Laurent\n";
    print "Destailleur) and saves its results into a MySQL database.\n";
    print "After this is done,you can show this results from PHP, perl, ASP or other\n";
    print "languages, with your own website design.\n";
    print "Aw2sql comes with ABSOLUTELY NO WARRANTY. It's a free software distributed\n";
    print "with a GNU General Public License (See LICENSE file for details).\n";
    print "\n";
    print "Syntax: $PROG.$Extension -config=virtualhostname [options]\n";
    print "\n";
    print "Options:\n";
    print "  -config        the site you want to analyze (not optional)\n";
    print "  -month=MM      to output a report for an old month MM\n";
    print "  -year=YYYY     to output a report for an old year YYYY\n";
    print "\n";
    print "Example:\n";
    print "  $ ./".$PROG.$Extension." -config=mysite\n";
    print "\n";
    print "Important:\n";
    print "  In the example, the database 'mysite_log' must exists in mysql\n";
    print "  and you must modify the values of this script variables, with\n";
    print "  the proper user and pass to access the database\n";
    print "\n";
    exit 2;
}

if (! $MonthConfig) { $MonthConfig = "$nowmonth"; }
elsif (($MonthConfig <= 0) || ($MonthConfig > 12)) { error("Wrong Month"); }
elsif ($MonthConfig < 10) { $MonthConfig = "0$MonthConfig"; }
if (! $YearConfig) { $YearConfig = "$nowyear"; }
elsif (($YearConfig < 1900) || ($YearConfig > 2100)) { error("Wrong Year"); }
# Well, I don't think this script lives until the year 2100
# but who knows? xD ... I don't want a Year 2KC effect xDDD

Read_Data();  # Reads the temp data file of awstats
# Access the database. The database must exists.
$dsn = "DBI:mysql:database=$dbname;host=$dbhost";
# Connect to the database
$dbh = DBI->connect($dsn,$dbuser,$dbpass, {RaiseError => 0, PrintError => 0})
  or error("Imposible conectar con el servidor: $DBI::err ($DBI::errstr)\n");
$dbh->do("SET character_set_client = 'utf8'");
$dbh->do("SET character_set_connection = 'utf8'");
$dbh->do("SET character_set_results= 'utf8'");


#################
# GENERAL TABLE #
#################
$sql = '';
$flag = 0;
Read_General();
$sth = $dbh->prepare("SELECT COUNT(*) FROM `general` WHERE ".
                     "`year_monthed`='$general{'year_monthed'}' ".
                     "AND `domain`='$general{'domain'}'");
$sth->execute();
my $count = $sth->fetchrow_array();
$sth->finish();

if($count == 1){
    $flag = &Table_Format(\%general, 'UPDATE', 'general', 'year_monthed');
}else{
    if($count > 1){
        warning("There are repeated rows for the date $general{'year_monthed'} ".
                "and $general{'domain'} into the 'general' table of $dbname\n");
        my $delsql = "DELETE FROM `general` WHERE `year_monthed`=".
                     "'$general{'year_monthed'}' AND `domain`='$general{'domain'}';";
	      $rows = $dbh->do($delsql);
    }
    $flag = &Table_Format(\%general, 'INSERT INTO', 'general');
}

if($flag){
    $rows = $dbh->do($sql);
    if(!$rows){
        warning("We can't add a new rows to the 'general' table ".
                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
    }
}
%general = ();

###############
# DAILY TABLE #
###############
my $tempdate;
my $maxday;
if($nowmonth == $MonthConfig){
    $maxday = $nowday;
}else{
    $maxday = NumberDays($MonthConfig, $YearConfig);
}

for(my $i=1; $i<=$maxday; $i++){
    if ($i < 10) {
        $tempdate = "0$i";
    }else{
        $tempdate = $i;
    }

    $sql = '';
    $flag = 0;
    Read_Daily($tempdate);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `daily` WHERE ".
                         "`day`='$daily{'day'}' AND `domain`='$daily{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%daily, 'UPDATE', 'daily', 'day');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $daily{'day'} ".
                    "and  $daily{'domain'} into the 'daily' table of $dbname\n");
            my $delsql = "DELETE FROM `daily` WHERE `day`='$daily{'day'}' ".
                         "AND `domain`='$daily{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%daily, 'INSERT INTO', 'daily');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'daily' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%daily = ();

###############
# HOURS TABLE #
###############
for(my $i=0; $i<=23; $i++){
    $sql = '';
    $flag = 0;
    Read_Hours($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `hours` WHERE `hour`='$i' AND `year_monthed`=".
                         "'$hours{'year_monthed'}' AND `domain`='$hours{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%hours, 'UPDATE', 'hours', 'year_monthed', 'hour');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $i, $hours{'year_monthed'} ".
                    "and $hours{'domain'} into the 'hours' table of $dbname\n");
            my $delsql = "DELETE FROM `hours` WHERE `hour`='$i' AND `year_monthed`=".
                         "'$hours{'year_monthed'}' AND `domain`='$hours{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%hours, 'INSERT INTO', 'hours');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'hours' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%hours = ();

#################
# SESSION TABLE #
#################
my $max = $datanumelem[Search_Sec("SESSION")];
for (my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Session($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `session` WHERE `year_monthed`='$session{'year_monthed'}' ".
                         "AND `ranged`='$session{'ranged'}' AND `domain`='$session{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%session, 'UPDATE', 'session', 'year_monthed', 'ranged');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $session{'ranged'}, ".
                    "$session{'year_monthed'} and $session{'domain'} ".
                    "into the 'session' table of $dbname\n");
            my $delsql = "DELETE FROM `session` WHERE `ranged`='$session{'ranged'}' ".
                         "AND `year_monthed`='$session{'year_monthed'}' ".
                         "AND `domain`='$session{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%session, 'INSERT INTO', 'session');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'session' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%session = ();

################
# DOMAIN TABLE #
################
my $max = $datanumelem[Search_Sec("DOMAIN")];
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Domain($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `domain` WHERE `year_monthed`='$domain{'year_monthed'}' ".
                         "AND `code`='$domain{'code'}' AND `domain`='$domain{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%domain, 'UPDATE', 'domain', 'year_monthed', 'code');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $domain{'code'}, ".
                    "$domain{'year_monthed'} and $domain{'domain'} ".
                    "into the 'domain' table of $dbname\n");
            my $delsql = "DELETE FROM `domain` WHERE `code`='$domain{'code'}' ".
                         "AND `year_monthed`='$domain{'year_monthed'}' ".
                         "AND `domain`='$domain{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%domain, 'INSERT INTO', 'domain');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'domain' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%domain = ();

############
# OS TABLE #
############
my $max = $datanumelem[Search_Sec("OS")];
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_OS($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `os` WHERE `name`='$os{'name'}' AND ".
                         "`year_monthed`='$os{'year_monthed'}' AND `domain`='$os{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%os, 'UPDATE', 'os', 'year_monthed', 'name');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $os{'name'}, ".
                    "$os{'year_monthed'} and $os{'domain'} ".
                    "into the 'os' table of $dbname\n");
            my $delsql = "DELETE FROM `os` WHERE `name`='$os{'name'}' ".
                         "AND `year_monthed`='$os{'year_monthed'}' ".
                         "AND `domain`='$os{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%os, 'INSERT INTO', 'os');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'os' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%os = ();

###############
# unkOS TABLE #
###############
my $max = $datanumelem[Search_Sec("UNKNOWNREFERER")];
#$rows = $dbh->do("TRUNCATE TABLE `unkos`"); # Vaciamos la tabla
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_unkos($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `unkos` WHERE `year_monthed`='$unkos{'year_monthed'}' ".
                         "AND `agent`='$unkos{'agent'}' AND `domain`='$unkos{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%unkos, 'UPDATE', 'unkos', 'year_monthed', 'agent', 'lastvisit');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $unkos{'name'}, ".
                    "$unkos{'year_monthed'} and $unkos{'domain'} ".
                    "into the 'unkos' table of $dbname\n");
            my $delsql = "DELETE FROM `unkos` WHERE `name`='$unkos{'name'}' ".
                         "AND `year_monthed`='$unkos{'year_monthed'}' ".
                         "AND `domain`='$unkos{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%unkos, 'INSERT INTO', 'unkos');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'unkos' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%unkos = ();

#################
# Browser TABLE #
#################
my $max = $datanumelem[Search_Sec("BROWSER")];
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Browser($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `browser` WHERE `name`='$browser{'name'}' AND ".
                         "`year_monthed`='$browser{'year_monthed'}' AND `domain`='$browser{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%browser, 'UPDATE', 'browser', 'year_monthed', 'name');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $browser{'name'}, ".
                    "$browser{'year_monthed'} and $browser{'domain'} ".
                    "into the 'browser' table of $dbname\n");
            my $delsql = "DELETE FROM `browser` WHERE `name`='$browser{'name'}' ".
                         "AND `year_monthed`='$browser{'year_monthed'}' ".
                         "AND `domain`='$browser{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%browser, 'INSERT INTO', 'browser');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'browser' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%browser = ();

####################
# unkbrowser TABLE #
####################
my $max = $datanumelem[Search_Sec("UNKNOWNREFERERBROWSER")];
#$rows = $dbh->do("TRUNCATE TABLE `unkbrowser`"); # Vaciamos la tabla
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_unkbrowser($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `unkbrowser` WHERE `year_monthed`='$unkbrowser{'year_monthed'}' ".
                         "AND `agent`='$unkbrowser{'agent'}' AND `domain`='$unkbrowser{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%unkbrowser, 'UPDATE', 'unkbrowser', 'year_monthed', 'agent', 'lastvisit');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $unkbrowser{'agent'}, ".
                    "$unkbrowser{'year_monthed'} and $unkbrowser{'domain'} ".
                    "into the 'unkbrowser' table of $dbname\n");
            my $delsql = "DELETE FROM `unkbrowser` WHERE `agent`='$unkbrowser{'agent'}' ".
                         "AND `year_monthed`='$unkbrowser{'year_monthed'}' ".
                         "AND `domain`='$unkbrowser{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%unkbrowser, 'INSERT INTO', 'unkbrowser');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'unkbrowser' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%unkbrowser = ();

###################
# filetypes TABLE #
###################
my $max = $datanumelem[Search_Sec("FILETYPES")];
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_FileTypes($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `filetypes` WHERE `year_monthed`='$ft{'year_monthed'}' ".
                         "AND `type`='$ft{'type'}' AND `domain`='$ft{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%ft, 'UPDATE', 'filetypes', 'year_monthed', 'type');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $ft{'type'}, ".
                    "$ft{'year_monthed'} and $ft{'domain'} ".
                    "into the 'filetypes' table of $dbname\n");
            my $delsql = "DELETE FROM `filetypes` WHERE `type`='$ft{'type'}' ".
                         "AND `year_monthed`='$ft{'year_monthed'}' ".
                         "AND `domain`='$ft{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%ft, 'INSERT INTO', 'filetypes');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'filetypes' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%ft = ();

################
# screen TABLE #
################
my $max = $datanumelem[Search_Sec("SCREENSIZE")];
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Screen($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `screen` WHERE `year_monthed`='$screen{'year_monthed'}' ".
                         "AND `size`='$screen{'size'}' AND `domain`='$screen{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%screen, 'UPDATE', 'screen', 'year_monthed', 'size');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $screen{'size'}, ".
                    "$screen{'year_monthed'} and $screen{'domain'} ".
                    "into the 'screen' table of $dbname\n");
            my $delsql = "DELETE FROM `screen` WHERE `size`='$screen{'size'}' ".
                         "AND `year_monthed`='$screen{'year_monthed'}' ".
                         "AND `domain`='$screen{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%screen, 'INSERT INTO', 'screen');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'screen' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%screen = ();

##############
# Misc TABLE #
##############
my $max = $datanumelem[Search_Sec("MISC")];
#$rows = $dbh->do("TRUNCATE TABLE `misc`"); # Empty the table
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Misc($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `misc` WHERE `year_monthed`='$misc{'year_monthed'}' ".
                         "AND `text`='$misc{'text'}' AND `domain`='$misc{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%misc, 'UPDATE', 'misc', 'year_monthed', 'text');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $misc{'text'}, ".
                    "$misc{'year_monthed'} and $misc{'domain'} ".
                    "into the 'misc' table of $dbname\n");
            my $delsql = "DELETE FROM `misc` WHERE `text`='$misc{'text'}' ".
                         "AND `year_monthed`='$misc{'year_monthed'}' ".
                         "AND `domain`='$misc{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%misc, 'INSERT INTO', 'misc');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'misc' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%misc = ();

###############
# Worms TABLE #
###############
my $max = $datanumelem[Search_Sec("WORMS")];
#$rows = $dbh->do("TRUNCATE TABLE `worms`"); # Empty the table
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Worms($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `worms` WHERE `year_monthed`='$worms{'year_monthed'}' ".
                         "AND `text`='$worms{'text'}' AND `domain`='$worms{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%worms, 'UPDATE', 'worms', 'year_monthed', 'text', 'lastvisit');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $worms{'text'}, ".
                    "$worms{'year_monthed'} and $worms{'domain'} ".
                    "into the 'worms' table of $dbname\n");
            my $delsql = "DELETE FROM `worms` WHERE `text`='$worms{'text'}' ".
                         "AND `year_monthed`='$worms{'year_monthed'}' ".
                         "AND `domain`='$worms{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%worms, 'INSERT INTO', 'worms');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'worms' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%worms = ();

###############
# Robot TABLE #
###############
my $max = $datanumelem[Search_Sec("ROBOT")];
#$rows = $dbh->do("TRUNCATE TABLE `robot`"); # Empty the table
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Robot($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `robot` WHERE `year_monthed`='$robot{'year_monthed'}' ".
                         "AND `name`='$robot{'name'}' AND `domain`='$robot{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%robot, 'UPDATE', 'robot', 'year_monthed', 'name', 'lastvisit');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $robot{'name'}, ".
                    "$robot{'year_monthed'} and $robot{'domain'} ".
                    "into the 'robot' table of $dbname\n");
            my $delsql = "DELETE FROM `robot` WHERE `name`='$robot{'name'}' ".
                         "AND `year_monthed`='$robot{'year_monthed'}' ".
                         "AND `domain`='$robot{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%robot, 'INSERT INTO', 'robot');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'robot' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%robot = ();

################
# warnings TABLE #
################
my $max = $datanumelem[Search_Sec("ERRORS")];
#$rows = $dbh->do("TRUNCATE TABLE `errors`"); # Empty the table
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Errors($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `errors` WHERE `year_monthed`='$errors{'year_monthed'}' ".
                         "AND `code`='$errors{'code'}' AND `domain`='$errors{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%errors, 'UPDATE', 'errors', 'year_monthed', 'code');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $errors{'code'}, ".
                    "$errors{'year_monthed'} and $errors{'domain'} ".
                    "into the 'errors' table of $dbname\n");
            my $delsql = "DELETE FROM `errors` WHERE `code`='$errors{'code'}' ".
                         "AND `year_monthed`='$errors{'year_monthed'}' ".
                         "AND `domain`='$errors{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%errors, 'INSERT INTO', 'errors');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'errors' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%errors = ();

###################
# Errors404 TABLE #
###################
my $max = $datanumelem[Search_Sec("SIDER_404")];
#$rows = $dbh->do("TRUNCATE TABLE `errors404`"); # Empty the table
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Errors404($i);
    $e404{'url'} =~ tr/\'/&#039;/; # we subs the incorrect character ' with its html code
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `errors404` WHERE `year_monthed`='$e404{'year_monthed'}' ".
                         "AND `url`='$e404{'url'}' AND `domain`='$e404{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%e404, 'UPDATE', 'errors404', 'year_monthed', 'url', 'referer');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $e404{'url'}, ".
                    "$e404{'year_monthed'} and $e404{'domain'} ".
                    "into the 'errors404' table of $dbname\n");
            my $delsql = "DELETE FROM `errors404` WHERE `url`='$e404{'url'}' ".
                         "AND `year_monthed`='$e404{'year_monthed'}' ".
                         "AND `domain`='$e404{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%e404, 'INSERT INTO', 'errors404');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'errors404' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%e404 = ();

##################
# Visitors TABLE #
##################
my $tvisitors = "visitors_".$YearConfig.$MonthConfig;
my $max = $datanumelem[Search_Sec("VISITOR")];
#$rows = $dbh->do("TRUNCATE TABLE `visitors`");
for(my $i=0; $i<$max; $i++){
    $sql = '';
    Read_Visitors($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `$tvisitors` WHERE `year_monthed`='$visit{'year_monthed'}' ".
                         "AND `host`='$visit{'host'}' AND `domain`='$visit{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $sql = "UPDATE `$tvisitors` SET `pages`=pages + $visit{'pages'}, ".
               "`hits`=hits + $visit{'hits'}, `bandwidth`=bandwidth + ".
               "$visit{'bandwidth'}, `lastvisit`='$visit{'lastvisit'}'";
        if(!($visit{'startlastvisit'} eq '')){
            $sql = "$sql, `startlastvisit`='$visit{'startlastvisit'}'";
        }
        if(!($visit{'lastpage'} eq '')){
            $sql = "$sql, `lastpage`='$visit{'lastpage'}'";
        }
        $sql = "$sql WHERE `year_monthed`='$visit{'year_monthed'}' and ".
               "`host`='$visit{'host'}' and `domain`='$visit{'domain'}' LIMIT 1;";
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $visit{'host'}, ".
                    "$visit{'year_monthed'} and $visit{'domain'} ".
                    "into the '$tvisitors' table of $dbname\n");
            my $delsql = "DELETE FROM `$tvisitors` WHERE `host`='$visit{'host'}' ".
                         "AND `year_monthed`='$visit{'year_monthed'}' ".
                         "AND `domain`='$visit{'domain'}';";
	          $rows = $dbh->do($delsql);
        }

        my $id = 0;
        $sql = "INSERT INTO `$tvisitors` SET ";
        while(my ($key, $value) = each %visit){
            if($id++){
                $sql .= ',';
            }
            $sql .= "`$key`='$value'";
        }
        $sql .= ';';
    }

    $rows = $dbh->do($sql);
    if(!$rows){
        warning("We can't add a new visitor to the '$tvisitors' table ".
                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
    }
}
%visit = ();

###############
# Pages TABLE #
###############
my $tpages = "pages_".$YearConfig.$MonthConfig;
my $max = $datanumelem[Search_Sec("SIDER")];
#$rows = $dbh->do("TRUNCATE TABLE `pages`");
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Pages($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `$tpages` WHERE `year_monthed`='$pages{'year_monthed'}' ".
                         "and `url`='$pages{'url'}' and `domain`='$pages{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%pages, 'UPDATE', $tpages, 'year_monthed', 'url');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $pages{'url'}, ".
                    "$pages{'year_monthed'} and $pages{'domain'} ".
                    "into the '$tpages' table of $dbname\n");
            my $delsql = "DELETE FROM `$tpages` WHERE `url`='$pages{'url'}' ".
                         "AND `year_monthed`='$pages{'year_monthed'}' ".
                         "AND `domain`='$pages{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%pages, 'INSERT INTO', $tpages);
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the '$tpages' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%pages = ();

################
# Origin TABLE #
################

# From where comes our visits.
# From0 => Direct address / Bookmarks
# From1 => Unknown Origin
# From2 => Links from an Internet Search Engine (google, yahoo, etc..)
# From3 => Links from an external page (other web sites except search engines)
# From4 => Links from an internal page (other page on same site)
# From5 => Links from a NewsGroup
my $max = $datanumelem[Search_Sec("ORIGIN")];
#$rows = $dbh->do("TRUNCATE TABLE `origin`");
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Origin($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `origin` WHERE `year_monthed`='$origin{'year_monthed'}' ".
                         "AND `fromed`='$origin{'fromed'}' AND `domain`='$origin{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%origin, 'UPDATE', 'origin', 'year_monthed', 'fromed');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $origin{'fromed'}, ".
                    "$origin{'year_monthed'} and $origin{'domain'} ".
                    "into the 'origin' table of $dbname\n");
            my $delsql = "DELETE FROM `origin` WHERE `fromed`='$origin{'fromed'}' ".
                         "AND `year_monthed`='$origin{'year_monthed'}' ".
                         "AND `domain`='$origin{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%origin, 'INSERT INTO', 'origin');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'origin' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%origin = ();

###################
# searchref TABLE #
###################
my $max = $datanumelem[Search_Sec("SEREFERRALS")];
#$rows = $dbh->do("TRUNCATE TABLE `searchref`");
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Searchref($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `searchref` WHERE `year_monthed`='$searchref{'year_monthed'}' ".
                         "AND `engine`='$searchref{'engine'}' AND `domain`='$searchref{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%searchref, 'UPDATE', 'searchref', 'year_monthed', 'engine');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $searchref{'engine'}, ".
                    "$searchref{'year_monthed'} and $searchref{'domain'} ".
                    "into the 'searchref' table of $dbname\n");
            my $delsql = "DELETE FROM `searchref` WHERE `engine`='$searchref{'engine'}' ".
                         "AND `year_monthed`='$searchref{'year_monthed'}' ".
                         "AND `domain`='$searchref{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%searchref, 'INSERT INTO', 'searchref');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'searchref' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%searchref = ();

#################
# pageref TABLE #
#################
my $max = $datanumelem[Search_Sec("PAGEREFS")];
#$rows = $dbh->do("TRUNCATE TABLE `pageref`");
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Pageref($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `pageref` WHERE `year_monthed`='$pageref{'year_monthed'}' ".
                         "AND `url`='$pageref{'url'}' AND `domain`='$pageref{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%pageref, 'UPDATE', 'pageref', 'year_monthed', 'url');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $pageref{'url'}, ".
                    "$pageref{'year_monthed'} and $pageref{'domain'} ".
                    "into the 'pageref' table of $dbname\n");
            my $delsql = "DELETE FROM `pageref` WHERE `url`='$pageref{'url'}' ".
                         "AND `year_monthed`='$pageref{'year_monthed'}' ".
                         "AND `domain`='$pageref{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%pageref, 'INSERT INTO', 'pageref');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'pageref' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%pageref = ();

#####################
# searchwords TABLE #
#####################
undef %keywordsflag;
my $max = $datanumelem[Search_Sec("SEARCHWORDS")];
#$rows = $dbh->do("TRUNCATE TABLE `searchwords`");
for(my $i=0; $i<$max; $i++){
    $sql = '';
    $flag = 0;
    Read_Searchwords($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `searchwords` WHERE ".
                         "`year_monthed`='$searchwords{'year_monthed'}' ".
                         "AND `words`='$searchwords{'words'}' AND ".
                         "`domain`='$searchwords{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%searchwords, 'UPDATE', 'searchwords', 'year_monthed', 'words');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $searchwords{'words'}, ".
                    "$searchwords{'year_monthed'} and $searchwords{'domain'} ".
                    "into the 'searchwords' table of $dbname\n");
            my $delsql = "DELETE FROM `searchwords` WHERE `words`='$searchwords{'words'}' ".
                         "AND `year_monthed`='$searchwords{'year_monthed'}' ".
                         "AND `domain`='$searchwords{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%searchwords, 'INSERT INTO', 'searchwords');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'searchwords' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%searchwords = ();

########################
# searchkeywords TABLE #
########################
undef %keywordsflag;
my $max = $datanumelem[Search_Sec("KEYWORDS")];
#$rows = $dbh->do("TRUNCATE TABLE `searchkeywords`");
for(my $i=0; $i<$max; $i++){
    Read_Searchkeywords($i);
    $sth = $dbh->prepare("SELECT COUNT(*) FROM `searchkeywords` WHERE ".
                         "`year_monthed`='$searchkeywords{'year_monthed'}' ".
                         "AND `words`='$searchkeywords{'words'}' AND ".
                         "`domain`='$searchkeywords{'domain'}'");
    $sth->execute();
    my $count = $sth->fetchrow_array();
    $sth->finish();

    if($count == 1){
        $flag = &Table_Format(\%searchkeywords, 'UPDATE', 'searchkeywords', 'year_monthed', 'words');
    }else{
        if($count > 1){
            warning("There are repeated rows for the date $searchkeywords{'words'}, ".
                    "$searchkeywords{'year_monthed'} and $searchkeywords{'domain'} ".
                    "into the 'searchkeywords' table of $dbname\n");
            my $delsql = "DELETE FROM `searchkeywords` WHERE `words`='$searchkeywords{'words'}' ".
                         "AND `year_monthed`='$searchkeywords{'year_monthed'}' ".
                         "AND `domain`='$searchkeywords{'domain'}';";
	          $rows = $dbh->do($delsql);
        }
        $flag = &Table_Format(\%searchkeywords, 'INSERT INTO', 'searchkeywords');
    }

    if($flag){
        $rows = $dbh->do($sql);
        if(!$rows){
            warning("We can't add a new rows to the 'searchkeywords' table ".
  	                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
        }
    }
}
%searchkeywords = ();

##########################
# web agent: miss or hit #
##########################
$sql = '';
$flag = 0;
Read_Webvisit();
$sth = $dbh->prepare("SELECT COUNT(*) FROM `webagent` WHERE ".
                     "`year_monthed`='$webagent{'year_monthed'}' ".
                     "AND `domain`='$webagent{'domain'}'");
$sth->execute();
my $count = $sth->fetchrow_array();
$sth->finish();

if($count == 1){
    $flag = &Table_Format(\%webagent, 'UPDATE', 'webagent', 'year_monthed');
}else{
    if($count > 1){
        warning("There are repeated rows for the date $webagent{'year_monthed'} ".
                "and $webagent{'domain'} into the 'webagent' table of $dbname\n");
        my $delsql = "DELETE FROM `webagent` WHERE `year_monthed`=".
                     "'$webagent{'year_monthed'}' AND `domain`='$webagent{'domain'}';";
	      $rows = $dbh->do($delsql);
    }
    $flag = &Table_Format(\%webagent, 'INSERT INTO', 'webagent');
}

if($flag){
    $rows = $dbh->do($sql);
    if(!$rows){
        warning("We can't add a new rows to the 'webagent' table ".
                "in the $dbname database.\n $DBI::err ($DBI::errstr)");
    }
}
%webagent = ();

$dbh->disconnect();
