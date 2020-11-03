/***********************************************************************
 *
 *   Created on: May 4, 2016
 *   Author: Gaobo
 *
 *   Modify by Hulinfan 2016-6-7		
 ************************************************************************/

/** bd cli cmd  code goes into this file */

#include <arpa/inet.h>
#include <net/if_arp.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

#include "cli.h"
#include "cli_log.h"

#include "inifile.h"

#include <sys/types.h>
#include <sys/wait.h>

/* processing commands that are implemented in this file can be declared here */
static void process_help_cmd(char *cmd_line);
static void process_list_cmd(char *cmd_line);
static void process_logout_cmd(char *cmd_line);
static void process_passwd_cmd(char *cmd_line);
static void process_datareset_cmd(char *cmd_line);
static void process_factoryreset_cmd(char *cmd_line);
static void process_ipconfig_cmd(char *cmd_line);
static void process_ipcheck_cmd(char *cmd_line);
static void process_ipmodify_cmd(char *cmd_line);
static void process_exit_on_idle_cmd(char *cmd_line);

typedef void (*cli_cmd_fnc) (char *cmd_line);

typedef struct {
	char *cmd_name;
    char *cmd_argv; /* NULL: use system standard arguememt, "": user defined arguement*/
	char *cmd_help;
	unsigned char is_lock_needed;  /**< Framework will acquire lock before calling processing func */
	cli_cmd_fnc cli_processing_func;
} cli_cmd_item;

#define LOCK_NEEDED TRUE

#define USEPRINTF 0

char *g_sql = NULL;
MYSQL g_conn;
int g_daemon = 0;

char g_bddb_ip[64];
int g_bddb_port = 3306;
char g_bddb_user[64];
char g_bddb_password[64];
char g_bddb_name[64];
char *inifile="/home/admin/bd_cli/config.ini";
char *g_fileBuf = NULL;
int g_fileBufLen = 0;
int g_filesize = 0;
int bInitMySQL = 0;

static void trim_line_end(char *line);

int initMySQL()
{
	if( bInitMySQL == 1 )
		return 1;

	if( !mysql_init( &g_conn ) )
	{
		if( g_daemon == 0 )
			if( USEPRINTF ) printf("init mysql failed! no free memory!\n");
		return 0;
	}
	if( g_daemon == 0 )
		if( USEPRINTF ) printf("init mysql succeed!\n");

	if( !mysql_real_connect(&g_conn, g_bddb_ip, g_bddb_user, g_bddb_password, g_bddb_name, g_bddb_port, NULL, 0) )
	{
		if( g_daemon == 0 )
			if( USEPRINTF ) printf("mysql connect failed!: Error %u(%s)\n", mysql_errno(&g_conn), mysql_error(&g_conn));
		mysql_close( &g_conn );
		return 0;
	}
	if( g_daemon == 0 )
		if( USEPRINTF ) printf("mysql connect succeed!\nversion=%d\n", (int)mysql_get_server_version(&g_conn));
	mysql_set_character_set(&g_conn, "utf8");

	if( mysql_select_db(&g_conn, g_bddb_name) )
	{
		if( g_daemon == 0 )
			if( USEPRINTF ) printf("use database failed!: Error %u(%s)\n", mysql_errno(&g_conn), mysql_error(&g_conn));
		mysql_close(&g_conn);
		return 0;
	}
	if( g_daemon == 0 )
		if( USEPRINTF ) printf("use database succeed!\n");

	bInitMySQL = 1;
	return 1;
}

void uinitMySQL()
{
	if( bInitMySQL == 1 )
	{
		mysql_close( &g_conn );
		mysql_library_end();
	}
	bInitMySQL = 0;
}


