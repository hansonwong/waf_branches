#!/usr/bin/perl

use DBI;
use strict;no strict "refs";

use vars qw/
  $logfile $dsn $dbname $dbuser $dbpass
  $dbhost $dbh $sth $rows $sql $dbconf
  @count $visits $vunique $pages $attack $htimes $bandwith
/;
$logfile = '/usr/local/bluedon/awstats/var/aw2sql.log';
$dbconf = '/usr/local/bluedon/monitor/etc/main.properties';

my $line;
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


###########
# funtion #
###########
#------------------------------------------------------------------------------
# Function:   Shows an error message and exits
# Parameters: Message with the error details
# Input:    msg
# Output:   None
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


########
# Main #
########
# Access the database. The database must exists.
$dsn = "DBI:mysql:database=$dbname;host=$dbhost";
# Connect to the database
$dbh = DBI->connect($dsn,$dbuser,$dbpass, {RaiseError => 0, PrintError => 0})
  or error("Imposible conectar con el servidor: $DBI::err ($DBI::errstr)\n");
$dbh->do("SET character_set_client = 'utf8'");
$dbh->do("SET character_set_connection = 'utf8'");
$dbh->do("SET character_set_results= 'utf8'");

$visits   = 0;
$vunique  = 0;
$pages    = 0;
$attack   = 0;
$htimes   = 0;
$bandwith = 0;
$sql = "SELECT `visits`,`visits_unique`,`pages` FROM `general`";
$sth = $dbh->prepare($sql);
$sth->execute();
while(@count = $sth->fetchrow_array()){
    $visits  += $count[0];
    $vunique += $count[1];
    $pages   += $count[2];
}
$sth->finish();

$sql = "SELECT `hit`,`bandwidth_hit` FROM `webagent`";
$sth = $dbh->prepare($sql);
$sth->execute();
while(@count = $sth->fetchrow_array()){
    $htimes  += $count[0];
    $bandwith += $count[1];
}
$sth->finish();

$sql = "SELECT COUNT(*) FROM `naxsilink`";
$sql = "SELECT table_name FROM information_schema.tables WHERE ".
       "table_schema = '$dbname' AND table_name LIKE 'naxsilink_%'";
$sth = $dbh->prepare($sql);
$sth->execute();
while(@count = $sth->fetchrow_array()){
    my $sql1 = "SELECT COUNT(*) FROM `$count[0]`";
    my $sth1 = $dbh->prepare($sql1);
    $sth1->execute();
    $attack += $sth1->fetchrow_array();
    $sth1->finish();
}
$sth->finish();

$sql = "SELECT COUNT(*) FROM `webvisit`";
$sth = $dbh->prepare($sql);
$sth->execute();
my $flag = $sth->fetchrow_array();
$sql = "`webvisit` SET `visits`=$visits, `visits_unique`=$vunique, `pages`=$pages, ".
       "`attack`=$attack, `hit_times`=$htimes, `bandwidth`=$bandwith;";
$sth->finish();
if($flag == 1){
    $sql = "UPDATE $sql;";
}else{
    if($flag > 1){
            warning("There are repeated rows for the 'webvisit' table of $dbname\n");
            my $delsql = "DELETE FROM `webvisit`;";
	          $rows = $dbh->do($delsql);
        }
        $sql = "INSERT INTO $sql;";
}
$rows = $dbh->do($sql);
if(!$rows){
    warning("We can't add a new rows to the 'webvisit' table ".
  	        "in the $dbname database.\n $DBI::err ($DBI::errstr)");
}

$dbh->disconnect();