int vas_bd_mysql_exec(char *sql)
{
	MYSQL mysql, *sock;

	if( !mysql_init( &mysql ) )
		return 0;

	if( !(sock = mysql_real_connect(&mysql, g_bddb_ip, g_bddb_user, g_bddb_password, g_bddb_name, g_bddb_port, NULL, 0)) )
	{
		//fprintf(stderr, "Couldn't connect to engine!\n%s\n\n", mysql_error(&mysql));
		return 0;
	}

	if( mysql_query(sock, sql) )
	{
		mysql_close( sock );
		return 0;
	}
	else
	{
		mysql_close( sock );
		return 1;
	}
}

/*
 * @cmd_argv NULL: use system default arguement, "" no arguement, "xxx" use specific argment
 * "<>" is a must and "[]" is optional
 */
static const cli_cmd_item cli_cmd_table[] = {
   { "?",              "",                                                    "List of all commands",                       0,            process_list_cmd },
   { "listcmd",        "",                                                    "List of all commands",                       0,            process_list_cmd },
   { "help",           "<command>",                                           "Show usage of a certain command",            0,            process_help_cmd },
   { "mgmtipconfig",   "<if_name> [-H <address>] [-M <mask>] [-G <gateway>]", "Configue network parameters",                0,            process_ipconfig_cmd },
   { "mgmtipcheck",    "<if_name|-a> [-A]",                                   "Check IP address" ,                          0,            process_ipcheck_cmd },
   { "mgmtipmodify",   "<if_name> [-H <address>] [-M <mask>] [-G <gateway>]", "Modify network parameters",                  0,            process_ipmodify_cmd },
   { "adminpwdreset",  "<-user user_name> <-new password>",                   "Reset Web login user's password",            0,            process_passwd_cmd },
   { "ping",           NULL,                                                  "Ping",                                       0,            NULL },
   { "traceroute",     NULL,                                                  "Traceroute",                                 0,            NULL },
   { "arp",            NULL,                                                  "Show arp table",                             0,            NULL },     
   { "route",          NULL,                                                  "Print route table",                          LOCK_NEEDED,  NULL },
//   { "datareset",      "",                                                  "Clear all working data",                     0,            process_datareset_cmd },
   { "factoryset",     "",                                                    "Do factory reset",                           0,            process_factoryreset_cmd },
   { "reboot",         NULL,                                                  "Reboot the system",                          LOCK_NEEDED,  NULL },
   { "halt",           NULL,                                                  "Shutdown the system",                        LOCK_NEEDED,  NULL },
   { "exit",           "",                                                    "Logout from CLI",                            0,            process_logout_cmd },
   { "exitOnIdle",     "",                                                    "Get/Set exit-on-idle timeout (in seconds)",  0,            process_exit_on_idle_cmd },
};

#define NUM_CLI_CMDS (sizeof(cli_cmd_table) / sizeof(cli_cmd_item))

static void show_cmd_usage(const char *cmd)
{
    int i;

    for (i = 0; i < NUM_CLI_CMDS; i++)
    {
        if (!strcasecmp(cli_cmd_table[i].cmd_name, cmd))
            break;
    }

    if (i < NUM_CLI_CMDS)
    {
        printf("%s\r\n", cli_cmd_table[i].cmd_help);

        if (cli_cmd_table[i].cmd_argv)
        {
		    printf("Usage: \r\n      %s %s\r\n", cli_cmd_table[i].cmd_name, cli_cmd_table[i].cmd_argv);
        }
        else
        {
            char cmd[256];

            snprintf(cmd, sizeof(cmd), "%s --help", cli_cmd_table[i].cmd_name);
            system(cmd);
        }
    }
    else
    {
        printf("command '%s' not found\r\n", cmd);
    }
}

static int print_cmd_exec_result(pid_t status)
{
    int ret = -1;

    if(status == -1)
	{
		fprintf(stderr, "KO\n");
	}
	else
	{
		if(WIFEXITED(status))
		{
            if (WEXITSTATUS(status))
            {
                fprintf(stderr, "KO\n");
            }
            else
            {
                fprintf(stderr, "OK\n");
                ret = 0;
            }
		}
		else
		{
			fprintf(stderr, "KO\n");
		}					
	}

    return ret;
}

unsigned char cli_process_cmd(const char *cmd_line)
{
	int found=FALSE;
	char compat_line[CLI_MAX_BUF_SZ] = {0};
	int i, cmd_name_len, compat_line_len;

	read_profile_string("database", "bddb_ip", g_bddb_ip, 64, "127.0.0.1", inifile);
	g_bddb_port = read_profile_int("database", "bddb_port", 3306, inifile);
	read_profile_string("database", "bddb_user", g_bddb_user, 64, "root", inifile);
	read_profile_string("database", "bddb_password", g_bddb_password, 64, "bd123456", inifile);
	read_profile_string("database", "bddb_name", g_bddb_name, 64, "db_firewall", inifile);
	
    strcpy(compat_line, cmd_line);

   	/*
     * Figure out the length of the command (the first word).
     */
	compat_line_len = strlen(compat_line);
	cmd_name_len = compat_line_len;
	for (i=0; i < compat_line_len; i++)
	{
		if (compat_line[i] == ' ')
		{
			cmd_name_len = i;
			break;
		}
	}

	for (i=0; i < NUM_CLI_CMDS; i++)
	{
      /*
       * Note that strcasecmp is used here, which means a command should not differ from
       * another command only in capitalization.
       */
		if ((cmd_name_len == strlen(cli_cmd_table[i].cmd_name)) &&
			(!strncasecmp(compat_line, cli_cmd_table[i].cmd_name, cmd_name_len))) {
			if (cli_cmd_table[i].is_lock_needed) 
			{
		            
			}

			if (cli_cmd_table[i].cli_processing_func != NULL)
			{
				if (compat_line_len == cmd_name_len)
				{
					/* there is no additional args, just pass in null terminator */
					(*(cli_cmd_table[i].cli_processing_func))(&(compat_line[cmd_name_len]));
				}
				else
				{
					/* pass the additional args to the processing func */
					(*(cli_cmd_table[i].cli_processing_func))(&(compat_line[cmd_name_len + 1]));
				}

			}
			else
			{
				system(compat_line);
			}

			if (cli_cmd_table[i].is_lock_needed)
			{
			
			}
		 
			found = TRUE;
			break;
		}
	}
	return found;
}

/*******************************************************************
 *
 * Command processing commands start here.
 *
 *******************************************************************
 */

void process_list_cmd(char *cmd_line __attribute((unused)))
{
	int i;

	for (i=0; i < NUM_CLI_CMDS; i++)
	{
		printf("%-16s %s\r\n", cli_cmd_table[i].cmd_name, cli_cmd_table[i].cmd_help);
	}
}

void process_help_cmd(char *cmd_line)
{
	int i;
    char *cmd;
	char *last = NULL;

	/* parse the command line and build the argument vector */
	cmd = strtok_r(cmd_line, " ", &last);
	if (cmd == NULL)
	{
        printf("Usage: help <command>\r\n");
        return;
	}

	show_cmd_usage(cmd);
}

void process_logout_cmd(char *cmd_line __attribute__((unused)))
{
	cli_keep_looping = FALSE;
	system("exit");	
}

int cmd_user_check(char *username)
{
	char sql[512];
	MYSQL_RES *res;
	MYSQL_ROW row;
	int ret = 0;
	
	if( initMySQL() == 0 )
	{	
		return 0;
	}

	sprintf(sql, "select sLoginAccount from m_tbaccount");
	if( mysql_query(&g_conn, sql) )
	{
		uinitMySQL();
		return 0;
	}

	res = mysql_store_result( &g_conn );
	while( (row = mysql_fetch_row( res )) )
	{
		char *userName = row[0];

		if( strcmp(userName, username) == 0 )
		{
			ret = 1;
			break;
		}				
	}

	mysql_free_result( res );
	uinitMySQL();

	return ret;
}

static int cli_isPasswd(const char *passwd)
{
    // weak password check
    return 1;
}

static int safe_exec(const char *cmd)
{
    char currdir[512];

    getcwd(currdir, 512);

    system(cmd);

    chdir(currdir);

    return 1;
}

/***************************************************************************
// Function Name: cmd_passwd_change
// Description  : change passwd for user
// Parameters   : userName - user.
//                      passwd - passwd
//                      msg - return error message
// Returns      : 0 - failed.
//                      1 -  success.
****************************************************************************/
int cmd_passwd_change(char *userName, char *passwd, char *msg) 
{
	char sql[512] = {'\0'}, cmd[512] = {'\0'};
    char passWord[64] = "2334";

	/*int i;
	unsigned char md[16] = {0};
	char tmp[3] = {'\0'},buf[33] = {'\0'};
	
	if (!cli_isPasswd(passwd))
    {   
      	strcpy(msg, "Invalid passwd.");
      	return 0;
    }

    strcat(passWord, passwd);

	MD5(passWord, strlen(passWord), md);
	
	for (i = 0; i < 16; i++)
	{
		sprintf(tmp, "%2.2x", md[i]);
		strcat(buf, tmp);
	}

	sprintf(cmd, "\\php /home/admin/bd_cli/mdpass.php '%s' '%s'", userName, passwd);
	system(cmd);*/

    //sprintf(cmd, "cd /Data/apps/wwwroot/firewall/apps/admin; /usr/bin/php "
    //             "/Data/apps/wwwroot/firewall/apps/admin/start loaddata getpasswd --username=\"%s\" --passwd=\"%s\"", userName, passwd);
    sprintf(cmd,  "/usr/bin/php /Data/apps/wwwroot/waf/www/yii sys-user/update-user-pwd \"%s\" \"%s\"", userName, passwd);
    safe_exec(cmd);
#if 0
	FILE *fp = fopen("/home/admin/bd_cli/passwd", "rb");
    if (!fp)
    {   
      	strcpy(msg, "No passwd file.");
        return 0;
    }

    memset(passWord, 0, sizeof(passWord));
	fgets(passWord, 64, fp);
	fclose(fp);
    
    trim_line_end(passWord);
    
	sprintf(sql, "update m_tbaccount set sPasswd='%s' where sLoginAccount='%s'", passWord, userName);
	return vas_bd_mysql_exec( sql );
#endif
    return 1;
}

void process_passwd_cmd(char *cmd_line)
{
	const int maxOpt = 4;
	signed int argc = 0;
	char *argv[maxOpt];
	char *last = NULL;
	char msg[BUFLEN_64];

	/* parse the command line and build the argument vector */
	argv[0] = strtok_r(cmd_line, " ", &last);
	if (argv[0] != NULL)
	{
		for (argc = 1; argc < maxOpt; argc++)
		{
			argv[argc] = strtok_r(NULL, " ", &last);
			if (argv[argc] == NULL)
				break;
		}
	}

	if (argc != 4 || strcmp(argv[0], "-user") || strcmp(argv[2], "-new"))
	{
		show_cmd_usage("adminpwdreset");
	}
	else if (cmd_user_check(argv[1]))
	{  
		if (cmd_passwd_change(argv[1], argv[3], msg) == 0)
		{
			fprintf(stderr, "KO\r\n");
		}
        else
        {
            fprintf(stderr, "OK\r\n");
        }
	}
	else if (strcasecmp(argv[0], "--help") == 0)
	{
		show_cmd_usage("adminpwdreset");
	}
	else 
	{
		fprintf(stderr, "KO: Invalid user '%s'\n", argv[1]);
	}
}

void process_datareset_cmd(char *cmd_line)
{
    char input;
	char cmd[256];

    printf("Are you sure you want to clear all working data ?(y/n) ");

    scanf("%c", &input);
    if (input != 'y' && input != 'Y')
        return;

    printf("Please wait...\n");

    /* copy original log to database */
	sprintf(cmd, "\\cp -rf  /var/log/mysql/default-data/db_firewall_log/* /var/log/mysql/data/db_firewall_log/");
	system(cmd);

    /* copy original data to database */
	sprintf(cmd, "\\cp -rf  /usr/local/mysql/default-data/db_firewall/* /usr/local/mysql/data/db_firewall/");
	pid_t status = system(cmd);
    print_cmd_exec_result(status);
}

void process_factoryreset_cmd(char *cmd_line)
{	
    char input;
	char cmd[256];

    printf("Are you sure you want to do factory reset?(y/n) ");

    scanf("%c", &input);
    if (input != 'y' && input != 'Y')
        return;

    /* Also reset all working data */
    //process_datareset(cmd_line);

	sprintf(cmd, "\\python /usr/local/bluedon/core/second_firewall_reset.py firewall");
    pid_t status = system(cmd);
    print_cmd_exec_result(status);
}

char *cmd_get_ipaddr(char *eth)
{
	FILE *fp;
	char cmd[128], buf[1024];
	char *pLine;
	char *ipaddr = NULL;

	//sprintf(cmd, "ifconfig %s|grep inet| sed -n '1p'|awk '{print $2}'|awk -F ':' '{print $2}'", eth);
	sprintf(cmd, "ifconfig %s|grep inet| sed -n '1p'|awk '{print $2}'", eth);
	fp = popen(cmd, "r");
    if (!fp)
        return NULL;

	if( fgets(buf, sizeof(buf), fp) != NULL )
	{
		ipaddr = strdup( buf );
	}
	
	pclose( fp );
	return ipaddr;
}

char *cmd_get_mask(char *eth)
{
	FILE *fp;
	char cmd[128], buf[1024];
	char *pLine;
	char *mask = NULL;

	//sprintf(cmd, "ifconfig %s|grep inet| sed -n '1p'|awk '{print $4}'|awk -F ':' '{print $2}'", eth);
	sprintf(cmd, "ifconfig %s|grep inet| sed -n '1p'|awk '{print $4}'", eth);
	fp = popen(cmd, "r");
    if (!fp)
        return NULL;

	if( fgets(buf, sizeof(buf), fp) != NULL )
	{
		mask = strdup( buf );
	}
	
	pclose( fp );
	return mask;
}

char *cmd_get_gateway()
{
    FILE *fp;
	char cmd[128], buf[1024];
	char *gw = NULL;

	sprintf(cmd, "route | grep default | sed -n '1p'|awk '{print $2}'");
	fp = popen(cmd, "r");
    if (!fp)
        return NULL;

	if(fgets(buf, sizeof(buf), fp) != NULL)
	{
		gw = strdup(buf);
	}
	
	pclose(fp);
	return gw;
}

int cmd_get_eth_status(char *eth)
{
	FILE *fp;
	char cmd[128], buf[1024];
	char *pLine;

	sprintf(cmd, "ifconfig %s | grep 'UP'", eth);
	fp = popen(cmd, "r");
	if( fgets(buf, sizeof(buf), fp) != NULL )
	{
		if( strstr(buf, "UP"))
		{
			pclose( fp );
			return 1;
		}
	}
	
	pclose( fp );
	return 0;
}

static void trim_line_end(char *line)
{
    size_t n;

    if (!line)
        return;

    n = strlen(line);

    while ((n-- > 0) && (line[n] == '\r' || line[n] == '\n'))
    {
        line[n] = '\0';
    }
}

static int calc_ip_bits(const char *ip)
{
    int ret;
    struct in_addr s;
    int i, netmask_bits = 0;

    ret = inet_pton(AF_INET, ip, (void *)&s);

    for (i = 0; i < 32; i++)
    {
        if ((s.s_addr >> i) & 0x01)
            netmask_bits++;
    }

    return  netmask_bits;
}

int cmd_set_ifeth(char *eth)
{
	char sql[512];
	MYSQL_RES *res;
	MYSQL_ROW row;
	int ret = 0;
	int ifstatus;

	char *ipbuf = cmd_get_ipaddr( eth );
	char *mkbuf = cmd_get_mask( eth );
	int ifon = cmd_get_eth_status( eth );

    trim_line_end(ipbuf);
    trim_line_end(mkbuf);

	if(ifon)
	{
		ifstatus = 1;
	}
	else
	{
		ifstatus = 0;
	}
	
	if( initMySQL() == 0 )
	{	
		goto err0;
	}

	sprintf(sql, "SELECT id FROM m_tbnetport WHERE sPortName='%s'", eth);
	
	if( mysql_query(&g_conn, sql) )
	{
		goto err1;
	}
	
	res = mysql_store_result( &g_conn );
	if(! (row = mysql_fetch_row( res )) )
	{
		sprintf(sql, "INSERT INTO m_tbnetport (sIPV4Address,sPortName,iStatus) VALUES ('%s/%d','%s','%d')", ipbuf, calc_ip_bits(mkbuf), eth, ifstatus);
	}
	else
	{
		sprintf(sql, "Update m_tbnetport set sIPV4Address='%s/%d', iStatus='%d' WHERE sPortName='%s'", ipbuf, calc_ip_bits(mkbuf), ifstatus, eth);
	}
	
	if (mysql_query(&g_conn, sql))
    {
        printf("failed to update netport table\n");
    }
	
	mysql_free_result( res );
    ret = 1;

err1:
	uinitMySQL();
err0:
    if (ipbuf)
        free(ipbuf);
    if (mkbuf)
        free(mkbuf);

	return ret;
}

static int ip_modify_flag = 0;

void process_ipconfig_cmd(char *cmd_line)
{
    int i, offset;
	const int maxOpt = 7;
	signed int argc = 0;
	char *argv[maxOpt];
    char *ipaddr = NULL, *netmask = NULL, *gateway = NULL;
	char *last = NULL;
    char cmdstr_line[CLI_MAX_BUF_SZ] = {0};
    int modify = ip_modify_flag;

    ip_modify_flag = 0;

    for (argc = 0; argc < maxOpt; argc++)
        argv[argc] = NULL;

	/* parse the command line and build the argument vector */
	argv[0] = strtok_r(cmd_line, " ", &last);
	if (argv[0] == NULL || !strcmp(argv[0], "--help"))
    {
        show_cmd_usage(modify ? "mgmtipmodify" : "mgmtipconfig");
        return;
    }
	
    for (argc = 1; argc < maxOpt; argc++)
	{
	    argv[argc] = strtok_r(NULL, " ", &last);
		if (argv[argc] == NULL)
		    break;
	}
	
    for (i = 1; i < argc; i++)
    {
        if (!strcmp(argv[i], "-H") || !strcmp(argv[i], "-h"))
        {
            if ((i + 1) >= argc)
            {
                printf("Missing arguement for -H\r\n");
                return;
            }

            ipaddr = argv[++i];
            if (!cli_isIpAddress(ipaddr))
            {
                printf("Invalid IP address: %s\r\n", ipaddr);
                return;
            }

            continue;
        }
        else if (!strcmp(argv[i], "-M") || !strcmp(argv[i], "-m"))
        {
            if ((i + 1) >= argc)
            {
                printf("Missing arguement for -M\r\n");
                return;
            }

            netmask = argv[++i];
            if (!cli_isIpAddress(netmask))
            {
                printf("Invalid netmask: %s\r\n", netmask);
                return;
            }

            continue;
        }
        else if (!strcmp(argv[i], "-G") || !strcmp(argv[i], "-g"))
        {
            if ((i + 1) >= argc)
            {
                printf("Missing arguement for -G\r\n");
                return;
            }

            gateway = argv[++i];
            if (!cli_isIpAddress(gateway))
            {
                printf("Invalid gateway: %s\r\n", gateway);
                return;
            }

            continue;
        }
        else
        {
            show_cmd_usage(modify ? "mgmtipmodify" : "mgmtipconfig");
            return;
        }
    }

    /* arguement 0 must be an interface name */
    sprintf(cmdstr_line, "ifconfig %s ", argv[0]);
    offset = strlen(cmdstr_line);

    if (ipaddr)
    {
        sprintf(cmdstr_line + offset, "%s " , ipaddr);
        offset = strlen(cmdstr_line);
    }
    if (netmask)
    {
        sprintf(cmdstr_line + offset, "netmask %s " , netmask);
        offset = strlen(cmdstr_line);
    }

    pid_t status = system(cmdstr_line); 

    if (gateway)
    {
        sprintf(cmdstr_line, "route | grep default");
        FILE *fp = popen(cmdstr_line, "r");
        if (fp) /* cmd succeeds */
        {
            char buf[2];
            if(fgets(buf, sizeof(buf), fp) != NULL)
            {
                system("route del default");
            }

            sprintf(cmdstr_line, "route add default gw %s " , gateway);
            status = system(cmdstr_line);

            pclose(fp);
        }
    }
	
	if(argv[1] != NULL)
	{
	    if (cmd_set_ifeth(argv[0]))
		    fprintf(stderr, "OK\n");
        else
		    fprintf(stderr, "KO: Cannot write to database\n");
	}
    else
    {
        print_cmd_exec_result(status);
    }
}

void process_ipcheck_cmd(char *cmd_line)
{
    char cmd[256];
    const int maxOpt = 2;
	signed int argc = 0;
	char *argv[maxOpt];
	char *last = NULL;

    for (argc = 0; argc < maxOpt; argc++)
        argv[argc] = NULL;

	/* parse the command line and build the argument vector */
	argv[0] = strtok_r(cmd_line, " ", &last);
	if (argv[0] == NULL || !strcmp(argv[0], "--help"))
    {
        show_cmd_usage("mgmtipcheck");
        return;
    }
	
    for (argc = 1; argc < maxOpt; argc++)
	{
	    argv[argc] = strtok_r(NULL, " ", &last);
		if (argv[argc] == NULL)
		    break;
	}

    if (!strcmp(argv[0], "-a"))
    {
        snprintf(cmd, sizeof(cmd), "ifconfig %s", argv[0]);
        system(cmd);
    }
    else /* arguement 0 must be an interface name */
    {
        char *ipbuf = cmd_get_ipaddr(argv[0]);
        char *netmask = cmd_get_mask(argv[0]);
        char *gw = cmd_get_gateway();

        if (argv[1] && (!strcmp(argv[1], "-A") || !strcmp(argv[1], "-a")))
        {
            printf("Information of %s:\n IP address: %s netmask: %s gateway: %s\n", argv[0], 
                    ipbuf ? ipbuf : "",
                    netmask ? netmask : "",
                    gw ? gw : "");
        }
        else if (!argv[1])
        {
            printf("Information of %s:\n IP address: %s\n", argv[0], ipbuf ? ipbuf : "");
        }
        else
        {
            show_cmd_usage("mgmtipcheck");
        }

        if (ipbuf)
            free(ipbuf);
        if (netmask)
            free(netmask);
        if (gw)
            free(gw);
    }
}

void process_ipmodify_cmd(char *cmd_line)
{
    ip_modify_flag = 1;
    process_ipconfig_cmd(cmd_line);
}

void process_exit_on_idle_cmd(char *cmd_line)
{
	if (!strncasecmp(cmd_line, "get", 3))
	{
		printf("current timout is %d seconds\n", exit_on_timeout);
	}
	else if (!strncasecmp(cmd_line, "set", 3))
	{
		exit_on_timeout = atoi(&(cmd_line[4]));
		printf("timeout is set to %d seconds (for this session only, not saved to config)\n", exit_on_timeout);
	}
	else
	{
		printf("usage: exitOnIdle get\n");
		printf("       exitOnIdle set <seconds>\n\n");
	}
}

