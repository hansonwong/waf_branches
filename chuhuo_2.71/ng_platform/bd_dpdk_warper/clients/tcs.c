#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <getopt.h>
#include <dpdk_warp.h>
#include <sys/msg.h>
#include <pthread.h>
#include <sys/wait.h>
#include <sys/shm.h>

#include "dpdk_frame.h"

#define TC_DEBUG 1

#ifdef TC_DEBUG
#define TRACE_TC(fmt,args...) do {\
		printf(fmt,##args);          \
} while(0)
#else
#define TRACE_TC(fmt,args...) do {} while(0)
#endif

#define TC_CMD "/sbin/tc"
#define IPTABLES_CMD "/usr/sbin/iptables"
#define IPTABLES_CHAIN "TC_RULES_CHAIN"
#define TABLES "mangle"
#define TC_VIR_NIC "ifb0"
#define IPTABLE_ETH_RULE 1

#define POINT_OUTDEV 1   //up link point outdev  you should use "tcs -O vEth0" to point outdev 

#define QUANTUM 1        //define quantum yourself
#ifdef QUANTUM 
#define TC_QUANTUM "quantum 3000"
#define TC_VIRLINE_QUANTUM "quantum 3000"
#else 
#define TC_QUANTUM ""
#define TC_VIRLINE_QUANTUM ""
#endif

#define TC_FW_MASK_TYPE 1   //when exec tc fw filter,if use fw mark/mask  

#define VALID_PROTOCOL 256
static char * proto_idx_name[VALID_PROTOCOL][2]=
{
	{"ALL","0"},
	{"FTP_CONTROL","1"},
	{"POP3","2"},
	{"SMTP","3"},
	{"IMAP","4"},
	{"DNS","5"},
	{"IPP","6"},
	{"HTTP","7"},
	{"MDNS","8"},
	{"NTP","9"},
	{"NetBIOS","10"},
	{"NFS","11"},
	{"SSDP","12"},
	{"BGP","13"},
	{"SNMP","14"},
	{"XDMCP","15"},
	{"SMB","16"},
	{"Syslog","17"},
	{"DHCP","18"},
	{"PostgreSQL","19"},
	{"MySQL","20"},
	{"TDS","21"},
	{"Direct_Download_Link","22"},
	{"POPS","23"},
	{"AppleJuice","24"},
	{"DirectConnect","25"},
	{"Socrates","26"},
	{"WinMX","27"},
	{"VMware","28"},
	{"SMTPS","29"},
	{"Filetopia","30"},
	{"iMESH","31"},
	{"Kontiki","32"},
	{"OpenFT","33"},
	{"FastTrack","34"},
	{"Gnutella","35"},
	{"eDonkey","36"},
	{"BitTorrent","37"},
	{"EPP","38"},
	{"AVI","39"},
	{"Flash","40"},
	{"OggVorbis","41"},
	{"MPEG","42"},
	{"QuickTime","43"},
	{"RealMedia","44"},
	{"WindowsMedia","45"},
	{"MMS","46"},
	{"Xbox","47"},
	{"QQ","48"},
	{"Move","49"},
	{"RTSP","50"},
	{"IMAPS","51"},
	{"IceCast","52"},
	{"PPLive","53"},
	{"PPStream","54"},
	{"Zattoo","55"},
	{"ShoutCast","56"},
	{"Sopcast","57"},
	{"Tvants","58"},
	{"TVUplayer","59"},
	{"HTTP_APPLICATION_VEOHTV","60"},
	{"QQLive","61"},
	{"Thunder","62"},
	{"Soulseek","63"},
	{"SSL_No_Cert","64"},
	{"IRC","65"},
	{"Ayiya","66"},
	{"Unencryped_Jabber","67"},
	{"MSN","68"},
	{"Oscar","69"},
	{"Yahoo","70"},
	{"BattleField","71"},
	{"Quake","72"},
	{"VRRP","73"},
	{"Steam","74"},
	{"HalfLife2","75"},
	{"WorldOfWarcraft","76"},
	{"Telnet","77"},
	{"STUN","78"},
	{"IPsec","79"},
	{"GRE","80"},
	{"ICMP","81"},
	{"IGMP","82"},
	{"EGP","83"},
	{"SCTP","84"},
	{"OSPF","85"},
	{"IP_in_IP","86"},
	{"RTP","87"},
	{"RDP","88"},
	{"VNC","89"},
	{"PcAnywhere","90"},
	{"SSL","91"},
	{"SSH","92"},
	{"Usenet","93"},
	{"MGCP","94"},
	{"IAX","95"},
	{"TFTP","96"},
	{"AFP","97"},
	{"Stealthnet","98"},
	{"Aimini","99"},
	{"SIP","100"},
	{"TruPhone","101"},
	{"ICMPV6","102"},
	{"DHCPV6","103"},
	{"Armagetron","104"},
	{"Crossfire","105"},
	{"Dofus","106"},
	{"Fiesta","107"},
	{"Florensia","108"},
	{"Guildwars","109"},
	{"HTTP_Application_ActiveSync","110"},
	{"Kerberos","111"},
	{"LDAP","112"},
	{"MapleStory","113"},
	{"MsSQL","114"},
	{"PPTP","115"},
	{"Warcraft3","116"},
	{"WorldOfKungFu","117"},
	{"Meebo","118"},
	{"Facebook","119"},
	{"Twitter","120"},
	{"DropBox","121"},
	{"GMail","122"},
	{"GoogleMaps","123"},
	{"YouTube","124"},
	{"Skype","125"},
	{"Google","126"},
	{"DCE_RPC","127"},
	{"NetFlow","128"},
	{"sFlow","129"},
	{"HTTP_Connect","130"},
	{"HTTP_Proxy","131"},
	{"Citrix","132"},
	{"NetFlix","133"},
	{"LastFM","134"},
	{"Waze","135"},
	{"SkyFile_PrePaid","136"},
	{"SkyFile_Rudics","137"},
	{"SkyFile_PostPaid","138"},
	{"Citrix_Online","139"},
	{"Apple","140"},
	{"Webex","141"},
	{"WhatsApp","142"},
	{"AppleiCloud","143"},
	{"Viber","144"},
	{"AppleiTunes","145"},
	{"Radius","146"},
	{"WindowsUpdate","147"},
	{"TeamViewer","148"},
	{"Tuenti","149"},
	{"LotusNotes","150"},
	{"SAP","151"},
	{"GTP","152"},
	{"UPnP","153"},
	{"LLMNR","154"},
	{"RemoteScan","155"},
	{"Spotify","156"},
	{"WebM","157"},
	{"H323","158"},
	{"OpenVPN","159"},
	{"NOE","160"},
	{"CiscoVPN","161"},
	{"TeamSpeak","162"},
	{"Tor","163"},
	{"CiscoSkinny","164"},
	{"RTCP","165"},
	{"RSYNC","166"},
	{"Oracle","167"},
	{"Corba","168"},
	{"UbuntuONE","169"},
	{"Whois-DAS","170"},
	{"Collectd","171"},
	{"SOCKS5","172"},
	{"SOCKS4","173"},
	{"RTMP","174"},
	{"FTP_DATA","175"},
	{"Wikipedia","176"},
	{"ZeroMQ","177"},
	{"Amazon","178"},
	{"eBay","179"},
	{"CNN","180"},
	{"Megaco","181"},
	{"Redis","182"},
	{"Pando_Media_Booster","183"},
	{"VHUA","184"},
	{"Telegram","185"},
	{"Vevo","186"},
	{"Pandora","187"},
	{"Quic","188"},
	{"WhatsAppVoice","189"},
	{"EAQ","190"},
	{"TIM_Meu","191"},
	{"Torcedor","192"},
	{"KakaoTalk","193"},
	{"KakaoTalk_Voice","194"},
	{"Twitch","195"},
	{"QuickPlay","196"},
	{"TIM","197"},
	{"Mpegts","198"},
	{"Snapchat","199"},
	{"Simet","200"},
	{"OpenSignal","201"},
	{"99Taxi","202"},
	{"EasyTaxi","203"},
	{"GloboTV","204"},
	{"SomDeChamada","205"},
	{"TIM_Menu","206"},
	{"TIM_PortasAbertas","207"},
	{"TIM_Recarga","208"},
	{"TIM_Beta","209"},
	{"Deezer","210"},
	{"Instagram","211"},
	{"Microsoft","212"},
	{"Stracraft","213"},
	{"Teredo","214"},
	{NULL,NULL}
};

enum TC_Link{
	TC_UP_LINK = 0,
	TC_DN_LINK,
	TC_MAX_LINK,
};


enum TC_IP_TYPE{
	IP_MASK  = 0,
	IP_RANGE,
	IP_SET,
	IP_MAX,
};

#define MAX_TC_VIRLINE 256
#define MAX_TC_SPORT   2048   //mark high 12bit, index 1-2047,so 2048-1
#define MAX_TC_ADDR    4096

#define MARK_ALL_MASK  0xfff00000
#define MARK_APP_MASK  0xfff00fff
#define MARK_SHIFT 20

#define MAX_HANDLE_POS 16
#define MAX_TC_CMD_STR 256

#define TC_SUBPORT_FUN_FORBID 1

#define IPQUAD(addr) \
((unsigned char *)&addr)[3], \
((unsigned char *)&addr)[2], \
((unsigned char *)&addr)[1], \
((unsigned char *)&addr)[0]

#define	ARRAY_REMOVE(headlist, elm, field, buff) do {	 \
	if((headlist)->head == (headlist)->tail){        \
		(headlist)->head = -1;                   \
		(headlist)->tail = -1;                   \
	}else if((elm)->field.pret == -1){       \
		(headlist)->head = (elm)->field.next;    \
		(buff)[(elm)->field.next].field.pret = -1;   \
	}else if((elm)->field.next == -1){       \
		(headlist)->tail = (elm)->field.pret;    \
		(buff)[(elm)->field.pret].field.next = -1;   \
	}else{                                   \
		(buff)[(elm)->field.pret].field.next = (elm)->field.next; \
		(buff)[(elm)->field.next].field.pret = (elm)->field.pret; \
	}                                        \
} while(0)

#define ARRAY_INSERT_TAIL(headlist, elm, field, buff) do { \
	(elm)->field.next = -1;    \
	(elm)->field.pret = -1;    \
	if((headlist)->head == -1){   \
		(headlist)->head = (elm)->field.index;  \
		(headlist)->tail = (elm)->field.index;  \
	}else{ \
		buff[(headlist)->tail].field.next = (elm)->field.index; \
		(elm)->field.next = -1; \
		(elm)->field.pret = (headlist)->tail; \
		(headlist)->tail  = (elm)->field.index; \
	}\
} while(0)

#define ARRAY_FOREACH(var, headlist, field, buff)   \
		for ((var) = (headlist)->head;				\
			 (var) != -1;							\
			 (var) = ((buff)[(var)].field.next))

#define ARRAY_FOREACH_BACK(var, headlist, field, buff) \
		for ((var) = (headlist)->tail;				   \
			 (var) != -1;							   \
			 (var) = ((buff)[(var)].field.pret))




#define ERROR_STR_SIZE  128

#define MAX_IP_GROUP    256
#define MAX_STRING_SIZE 32

#define display_bw(a,b) display_bw_1000(a,b)

#define kbps 125
#define mbps 125000
#define gbps 125000000

//protocol bitmap
#define TC_PROTOCOL_SHIFT 0x0000000000000001UL
#define TC_PROTOCOL_MAX   0xFFFFFFFFFFFFFFFFUL
#define TC_PROTOCOL_TOTAL 256  // PROTOCOL_NUMS * PROTOCOL_BITS
#define TC_PROTOCOL_NUMS  4
#define TC_PROTOCOL_BITS  64

#define MAX_IPSET_NAME  64
#define MAX_NAME_STRING 32
#define MAX_FILE_PATH   256
#define MAX_ETHPORTS  RTE_MAX_ETHPORTS

/*new add 5 lines*/
#define ALL_APP    0
#define FIRST_APP  1
#define SECOND_APP 2
#define THIRD_APP  3
static uint32_t mark_mask[4]={0xfff00000,0xffff0000,0xffffff00,0xffffffff};

typedef struct __TcCtlParam{
	uint32_t cmdvalue;
	uint16_t iptype;      /*0. one ip or ip mask   1. ip1 - ip2  2. ipset*/
	uint16_t addr_nums;                /*one ip or ip mask*/
	uint64_t ip_addr[MAX_IP_GROUP];
	uint32_t iprange[2];               /*ip1 - ip2*/
	char ipset[MAX_IPSET_NAME];        /*ipset*/
	uint64_t protomask[TC_PROTOCOL_NUMS];
	/*new add appid*/
    uint32_t appid;
	uint32_t rate[TC_MAX_LINK];
	uint32_t ceil[TC_MAX_LINK];
	uint32_t sceil[TC_MAX_LINK];
	uint32_t vir_rate[TC_MAX_LINK];
	uint32_t virid;
	uint32_t sportid;
	uint32_t priority;
	uint16_t portid;
	uint16_t outportid;
	char eth[MAX_NAME_STRING];
	char outeth[MAX_NAME_STRING];
	char configfile[MAX_FILE_PATH];
}TcCtlParam;

typedef struct __ArrayList{
	int head;
	int tail;
}ArrayList;

typedef struct __ArrayNode{
	int next;
	int pret;
	int index;
}ArrayNode;

typedef struct __TcSport{
	uint32_t sportid;       //user id
	uint32_t prior;         //used priority
	uint16_t priority;      //inner priority
	uint16_t iptype;
	uint32_t iprange[2];
	uint16_t type;          //shared single
	uint16_t forbid;
	uint16_t handleid;
	uint16_t shandleid;
	uint16_t used;
	uint32_t surebw[TC_MAX_LINK];
	uint32_t ceilbw[TC_MAX_LINK];
	uint32_t sigebw[TC_MAX_LINK];
	int virindex;
	int addr_nums;
	uint64_t protomask[TC_PROTOCOL_NUMS];  //PROTOCOL_NUMS * 64 protocols
	/*new add appid apptype*/
	uint32_t appid;
    uint32_t apptype;
	char ipset[MAX_IPSET_NAME];
	ArrayList userlist;
	ArrayNode virsportchain;
	ArrayNode sportchain;
}TcSport;

typedef struct __TcVirline{
	uint32_t virid;           //user vir id
	uint32_t totalbw[TC_MAX_LINK];
	uint32_t usedbw[TC_MAX_LINK];
	uint16_t inportid;        /**in physical port id*/
	uint16_t outportid;       /**out physical port id*/
	uint16_t handleid;        //tc id
	uint16_t used;
	ArrayList virsport;
	ArrayNode virchain;
}TcVirline;

typedef struct __TcPort{
	short    enable;                        /**if port tc is enable or disable*/
	short    ifcfg;                         /**down link if config*/                       
	short    qdisccfg;                      /**if port have config qdisc*/
	short    inuse;                         /**if nic is inuse*/
	int      mode;                          /**port mode<from dpdk port mode>*/
	int      value;                         /**port value<from dpdk port mode>*/
	int      upvirline_ref;                 /**up link virline nums*/
	uint16_t portid;                        /**physical port id*/
	uint16_t handleid;                      /**physical port tc handle id*/ 
	char eth[MAX_NAME_STRING];              /**physical port name*/
	uint32_t linkspeed[TC_MAX_LINK];        /**port link speed kbps*/
	uint32_t usedspeed[TC_MAX_LINK];        /**port used speed kbps*/
	ArrayList  virlinelist;                 /**virtual line list*/
	ArrayList  sportlist;					/**port sport list*/
}TcPort;

typedef struct __TcAddr{
	uint64_t  addr;
	ArrayNode addrchain;
	int used;
}TcAddr;

typedef struct __TcConfig{
	int tcswitch;
	int tcpons;
	
	TcPort     tcp[MAX_ETHPORTS];
	TcVirline  virline[MAX_TC_VIRLINE];
	TcSport    sport[MAX_TC_SPORT];
	TcAddr     addr[MAX_TC_ADDR];
}TcConfig;

struct tc_ctl{
	const  char         * program_name;
	struct system_info  * sysinfo;
	TcConfig * stc;
	TcCtlParam cmdtc;
	pid_t  pidid;
	int    shmid;
	int    newflag;
};

static struct tc_ctl gTc = {0};

const char tcs_short_options[] ="T:I:A:D:U:S:L:ERP:O:u:e:d:p:r:c:ts:g:o:q:b:f:l:v:h";

const struct option tcs_long_options[]=
{
	{.name = "qos switch",    .has_arg = 1, .val = 'T'},
	{.name = "enable/disable",.has_arg = 1, .val = 'I'},
	{.name = "add",        	  .has_arg = 1, .val = 'A'},
	{.name = "delete",        .has_arg = 1, .val = 'D'},
	{.name = "update",        .has_arg = 1, .val = 'U'},
	{.name = "shift",         .has_arg = 1, .val = 'S'},
	{.name = "list",          .has_arg = 1, .val = 'L'},
	{.name = "list_port_used",.has_arg = 1, .val = 'E'},
	{.name = "reset_data",    .has_arg = 1, .val = 'R'},
	{.name = "print_realrate",.has_arg = 1, .val = 'P'},
	{.name = "point outdev",  .has_arg = 1, .val = 'O'},
	{.name = "user/ip_addr",  .has_arg = 1, .val = 'u'},
	{.name = "user/ipset",    .has_arg = 1, .val = 'e'},
	{.name = "user/iprange",  .has_arg = 1, .val = 'd'},
	{.name = "protocol",      .has_arg = 1, .val = 'p'}, 
	{.name = "assure_rate",   .has_arg = 1, .val = 'r'},
	{.name = "ceil_rate",     .has_arg = 1, .val = 'c'},
	{.name = "stop_singleip", .has_arg = 1, .val = 't'},
	{.name = "start_singleip",.has_arg = 1, .val = 's'},
	{.name = "traffic id",    .has_arg = 1, .val = 'g'},
	{.name = "priority",      .has_arg = 1, .val = 'o'},
	{.name = "queue_size",    .has_arg = 1, .val = 'q'},
	{.name = "bucket_size",   .has_arg = 1, .val = 'b'},
	{.name = "configfile",    .has_arg = 1, .val = 'f'},
	{.name = "line_road",     .has_arg = 1, .val = 'l'},
	{.name = "line_road_rate",.has_arg = 1, .val = 'v'},
	{.name = "help",          .has_arg = 1, .val = 'h'},
	{NULL},
};


#define TC_CMD_NONE				0x00000000U
#define TC_CMD_ENABLE			0x00000001U
#define TC_CMD_DISABLE			0x00000002U
#define TC_CMD_ADD				0x00000004U
#define TC_CMD_DELETE			0x00000008U
#define TC_CMD_UPDATE			0x00000010U
#define TC_CMD_SHIFT        	0x00000020U
#define TC_CMD_LIST				0x00000040U
#define TC_CMD_PORT_USED		0x00000080U
#define TC_CMD_RESET            0x00000100U
#define TC_CMD_PRINT            0x00000200U
#define TC_CMD_SWITCHON			0x00000400U
#define TC_CMD_SWITCHOFF		0x00000800U
#define TC_NUMBER_OF_CMD		13

#define TC_VALUE_USE        	0x00000001U
#define TC_VALUE_PROTOCOL   	0x00000002U
#define TC_VALUE_RATE       	0x00000004U
#define TC_VALUE_CEIL       	0x00000008U
#define TC_VALUE_TCID      	    0x00000010U
#define TC_VALUE_PRIOR  	    0x00000020U
#define TC_VALUE_QSIZE      	0x00000040U
#define TC_VALUE_BUCKETSIZE 	0x00000080U
#define TC_VALUE_SUBPORT_UP     0x00000100U
#define TC_VALUE_SUBPORT_DOWN   0x00000200U
#define TC_VALUE_SINGLE_UP      0x00000400U
#define TC_VALUE_SINGLE_DOWN    0x00000800U
#define TC_VALUE_FILE           0x00001000U
#define TC_VALUE_VIRLINE        0x00002000U
#define TC_VALUE_VIRLINE_RATE   0x00004000U
#define TC_VALUE_OUTDEV         0x00008000U


static const char cmdflags[] = {'T','T','I','I','A','D','U','S','L','E','R','P'};

static void exit_printhelp()
{
	const char * proname = gTc.program_name;
	
	printf("HOW TO USE %s\n"
		   "Usage: %s -[T] on/off traffic control main switch\n"
		   "       %s -[I] enable/disable nic eg:%s -I vEth0 UP\n"
           "       %s -[A] add nic virtual line/traffic channel\n"
		   "               eg:%s -A vEth0 -l 1 -v 1000/1000\n"
		   "                  %s -A vEth0 -l 1 -p tcp -u 192.168.1.100 -c 100/100 -r 50/50 -s 50/50 -g 1\n"
		   "       %s -[D] delete nic virtual line/traffic channel\n"
		   "               eg:%s -D vEth0 -l 1 [notice:it will delete all TCs of VL 1]\n"
		   "				  %s -D vEth0 -g 1\n"
		   "       %s -[U] update nic traffic channel\n"
		   "               eg:%s -U vEth0 -g 1 -[crs] 100/20 \n"
		   "				  %s -U vEth0 -g 1 -t\n"
		   "				  %s -U vEth0 -g 1 -s 100/50\n"
		   "				  %s -U vEth0 [UP/DOWN] -g 1\n"
 		   "       %s -[S] update traffic channel prior\n"
		   "               eg:%s -S vEth0 -g 1 -o 2\n"
	       "       %s -[L] list nic virtual line/traffic channel info\n"
		   "               eg:%s -L vEth0 -l 1\n"
		   "                  %s -L vEth0 -g 1\n"
	       "       %s -[P] print nic virtual line/traffic channel rate\n"
		   "               eg:%s -P vEth0 -l 1\n"
		   "                  %s -P vEth0 -g 1\n"
	       "       %s -[R] reset data\n"
	       "       %s -[E] show nic state\n",
	       proname,proname,proname,
	       proname,proname,proname,
	       proname,proname,proname,
	       proname,proname,proname,proname,
	       proname,proname,proname,
	       proname,proname,proname,
	       proname,proname,proname,
	       proname,proname,proname);
	
	printf(
		   "options:\n"
		   "  --outdev      -O vEth1 \n"
	 	   "  --user        -u 192.168.1.100/24 \n"
	 	   "  --protocol    -p tcp:udp or -p 6:17 [reference dpi mark]\n"
	 	   "  --ceil   rate -c [down_link/up_link] default unit kbps,[kbps,mbps,gbps]\n"
		   "  --assure rate -r [down_link/up_link] default unit kbps,[kbps,mbps,gbps]\n"
		   "  --single rate -r [down_link/up_link] default unit kbps,[kbps,mbps,gbps]\n"
		   "  --vl rate     -v [down_link/up_link] default unit kbps,[kbps,mbps,gbps]\n"
		   "  --priority    -o\n"
		   "  --down single -t\n"
		   "  --TC uniqueid -g\n"
		   "  --VL uniqueid -l\n"
		   "  --queue size  -q\n"
		   "  --bucket size -b\n"
		   "  --config file -f\n"
		   "  --help        -h\n");
	exit(0);
}

static unsigned trim(char *str, unsigned len)
{
	int newlen = len;
	if (len == 0)
		return 0;

	if (isspace(str[len-1])) {
		/* strip trailing whitespace */
		while (newlen > 0 && isspace(str[newlen - 1]))
			str[--newlen] = '\0';
	}

	if (isspace(str[0])) {
		/* strip leading whitespace */
		int i,start = 1;
		while (isspace(str[start]) && start < newlen)
			start++
			; /* do nothing */
		newlen -= start;
		for (i = 0; i < newlen; i++)
			str[i] = str[i+start];
		str[i] = '\0';
	}
	return newlen;
}

static int strsplit(char *string, int stringlen,char **tokens, int maxtokens, char delim)
{
	int i, tok   = 0;
	int tokstart = 1; /* first token is right at start of string */

	if (string == NULL || tokens == NULL)
		return -1;

	for (i = 0; i < stringlen; i++) {
		if (string[i] == '\0' || tok >= maxtokens)
			break;
		if (tokstart) {
			tokstart = 0;
			tokens[tok++] = &string[i];
		}
		if (string[i] == delim) {
			string[i] = '\0';
			tokstart = 1;
		}
	}
	return tok;
}

static char *display_bw_1000(uint64_t bw, const char *unit)
{
	static char buf[20];

	if (bw >= (uint64_t)(1000000000))
		snprintf(buf, sizeof(buf), "%.2lf %s%s", (double)bw/1000000000, "G", unit);
	else if (bw >= (uint64_t)(1000000))
		snprintf(buf, sizeof(buf), "%.2lf %s%s", (double)bw/1000000, "M", unit);
	else if (bw >= (uint64_t)(1000))
		snprintf(buf, sizeof(buf), "%.2lf %s%s", (double)bw/1000, "K", unit);
	else
		snprintf(buf, sizeof(buf), "%.2lf %s%s", (double)bw, "", unit);

	return buf;
}

static char *display_bw_1024(uint64_t bw, const char *unit)
{
	static char buf[20];

	if (bw >= (uint64_t)(2 << 30))
		snprintf(buf, sizeof(buf), "%lu %s%s", bw >> 30, "G", unit);
	else if (bw >= (uint64_t)(2 << 20))
		snprintf(buf, sizeof(buf), "%lu %s%s", bw >> 20, "M", unit);
	else if (bw >= (uint64_t)(2 << 10))
		snprintf(buf, sizeof(buf), "%lu %s%s", bw >> 10, "K", unit);
	else
		snprintf(buf, sizeof(buf), "%lu %s%s", bw, "", unit);

	return buf;
}

static char *display_rate(uint64_t rate, const char *unit)
{
	uint64_t bw = rate;

	return display_bw(bw, unit);
}


static void TcPrintSport(TcConfig * tc,TcSport * sport)
{
	if (sport == NULL) return;
	printf("ID:%u(%s)\n",sport->priority,(sport->forbid ? "DOWN" : "UP"));
	printf("Subport ID:%u,Virtual Line ID:%u,priority:%u,inner index:%d,next:%d,pret:%d\n",
		    sport->sportid,
		    tc->virline[sport->virindex].virid,
		    sport->prior,
		    sport->sportchain.index,
		    sport->sportchain.next,
		    sport->sportchain.pret);
	printf("[uplink]assure rate:%s\n",display_rate(((uint64_t)sport->surebw[TC_UP_LINK])*1000,"b/s"));
	printf("        ceil rate  :%s\n",display_rate(((uint64_t)sport->ceilbw[TC_UP_LINK])*1000,"b/s"));
	printf("        single ip limit:%s%s\n",sport->type ? "enable,rate:":"disable",
		                                    sport->type ? display_rate(((uint64_t)sport->sigebw[TC_UP_LINK])*1000,"b/s"):"");
	printf("[downlink]assure rate:%s\n",display_rate(((uint64_t)sport->surebw[TC_DN_LINK])*1000,"b/s"));
	printf("        ceil rate  :%s\n",display_rate(((uint64_t)sport->ceilbw[TC_DN_LINK])*1000,"b/s"));
	printf("        single ip limit:%s%s\n",sport->type ? "enable,rate:":"disable",
		                                    sport->type ? display_rate(((uint64_t)sport->sigebw[TC_DN_LINK])*1000,"b/s"):"");

}


static void TcPrintOnlyVirline(TcVirline * vir)
{
	if(vir == NULL) return;
	printf("************************************************************************\n");
	printf("Virtual Line ID:%u Inner ID:%d\n",vir->virid,vir->virchain.index);
	printf("Virtual line UP-Link   total rate:%s",display_rate(((uint64_t)vir->totalbw[TC_UP_LINK])*1000,"b/s"));
	printf(",used rate:%s\n",display_rate(((uint64_t)vir->usedbw[TC_UP_LINK])*1000,"b/s"));
	
	printf("Virtual line DOWN-Link total rate:%s",display_rate(((uint64_t)vir->totalbw[TC_DN_LINK])*1000,"b/s"));
	printf(",used rate:%s\n",display_rate(((uint64_t)vir->usedbw[TC_DN_LINK])*1000,"b/s"));

}

static void TcPrintVirline(TcConfig * tc,TcVirline * vir)
{
	if(vir == NULL) return;
	TcPrintOnlyVirline(vir);
	int pos;
	ARRAY_FOREACH(pos,&vir->virsport,virsportchain,tc->sport){
		TcPrintSport(tc,&tc->sport[pos]);
	}
}

static char cmd2char(int option)
{
	const char *ptr;
	for (ptr = cmdflags; option > 1; option >>= 1, ptr++);

	return *ptr;
}

static void add_command(unsigned int *cmd, const int newcmd, const int othercmds)
{
	if (*cmd & (~othercmds)){
		printf("Cannot use -%c with -%c\n",
			   cmd2char(newcmd), cmd2char(*cmd & (~othercmds)));
		exit(-1);
	}
	*cmd |= newcmd;
}

static int proto2id(char * protoname,uint16_t * protoid)
{

	int index;
	for ( index = 0; index < VALID_PROTOCOL-1 && 
		             proto_idx_name[index][0]!=NULL; index++ )
	{
		if(strcasecmp(protoname,proto_idx_name[index][0])==0 ||
		   strcasecmp(protoname,proto_idx_name[index][1])==0)
		{
			*protoid = index;
			return 0;
		}	
	}
	printf("protocol %s does not identify!\n",protoname);
	return -1;
}

static int TcProtoParse(char * proto,uint64_t * protomask)
{
	int ret;
	char * str = proto;
	char * p;
	int index;
	uint16_t protoid;
	while((p=strsep(&str,":"))!=NULL){
		ret = proto2id(p,&protoid);
		if (ret==0){
			if (protoid==0){
				for (index=0;index<TC_PROTOCOL_NUMS;index++){
					protomask[index] |= TC_PROTOCOL_MAX;
				}
				break;
			}
			protomask[protoid/TC_PROTOCOL_BITS] |= 
				TC_PROTOCOL_SHIFT << (protoid%TC_PROTOCOL_BITS);
		}
	}
	return 0;
}

static int TcAddrParse(const char *ipadrmsk,TcCtlParam * tp)
{
	char buf[2][16];
	uint32_t ip,mask;
	int32_t  masklen;
	int shift;
	
	int res = sscanf(ipadrmsk,"%[^/]/%[0-9]",buf[0],buf[1]);
	if (res<1){
		goto err_value;
	}
	ip = inet_network/*inet_addr*/(buf[0]);
	if(res==1)
		masklen=32;
	else {
		masklen=atoi(buf[1]);
		if(masklen==-1 || masklen>32)
			goto err_value;
	}
	mask = 0;
	for (shift = 0; shift < masklen; shift++){
		 mask |= 0x80000000>>shift;
	}
	
	if(ip==0xffffffff || ((ip & mask) !=ip)){
		goto err_value;
	}
	uint64_t ipaddr = ip; 
	tp->ip_addr[tp->addr_nums] = (uint64_t)((ipaddr << 32) | mask);
	tp->addr_nums++;
	return 0;
err_value:
	printf("Error:[%s] ipaddr or mask format invalid!Please input -u xxx.xxx.xxx.xxx/xx\n",ipadrmsk);
	return -1;
}


static int TcAddrRangeParse(const char *iprange,TcCtlParam * tp)
{
	char buf[2][16];
	uint32_t ip1,ip2,ip;

	int res = sscanf(iprange,"%[^-]-%[.0-9]",buf[0],buf[1]);
	if (res != 2){
		goto err_value;
	}
	ip1 = inet_network/*inet_addr*/(buf[0]);
	ip2 = inet_network/*inet_addr*/(buf[1]);
	if(ip1 > ip2){
		ip  = ip1;
		ip1 = ip2;
		ip2 = ip;
	}
	tp->iprange[0] = ip1;
	tp->iprange[1] = ip2;
	return 0;
err_value:
	printf("Error:[%s] ip rangle format invalid!Please input -d xxx.xxx.xxx.xxx-xxx.xxx.xxx.xxx\n",iprange);
	return -1;
}

static int TcRateParse(const char *ratestr,int unit,uint32_t * rate)
{
	char buf[2][16];
	int downrate,uprate;
	if (strlen(ratestr)>32){
		goto err_value;
	}
	
	int res = sscanf(ratestr,"%[0-9]/%[0-9]",buf[0],buf[1]);
	if (res!=2){
		goto err_value;
	}

	downrate = atoi(buf[0]);
	if( downrate < 0 ){
		goto err_value;
	}
	uprate =atoi(buf[1]);
	if( uprate < 0 ){
		goto err_value;
	}
	rate[TC_DN_LINK] = (uint32_t)(downrate*unit / kbps);
	rate[TC_UP_LINK] = (uint32_t)(uprate*unit   / kbps);

	return 0;
err_value:
	printf("rate format error,should down_rate/up_rate!\n");
	return -1;
}

static int TcGetUnit(const char * unit,int * pr)
{
	int value;
		
	if (unit==NULL){
		*pr = kbps;
		return 0;
	}

	if (strcasecmp(unit,"kbps")==0){
		value = kbps;
	}
	
	else if (strcasecmp(unit,"mbps")==0){
		value = mbps;
	}
	else if (strcasecmp(unit,"gbps")==0){
		value = gbps;
	}
	else {
		printf("Unable to identify the unit %s\n",unit);
		printf("Please input Kbps/Mbps/Gbps,default Kbps\n");
		return -1;
	}
	*pr = value;
	return 0;
}

static int TcPortLook(TcConfig * tc,const char * eth)
{
	int index = 0;
	while ( index < MAX_ETHPORTS ){
		if(strcmp(tc->tcp[index].eth,eth) == 0){
			return tc->tcp[index].portid;
		}
		index++;
	}
	TRACE_TC("NIC:%s does not exist! please input correct NIC!\n",eth);
	return -1;
}

static int TcParseFile(const char * filename,TcCtlParam * tp,uint32_t nums)
{
	char buffer[256];
	int lineno = 0;
	uint32_t index   = 0;
	uint32_t entries = 0;

	FILE *file = fopen(filename, "r");
	if (file == NULL){
		printf("%s can not be open",filename);
		return -1;
	}
	
	while (fgets(buffer, sizeof(buffer), file) != NULL && entries <= nums){
		
		char *pos = NULL;
		size_t len = strnlen(buffer, sizeof(buffer));
		lineno++;
		if (len >=sizeof(buffer) - 1 && buffer[len-1] != '\n'){
			printf("Error line %d - no \\n found on string. "
					"Check if line too long\n", lineno);
			goto error;
		}
		if ((pos = memchr(buffer, ';', sizeof(buffer))) != NULL) {
			*pos = '\0';
			len = pos -  buffer;
		}

		len = trim(buffer, len);
		if (buffer[0] != '[' && memchr(buffer, '=', len) == NULL)
			continue;
		
		if (buffer[0] == '[') {
			index = entries;
			entries++;
			
			/* section heading line */
			char *end = memchr(buffer, ']', len);
			if (end == NULL) {
				printf("Error line %d - no terminating '[' found\n", lineno);
				goto error;
			}
			*end = '\0';
			trim(&buffer[1], end - &buffer[1]);
			char * bsplit[2];
			char   bname[MAX_STRING_SIZE];
			char  bvalue[MAX_STRING_SIZE];
			if (strsplit(&buffer[1], sizeof(buffer), bsplit, 2, '=') != 2) {
				printf("Error at line %d - cannot split string\n", lineno);
				goto error;
			}
			snprintf(bname, sizeof(bname), "%s", bsplit[0]);
			snprintf(bvalue,sizeof(bvalue),"%s", bsplit[1]);
			trim(bname, strnlen(bname, sizeof(bname)));
			trim(bvalue,strnlen(bvalue,sizeof(bvalue)));
			if(strncmp(bname,"subport",sizeof(bname)) == 0){
				tp[index].sportid= (uint32_t)atoi(bvalue);
				tp[index].cmdvalue |= TC_VALUE_TCID;
			}
		}
		else {	
			char * split[2];
			char   name[MAX_STRING_SIZE];
			char  value[MAX_STRING_SIZE];
			if (strsplit(buffer, sizeof(buffer), split, 2, '=') != 2) {
				printf("Error at line %d - cannot split string\n", lineno);
				goto error;
			}
			snprintf(name, sizeof(name), "%s", split[0]);
			snprintf(value,sizeof(value),"%s", split[1]);
			trim(name, strnlen(name, sizeof(name)));
			trim(value,strnlen(value,sizeof(value)));
			
			if(strncmp(name,"user",sizeof(name)) == 0 && !(tp[index].cmdvalue & TC_VALUE_USE)){
				if(0 != TcAddrParse(value,&tp[index])){
					printf("Error at line %d - cannot parse addr string %s\n", lineno,value);
					goto error;
				}
				tp[index].cmdvalue |= TC_VALUE_USE;
				tp[index].iptype = IP_MASK;
			}
			if(strncmp(name,"userset",sizeof(name)) == 0 && !(tp[index].cmdvalue & TC_VALUE_USE)){
				strncpy(tp[index].ipset,value,MAX_IPSET_NAME-1);
				tp[index].cmdvalue |= TC_VALUE_USE;
				tp[index].iptype = IP_SET;
			}
			if(strncmp(name,"userrange",sizeof(name)) == 0 && !(tp[index].cmdvalue & TC_VALUE_USE)){
				if(0 != TcAddrRangeParse(value,&tp[index])){
					printf("Error at line %d - cannot parse addr rangle string %s\n", lineno,value);
					goto error;
				}
				tp[index].cmdvalue |= TC_VALUE_USE;
				tp[index].iptype = IP_RANGE;
			}
			if(strncmp(name,"protocol",sizeof(name)) == 0){
                /*
				if(0 != TcProtoParse(value,tp[index].protomask)){
					printf("Error at line %d - cannot parse protocal string %s\n", lineno,value);
					goto error;
				}
				*/
				/*new add 1 lines*/
				tp[index].appid = (uint32_t)atoi(value);
				tp[index].cmdvalue |= TC_VALUE_PROTOCOL;
			}
			if(strncmp(name,"ceil",sizeof(name)) == 0){
				if(0 != TcRateParse(value,kbps,tp[index].ceil)){
					printf("Error at line %d - formal error,cannot parse ceil string %s\n",lineno,value);
					goto error;
				}
				tp[index].cmdvalue |= TC_VALUE_CEIL;
			}
			if(strncmp(name,"rate",sizeof(name)) == 0){
				if(0 != TcRateParse(value,kbps,tp[index].rate)){
					printf("Error at line %d - formal error,cannot parse rate string %s\n",lineno,value);
					goto error;
				}
				tp[index].cmdvalue |= TC_VALUE_RATE;
			}
			if(strncmp(name,"single ceil",sizeof(name)) == 0){
				if(0 != TcRateParse(value,kbps,tp[index].sceil)){
					printf("Error at line %d - formal error,cannot parse single ip rate string %s\n",lineno,value);
					goto error;
				}
				tp[index].cmdvalue |= TC_VALUE_SINGLE_UP;
			}
			if(strncmp(name,"virtual line",sizeof(name)) == 0){
				tp[index].virid = (uint32_t)atoi(value);
				tp[index].cmdvalue |= TC_VALUE_VIRLINE;
			}
			if(strncmp(name,"priority",sizeof(name)) == 0){
				tp[index].priority = (uint32_t)atoi(value);
				tp[index].cmdvalue |= TC_VALUE_PRIOR;
			}
		}
	}
	fclose(file);
	return 0;
error:
	fclose(file);
	return -1;
}

static int TcCheckCmdline(TcCtlParam * tp)
{
	if(!(tp->cmdvalue & TC_VALUE_VIRLINE)){
		printf("Don't appoint -l(virtual line id)\n");
		return -1;
	}
	
	if(!(tp->cmdvalue & TC_VALUE_USE) || !(tp->cmdvalue & TC_VALUE_PROTOCOL)){
		printf("Don't have user or protocol!Please use options -u and -p\n");
		return -1;
	}

	if(!(tp->cmdvalue & TC_VALUE_CEIL) && !(tp->cmdvalue & TC_VALUE_RATE)){
		printf("Don't have assure rate or burst rate!Please use options -c or -r\n");
		return -1;		
	}

	if(!(tp->cmdvalue & TC_VALUE_TCID)){
		printf("Don't appoint -g(traffic channel id)\n");
		return -1;
	}
	return 0;
}

static int TcExecCmd(const char * cmdstr)
{
	pid_t status = system(cmdstr);
    if (-1 == status){
		return -1;
    }  
    else  
    {
    	if (WIFEXITED(status)){
			if (0 == WEXITSTATUS(status)){
                return 0; 
            }  
            else{  
                TRACE_TC("Exec tc fail,exit code: %d\n",cmdstr,WEXITSTATUS(status));
				return -1;
            }
        }
	}
	return 0;
}


static int TcExecCmdAndPrint(const char * cmdstr)
{
	if(TcExecCmd(cmdstr) < 0){
		TRACE_TC("FAIL: %s\n",cmdstr);
	}
	else TRACE_TC("OK  : %s\n",cmdstr);
	return 0;
}

static int TcExecAddIptables(TcConfig* tc,TcSport * sport,uint16_t portid)
{
	char cmdstr[MAX_TC_CMD_STR];
	char chainname[MAX_TC_CMD_STR];
	char chainroot[MAX_TC_CMD_STR];
	sprintf(chainname,"%s_%d_%d",IPTABLES_CHAIN,portid,sport->sportchain.index);
	sprintf(chainroot,"%s_%d",IPTABLES_CHAIN,portid);
	sprintf(cmdstr,"%s -t %s -N %s",IPTABLES_CMD,TABLES,chainname);
	TcExecCmdAndPrint(cmdstr);
	sprintf(cmdstr,"%s -t %s -I %s %d -j %s",IPTABLES_CMD,TABLES,chainroot,sport->priority+1,chainname);
	TcExecCmdAndPrint(cmdstr);
	uint32_t upmark,downmark;
	uint16_t outportid;
#if POINT_OUTDEV==1
	upmark   = (uint32_t)(sport->sportchain.index + 1) << MARK_SHIFT;
	downmark = upmark;
#else
	upmark   = (uint32_t)(sport->sportchain.index * 2 + 2) << MARK_SHIFT;
	downmark = (uint32_t)(sport->sportchain.index * 2 + 1) << MARK_SHIFT;	
#endif

	char outeth[MAX_TC_CMD_STR];
	char ineth[MAX_TC_CMD_STR];
	memset(outeth,0,sizeof(outeth));
	memset(ineth,0,sizeof(ineth));
	
#ifdef IPTABLE_ETH_RULE
	outportid = tc->virline[sport->virindex].outportid;
	if(tc->tcp[portid].mode == BRIDGE_SIMPLE){
		sprintf(outeth,"-m physdev --physdev-out %s -m physdev --physdev-in %s",tc->tcp[portid].eth,tc->tcp[outportid].eth);
		sprintf(ineth, "-m physdev --physdev-in %s -m physdev --physdev-out %s",tc->tcp[portid].eth,tc->tcp[outportid].eth);
	}
	else{
		sprintf(outeth,"-o %s -i %s",tc->tcp[portid].eth,tc->tcp[outportid].eth);
		sprintf(ineth, "-i %s -o %s",tc->tcp[portid].eth,tc->tcp[outportid].eth);
	}
#endif

	if(sport->iptype == IP_MASK){
		int pos;
		ARRAY_FOREACH(pos,&sport->userlist,addrchain,tc->addr){
			uint32_t ip   = (uint32_t)(tc->addr[pos].addr >> 32 & 0xffffffff);
	    	uint32_t mask = (uint32_t)(tc->addr[pos].addr & 0xffffffff); 
			sprintf(cmdstr,"%s -t %s -A %s %s -d %u.%u.%u.%u/%u.%u.%u.%u -m mark --mark 0x0/0x%x -j MARK --or-mark %u",
					        IPTABLES_CMD,TABLES,chainname,outeth,IPQUAD(ip),IPQUAD(mask),MARK_ALL_MASK,downmark);
			TcExecCmdAndPrint(cmdstr);
			sprintf(cmdstr,"%s -t %s -A %s %s -s %u.%u.%u.%u/%u.%u.%u.%u -m mark --mark 0x0/0x%x -j MARK --or-mark %u",
					        IPTABLES_CMD,TABLES,chainname,ineth,IPQUAD(ip),IPQUAD(mask),MARK_ALL_MASK,upmark);
			TcExecCmdAndPrint(cmdstr);
		}		
	}
	else if(sport->iptype == IP_RANGE){
		sprintf(cmdstr,"%s -t %s -A %s %s -m iprange --dst-range %u.%u.%u.%u-%u.%u.%u.%u -m mark --mark 0x0/0x%x -j MARK --or-mark %u",
						IPTABLES_CMD,TABLES,chainname,outeth,IPQUAD(sport->iprange[0]),IPQUAD(sport->iprange[1]),MARK_ALL_MASK,downmark);
		TcExecCmdAndPrint(cmdstr);
		sprintf(cmdstr,"%s -t %s -A %s %s -m iprange --src-range %u.%u.%u.%u-%u.%u.%u.%u -m mark --mark 0x0/0x%x -j MARK --or-mark %u",
						IPTABLES_CMD,TABLES,chainname,ineth,IPQUAD(sport->iprange[0]),IPQUAD(sport->iprange[1]),MARK_ALL_MASK,upmark);
		TcExecCmdAndPrint(cmdstr);
	}
	else if(sport->iptype == IP_SET){
		sprintf(cmdstr,"%s -t %s -A %s %s -m set --set %s dst -m mark --mark 0x0/0x%x -j MARK --or-mark %u",
					    IPTABLES_CMD,TABLES,chainname,outeth,sport->ipset,MARK_ALL_MASK,downmark);
		TcExecCmdAndPrint(cmdstr);
		sprintf(cmdstr,"%s -t %s -A %s %s -m set --set %s src -m mark --mark 0x0/0x%x -j MARK --or-mark %u",
					    IPTABLES_CMD,TABLES,chainname,ineth,sport->ipset,MARK_ALL_MASK,upmark);
		TcExecCmdAndPrint(cmdstr);
	}

	return 0;
}

static int TcExecUpdIptables(TcConfig* tc,TcSport * sport,uint16_t portid)
{
	char cmdstr[MAX_TC_CMD_STR];
	char chainname[MAX_TC_CMD_STR];
	char chainroot[MAX_TC_CMD_STR];
	sprintf(chainname,"%s_%d_%d",IPTABLES_CHAIN,portid,sport->sportchain.index);
	sprintf(chainroot,"%s_%d",IPTABLES_CHAIN,portid);
	sprintf(cmdstr,"%s -t %s -D %s -j %s",IPTABLES_CMD,TABLES,chainroot,chainname);
	TcExecCmdAndPrint(cmdstr);
	sprintf(cmdstr,"%s -t %s -I %s %d -j %s",IPTABLES_CMD,TABLES,chainroot,sport->priority,chainname);
	TcExecCmdAndPrint(cmdstr);
	return 0;
}

static int TcExecDelIptables(TcConfig* tc,TcSport * sport,uint16_t portid)
{
	char cmdstr[MAX_TC_CMD_STR];
	char chainname[MAX_TC_CMD_STR];
	char chainroot[MAX_TC_CMD_STR];
	sprintf(chainname,"%s_%d_%d",IPTABLES_CHAIN,portid,sport->sportchain.index);
	sprintf(chainroot,"%s_%d",IPTABLES_CHAIN,portid);
	sprintf(cmdstr,"%s -t %s -D %s -j %s",IPTABLES_CMD,TABLES,chainroot,chainname);
	TcExecCmdAndPrint(cmdstr);
	sprintf(cmdstr,"%s -t %s -F %s",IPTABLES_CMD,TABLES,chainname);
	TcExecCmdAndPrint(cmdstr);
	sprintf(cmdstr,"%s -t %s -X %s",IPTABLES_CMD,TABLES,chainname);
	TcExecCmdAndPrint(cmdstr);
	return 0;
}

/*new add func*/
static int TcGetAppType(uint32_t appid)
{
    int type;
    type = appid & 0xff;
    if(type != 0)
        return THIRD_APP;
    
    appid = appid >> 8;
    type = appid & 0xff;
    if(type != 0)
        return SECOND_APP;
    appid = appid >> 8;
    if(appid != 0)
        return FIRST_APP;
    return ALL_APP;
}

static int TcIfAllProto(uint64_t * protomask)
{
	int index = 0;
	while(index < TC_PROTOCOL_NUMS){
		if(protomask[index] != TC_PROTOCOL_MAX){
			return 0;
		}
		index++;
	}
	return 1;
}

static int TcExecAddFilter(TcConfig* tc,TcSport * sport,uint16_t portid)
{
	uint32_t i,mark;
#if POINT_OUTDEV==1
	mark = (uint32_t)(sport->sportchain.index + 1) << MARK_SHIFT;
#else
	//down link
	mark = (uint32_t)(sport->sportchain.index * 2 + 1) << MARK_SHIFT;
#endif
	uint32_t flowid = sport->type ? sport->shandleid : sport->handleid;
	char cmdstr[MAX_TC_CMD_STR];
    /*
	if(TcIfAllProto(sport->protomask) == 0){
		for( i = 0; i < PROTOCOL_TOTAL; i++){
			if((sport->protomask[i/TC_PROTOCOL_BITS] & (TC_PROTOCOL_SHIFT << (i%TC_PROTOCOL_BITS))) == 0)
				continue;
			if(i == 0) continue;
			sprintf(cmdstr,"%s filter add dev %s parent %u:0 protocol ip prio %u handle 0x%x/0x%x fw flowid %u:%u",
						    TC_CMD,tc->tcp[portid].eth,tc->tcp[portid].handleid,
						    sport->sportchain.index+1,(mark|i),MARK_APP_MASK,tc->tcp[portid].handleid,flowid);
			TcExecCmdAndPrint(cmdstr);
		}
	}
	else {
#if TC_FW_MASK_TYPE==1
		sprintf(cmdstr,"%s filter add dev %s parent %u:0 protocol ip prio %u handle 0x%x/0x%x fw flowid %u:%u",
					    TC_CMD,tc->tcp[portid].eth,tc->tcp[portid].handleid,
						sport->sportchain.index+1,mark,MARK_ALL_MASK,tc->tcp[portid].handleid,flowid);
		TcExecCmdAndPrint(cmdstr);
#else		
		for( i = 0; i < VALID_PROTOCOL; i++){
			sprintf(cmdstr,"%s filter add dev %s parent %u:0 protocol ip prio %u handle 0x%x/0x%x fw flowid %u:%u",
						    TC_CMD,tc->tcp[portid].eth,tc->tcp[portid].handleid,
						    sport->sportchain.index+1,(mark|i),MARK_APP_MASK,tc->tcp[portid].handleid,flowid);
			TcExecCmdAndPrint(cmdstr);
		}
#endif
	}
	*/
	/*new add 4 lines*/
    sprintf(cmdstr,"%s filter add dev %s parent %u:0 protocol ip prio %u handle 0x%x/0x%x fw flowid %u:%u",
					TC_CMD,tc->tcp[portid].eth,tc->tcp[portid].handleid,
					sport->sportchain.index+1,(mark|sport->appid),mark_mask[sport->apptype],tc->tcp[portid].handleid,flowid);
	TcExecCmdAndPrint(cmdstr);
	return 0;
}
static int TcExecDelFilter(TcConfig* tc,TcSport * sport,uint16_t portid)
{

	char cmdstr[MAX_TC_CMD_STR];
	sprintf(cmdstr,"%s filter del dev %s parent %u:0 protocol ip prio %u",
					TC_CMD,tc->tcp[portid].eth,tc->tcp[portid].handleid,
					sport->sportchain.index+1);
	TcExecCmdAndPrint(cmdstr);
	
	return 0;
}

#if POINT_OUTDEV==1
static int TcExecAddUpSport(TcConfig * tc,TcSport * sport,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0 || sport->forbid == 1) return 0;
	
	char cmdstr[MAX_TC_CMD_STR];
	uint32_t ratebw,ceilbw;
	uint16_t outportid = tc->virline[sport->virindex].outportid;
	
	ratebw = sport->surebw[TC_UP_LINK]!=0 ? sport->surebw[TC_UP_LINK] : sport->ceilbw[TC_UP_LINK];
	ceilbw = sport->ceilbw[TC_UP_LINK]!=0 ? sport->ceilbw[TC_UP_LINK] : sport->surebw[TC_UP_LINK];
	sprintf(cmdstr,"%s class add dev %s parent %u:0 classid %u:%u htb rate %uKbit ceil %uKbit %s",
					TC_CMD,tc->tcp[outportid].eth,tc->tcp[outportid].handleid,
					tc->tcp[outportid].handleid,sport->handleid,ratebw,ceilbw,TC_QUANTUM);
	TcExecCmdAndPrint(cmdstr);

	if(sport->type == 1){
		sprintf(cmdstr,"%s class add dev %s parent %u:%u classid %u:%u htb rate %uKbit ceil %uKbit %s",
					    TC_CMD,tc->tcp[outportid].eth,tc->tcp[outportid].handleid,sport->handleid,
					    tc->tcp[outportid].handleid,sport->shandleid,
					    sport->sigebw[TC_UP_LINK],sport->sigebw[TC_UP_LINK],TC_QUANTUM);
		TcExecCmdAndPrint(cmdstr);
	}
	TcExecAddFilter(tc,sport,outportid);
	return 0;
}

static int TcExecDelUpSport(TcConfig * tc,TcSport * sport,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0 || sport->forbid == 1) return 0;
	
	char cmdstr[MAX_TC_CMD_STR];
	uint32_t ratebw,ceilbw;
	uint16_t outportid = tc->virline[sport->virindex].outportid;

	TcExecDelFilter(tc,sport,outportid);
	
	if(sport->type == 1){
		sprintf(cmdstr,"%s class del dev %s parent %u:%u classid %u:%u htb rate %uKbit ceil %uKbit %s",
					    TC_CMD,tc->tcp[outportid].eth,tc->tcp[outportid].handleid,sport->handleid,
					    tc->tcp[outportid].handleid,sport->shandleid,
					    sport->sigebw[TC_UP_LINK],sport->sigebw[TC_UP_LINK],TC_QUANTUM);
		TcExecCmdAndPrint(cmdstr);
	}
	ratebw = sport->surebw[TC_UP_LINK]!=0 ? sport->surebw[TC_UP_LINK] : sport->ceilbw[TC_UP_LINK];
	ceilbw = sport->ceilbw[TC_UP_LINK]!=0 ? sport->ceilbw[TC_UP_LINK] : sport->surebw[TC_UP_LINK];
	sprintf(cmdstr,"%s class del dev %s parent %u:0 classid %u:%u htb rate %uKbit ceil %uKbit %s",
					TC_CMD,tc->tcp[outportid].eth,tc->tcp[outportid].handleid,
					tc->tcp[outportid].handleid,sport->handleid,ratebw,ceilbw,TC_QUANTUM);
	TcExecCmdAndPrint(cmdstr);
	
	return 0;
}

#else
static int TcExecAddUpSport(TcConfig * tc,TcSport * sport,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0 || sport->forbid == 1) return 0;
	
	int allproto = TcIfAllProto(sport->protomask);
	char cmdstr[MAX_TC_CMD_STR];
	uint32_t i,mark,flowid,ratebw,ceilbw;

	ratebw = sport->surebw[TC_UP_LINK]!=0 ? sport->surebw[TC_UP_LINK] : sport->ceilbw[TC_UP_LINK];
	ceilbw = sport->ceilbw[TC_UP_LINK]!=0 ? sport->ceilbw[TC_UP_LINK] : sport->surebw[TC_UP_LINK];
	sprintf(cmdstr,"%s class add dev %s parent 1:0 classid 1:%u htb rate %uKbit ceil %uKbit %s",
					TC_CMD,TC_VIR_NIC,sport->handleid,ratebw,ceilbw,TC_QUANTUM);
	TcExecCmdAndPrint(cmdstr);

	if(sport->type == 1){
		sprintf(cmdstr,"%s class add dev %s parent 1:%u classid 1:%u htb rate %uKbit ceil %uKbit %s",
					    TC_CMD,TC_VIR_NIC,sport->handleid,sport->shandleid,
					    sport->sigebw[TC_UP_LINK],sport->sigebw[TC_UP_LINK],TC_QUANTUM);
		TcExecCmdAndPrint(cmdstr);
	}
	//up link
	mark = (uint32_t)(sport->sportchain.index * 2 + 2) << MARK_SHIFT;
	flowid = sport->type ? sport->shandleid : sport->handleid;
    /*
	if(allproto == 0){
		for( i = 0; i < VALID_PROTOCOL; i++){
			if((sport->protomask[i/TC_PROTOCOL_BITS] & (TC_PROTOCOL_SHIFT << (i%TC_PROTOCOL_BITS))) == 0)
					continue;
			if(i == 0) continue;
			sprintf(cmdstr,"%s filter add dev %s parent 1:0 protocol ip prio %u handle 0x%x/0x%x fw flowid 1:%u",
						    TC_CMD,TC_VIR_NIC,sport->sportchain.index+1,(mark|i),MARK_APP_MASK,flowid);
			TcExecCmdAndPrint(cmdstr);
		}
	}
	else {
#if TC_FW_MASK_TYPE==1
		sprintf(cmdstr,"%s filter add dev %s parent 1:0 protocol ip prio %u handle 0x%x/0x%x fw flowid 1:%u",
						TC_CMD,TC_VIR_NIC,sport->sportchain.index+1,mark,MARK_ALL_MASK,flowid);
		TcExecCmdAndPrint(cmdstr);
#else		
		for( i = 0; i < VALID_PROTOCOL; i++){
			sprintf(cmdstr,"%s filter add dev %s parent 1:0 protocol ip prio %u handle 0x%x/0x%x fw flowid 1:%u",
							TC_CMD,TC_VIR_NIC,sport->sportchain.index+1,(mark|i),MARK_APP_MASK,flowid);
			TcExecCmdAndPrint(cmdstr);
		}
#endif
	}
	*/
	/*new add 3 lines*/
	sprintf(cmdstr,"%s filter add dev %s parent 1:0 protocol ip prio %u handle 0x%x/0x%x fw flowid 1:%u",
				    TC_CMD,TC_VIR_NIC,sport->sportchain.index+1,(mark|sport->appid),mark_mask[sport->apptype],flowid);
	TcExecCmdAndPrint(cmdstr);
	return 0;
}

static int TcExecDelUpSport(TcConfig * tc,TcSport * sport,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0 || sport->forbid == 1) return 0;
	
	char cmdstr[MAX_TC_CMD_STR];
	uint32_t ratebw,ceilbw;

	sprintf(cmdstr,"%s filter del dev %s parent 1:0 protocol ip prio %u",
					TC_CMD,TC_VIR_NIC,sport->sportchain.index+1);
	TcExecCmdAndPrint(cmdstr);

	if(sport->type == 1){
		sprintf(cmdstr,"%s class del dev %s parent 1:%u classid 1:%u htb rate %uKbit ceil %uKbit %s",
					    TC_CMD,TC_VIR_NIC,sport->handleid,sport->shandleid,
					    sport->sigebw[TC_UP_LINK],sport->sigebw[TC_UP_LINK],TC_QUANTUM);
		TcExecCmdAndPrint(cmdstr);
	}
	ratebw = sport->surebw[TC_UP_LINK]!=0 ? sport->surebw[TC_UP_LINK] : sport->ceilbw[TC_UP_LINK];
	ceilbw = sport->ceilbw[TC_UP_LINK]!=0 ? sport->ceilbw[TC_UP_LINK] : sport->surebw[TC_UP_LINK];
	sprintf(cmdstr,"%s class del dev %s parent 1:0 classid 1:%u htb rate %uKbit ceil %uKbit %s",
						TC_CMD,TC_VIR_NIC,sport->handleid,ratebw,ceilbw,TC_QUANTUM);
	TcExecCmdAndPrint(cmdstr);
	
	return 0;
}

#endif
static int TcExecAddSport(TcConfig* tc,TcSport * sport,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0 || sport->forbid == 1) return 0;

	TcExecAddIptables(tc,sport,portid);
	char cmdstr[MAX_TC_CMD_STR];
	uint32_t ratebw = sport->surebw[TC_DN_LINK]!=0 ? sport->surebw[TC_DN_LINK] : sport->ceilbw[TC_DN_LINK];
	uint32_t ceilbw = sport->ceilbw[TC_DN_LINK]!=0 ? sport->ceilbw[TC_DN_LINK] : sport->surebw[TC_DN_LINK];
	sprintf(cmdstr,"%s class add dev %s parent %u:%u classid %u:%u htb rate %uKbit ceil %uKbit prio %u %s",
					TC_CMD,tc->tcp[portid].eth,
					tc->tcp[portid].handleid,tc->virline[sport->virindex].handleid,
					tc->tcp[portid].handleid,sport->handleid,
					ratebw,ceilbw,sport->priority,TC_QUANTUM);
	TcExecCmdAndPrint(cmdstr);
	
	if(sport->type == 1){
		sprintf(cmdstr,"%s class add dev %s parent %u:%u classid %u:%u htb rate %uKbit ceil %uKbit %s",
					    TC_CMD,tc->tcp[portid].eth,
					    tc->tcp[portid].handleid,sport->handleid,
					    tc->tcp[portid].handleid,sport->shandleid,
					    sport->sigebw[TC_DN_LINK],sport->sigebw[TC_DN_LINK],TC_QUANTUM);
		TcExecCmdAndPrint(cmdstr);
	}
	TcExecAddFilter(tc,sport,portid);
	TcExecAddUpSport(tc,sport,portid);
	return 0;
}
static int TcExecDelSport(TcConfig* tc,TcSport * sport,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0 || sport->forbid == 1) return 0;

	TcExecDelIptables(tc,sport,portid);
	
	char cmdstr[MAX_TC_CMD_STR];

	TcExecDelFilter(tc,sport,portid);
	if(sport->type == 1){
		sprintf(cmdstr,"%s class del dev %s parent %u:%u classid %u:%u htb rate %uKbit ceil %uKbit %s",
					    TC_CMD,tc->tcp[portid].eth,
					    tc->tcp[portid].handleid,sport->handleid,
					    tc->tcp[portid].handleid,sport->shandleid,
					    sport->sigebw[TC_DN_LINK],sport->sigebw[TC_DN_LINK],TC_QUANTUM);
		TcExecCmdAndPrint(cmdstr);
	}
	uint32_t ratebw = sport->surebw[TC_DN_LINK]!=0 ? sport->surebw[TC_DN_LINK] : sport->ceilbw[TC_DN_LINK];
	uint32_t ceilbw = sport->ceilbw[TC_DN_LINK]!=0 ? sport->ceilbw[TC_DN_LINK] : sport->surebw[TC_DN_LINK];
	sprintf(cmdstr,"%s class del dev %s parent %u:%u classid %u:%u htb rate %uKbit ceil %uKbit prio %u %s",
			        TC_CMD,tc->tcp[portid].eth,
			        tc->tcp[portid].handleid,tc->virline[sport->virindex].handleid,
			        tc->tcp[portid].handleid,sport->handleid,
			        ratebw,ceilbw,sport->priority,TC_QUANTUM);
	TcExecCmdAndPrint(cmdstr);
	TcExecDelUpSport(tc,sport,portid);
	return 0;
}

static int TcExecAddUpVirine(TcConfig* tc,TcVirline * vir,uint16_t outportid)
{
	if(tc->tcswitch == 0) return 0;

	char cmdstr[MAX_TC_CMD_STR];
	
	if(tc->tcp[outportid].qdisccfg==0){
		sprintf(cmdstr,"%s qdisc add dev %s root handle %u:0 htb default 1",
			        	TC_CMD,tc->tcp[outportid].eth,tc->tcp[outportid].handleid);
		TcExecCmdAndPrint(cmdstr);
		tc->tcp[outportid].qdisccfg = 1;
	}
	sprintf(cmdstr,"%s class add dev %s parent %u:0 classid %u:%u htb rate %uKbit %s",
			            TC_CMD,tc->tcp[outportid].eth,
			            tc->tcp[outportid].handleid,
			            tc->tcp[outportid].handleid,
			            vir->handleid,vir->totalbw[TC_UP_LINK],TC_VIRLINE_QUANTUM);
	TcExecCmdAndPrint(cmdstr);
	tc->tcp[outportid].upvirline_ref++;
	return 0;
}
static int TcExecDelUpVirline(TcConfig* tc,TcVirline * vir,uint16_t outportid)
{
	if(tc->tcswitch == 0) return 0;

	char cmdstr[MAX_TC_CMD_STR];
	
	sprintf(cmdstr,"%s class del dev %s parent %u:0 classid %u:%u htb rate %uKbit %s",
			            TC_CMD,tc->tcp[outportid].eth,
			            tc->tcp[outportid].handleid,
			            tc->tcp[outportid].handleid,
			            vir->handleid,vir->totalbw[TC_UP_LINK],TC_VIRLINE_QUANTUM);
	TcExecCmdAndPrint(cmdstr);

	tc->tcp[outportid].upvirline_ref--;
	
	if(tc->tcp[outportid].qdisccfg==1 && 
	   tc->tcp[outportid].ifcfg==0 &&
	   tc->tcp[outportid].upvirline_ref==0){
	   
		sprintf(cmdstr,"%s qdisc del dev %s root",TC_CMD,tc->tcp[outportid].eth);
		TcExecCmdAndPrint(cmdstr);
		tc->tcp[outportid].qdisccfg = 0;
	}
	
	return 0;
}

static int TcExecAddVirine(TcConfig* tc,TcVirline * vir,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0) return 0;
	char cmdstr[MAX_TC_CMD_STR];
	sprintf(cmdstr,"%s class add dev %s parent %u:0 classid %u:%u htb rate %uKbit %s",
			            TC_CMD,tc->tcp[portid].eth,
			            tc->tcp[portid].handleid,
			            tc->tcp[portid].handleid,
			            vir->handleid,vir->totalbw[TC_DN_LINK],TC_VIRLINE_QUANTUM);
	TcExecCmdAndPrint(cmdstr);
#if POINT_OUTDEV==1
	TcExecAddUpVirine(tc,vir,vir->outportid);
#endif
	return 0;
}
static int TcExecDelVirline(TcConfig* tc,TcVirline * vir,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0) return 0;
	int pos;
	char cmdstr[MAX_TC_CMD_STR];
	sprintf(cmdstr,"%s class del dev %s parent %u:0 classid %u:%u htb rate %uKbit %s",
			            TC_CMD,tc->tcp[portid].eth,
			            tc->tcp[portid].handleid,
			            tc->tcp[portid].handleid,
			            vir->handleid,vir->totalbw[TC_DN_LINK],TC_VIRLINE_QUANTUM);
	TcExecCmdAndPrint(cmdstr);
#if POINT_OUTDEV==1
	TcExecDelUpVirline(tc,vir,vir->outportid);
#endif
	return 0;
}


static TcVirline * TcAllocVirline(TcConfig * tc)
{
	int index;
	for(index = 0; index < MAX_TC_VIRLINE; index++){
		if(tc->virline[index].used == 0){
			tc->virline[index].virchain.index= index;
			tc->virline[index].used     = 1;
			return &tc->virline[index];
		}
	}
	return NULL;
}

static void TcFreeVirline(TcVirline * virline)
{
	virline->used = 0;
}

static TcVirline * TcFindVirline(TcConfig* tc,uint32_t virid,uint16_t portid)
{
	int pos;
	ARRAY_FOREACH(pos,&tc->tcp[portid].virlinelist,virchain,tc->virline){
		if(tc->virline[pos].virid == virid){
			return &tc->virline[pos];
		}
	}
	return NULL;
}
static int TcAddVirline(TcConfig* tc,TcCtlParam * tp)
{
	TcPort * tcp = &tc->tcp[tp->portid];
	if(tp->vir_rate[TC_DN_LINK] > tcp->linkspeed[TC_DN_LINK]-tcp->usedspeed[TC_DN_LINK]){
		TRACE_TC("Don't have enough bandwidth for downlink virline:%u!\n",tp->virid);
		return -1;
	}
	if(tp->vir_rate[TC_UP_LINK] > tcp->linkspeed[TC_UP_LINK]-tcp->usedspeed[TC_UP_LINK]){
		TRACE_TC("Don't have enough bandwidth for uplink virline:%u!\n",tp->virid);
		return -1;
	}

	TcVirline * virline;

	virline = TcFindVirline(tc,tp->virid,tp->portid);
	if(virline != NULL){
		TRACE_TC("virtual line %u have created\n",tp->virid);
		return -1;
	}

	virline = TcAllocVirline(tc);
	if(virline == NULL) {
		TRACE_TC("alloc virtual line %u fail\n",tp->virid);
		return -1;
	}
	
	virline->virid     = tp->virid;
	virline->inportid  = tp->portid;
	virline->outportid = tp->outportid;
	virline->handleid  = virline->virchain.index + MAX_HANDLE_POS + MAX_ETHPORTS;
	virline->totalbw[TC_UP_LINK] = tp->vir_rate[TC_UP_LINK];
	virline->totalbw[TC_DN_LINK] = tp->vir_rate[TC_DN_LINK];
	virline->usedbw[TC_UP_LINK]  = 0;
	virline->usedbw[TC_DN_LINK]  = 0;
	virline->virsport.head = -1;
	virline->virsport.tail = -1;
	tcp->usedspeed[TC_UP_LINK] += tp->vir_rate[TC_UP_LINK];
	tcp->usedspeed[TC_DN_LINK] += tp->vir_rate[TC_DN_LINK];

	TcExecAddVirine(tc,virline,tp->portid);
	
	/**insert tail*/
	ARRAY_INSERT_TAIL(&tcp->virlinelist,virline,virchain,tc->virline);	
	return 0;
}


static int TcSportAddrFree(TcConfig * tc,TcSport * sport)
{
	int pos;
	ARRAY_FOREACH(pos,&sport->userlist,addrchain,tc->addr){
		tc->addr[pos].used = 0;
	}
	sport->userlist.head = -1;
	sport->userlist.tail = -1;
	return 0;
}

static void TcFreeSport(TcSport * sport)
{
	sport->used = 0;
}

static int TcClearSport(TcConfig* tc,TcSport * sport, uint16_t portid)
{
	TcVirline * vir;
	TcPort * tcp = &tc->tcp[portid];
	TcExecDelSport(tc,sport,portid);
	TcSportAddrFree(tc,sport);
	ARRAY_REMOVE(&tcp->sportlist,sport,sportchain,tc->sport);
	TcFreeSport(sport);
	return 0;
}

static int TcDelVirline(TcConfig* tc,TcCtlParam * tp)
{
	TcVirline * virline;
	TcPort * tcp = &tc->tcp[tp->portid];
	
	virline = TcFindVirline(tc,tp->virid,tp->portid);
	if(virline == NULL){
		TRACE_TC("virtual line %u have not existed\n",tp->virid);
		return -1;
	}
	int pos;
	TcSport * sport;
	ARRAY_FOREACH(pos,&virline->virsport,virsportchain,tc->sport){
		sport = &tc->sport[pos];
		TcClearSport(tc,sport,tp->portid);
	}

	TcExecDelVirline(tc,virline,tp->portid);
	
	tcp->usedspeed[TC_UP_LINK] -= virline->totalbw[TC_UP_LINK];
	tcp->usedspeed[TC_DN_LINK] -= virline->totalbw[TC_DN_LINK];
	ARRAY_REMOVE(&tcp->virlinelist,virline,virchain,tc->virline);
	TcFreeVirline(virline);
	return 0;
}

static TcSport * TcAllocSport(TcConfig * tc)
{
	int index;
	for(index = 0; index < MAX_TC_SPORT-1; index++){
		if(tc->sport[index].used == 0){
			tc->sport[index].sportchain.index = index;
			tc->sport[index].virsportchain.index = index;
			tc->sport[index].used     = 1;
			return &tc->sport[index];
		}
	}
	return NULL;
}

static TcSport * TcFindSport(TcConfig* tc,uint32_t sportid,uint16_t portid)
{
	int pos;
	ARRAY_FOREACH(pos,&tc->tcp[portid].sportlist,sportchain,tc->sport){
		if(tc->sport[pos].sportid == sportid){
			return &tc->sport[pos];
		}
	}
	return NULL;
}

static int TcSportBwCheck(TcVirline * vir,TcCtlParam * tp,int flag)
{
	uint32_t uptotal  = vir->totalbw[flag];
	uint32_t upused   = vir->usedbw[flag];
	uint32_t upleftbw = uptotal - upused;

	if(tp->ceil[flag] != 0 && tp->ceil[flag] > uptotal){
		TRACE_TC("%s link ceil [%u kbps] is high\n",(flag==TC_UP_LINK ? "up":"down"),tp->ceil[flag]);
		return -1;
	}
	if(tp->rate[flag] != 0 && tp->rate[flag] > upleftbw){
		TRACE_TC("Don't have enough bandwidth for %s link rate:%u!\n",(flag == TC_UP_LINK ? "up":"down"),tp->sportid);
		return -1;
	}
	return 0;
}

static int TcSportAddr(TcConfig * tc,TcCtlParam * tp,TcSport * sport)
{
	int index,i;
	int cnt = 0;
	int addr_nums = tp->addr_nums;
	for( index = 0; index < addr_nums; index++){
		for( i = 0; i < MAX_TC_ADDR; i++){
			if(tc->addr[i].used == 0){
				tc->addr[i].addr = tp->ip_addr[index];
				tc->addr[i].addrchain.index = i;
				tc->addr[i].used = 1;
				ARRAY_INSERT_TAIL(&sport->userlist,&tc->addr[i],addrchain,tc->addr);
				cnt++;
				break;
			}			
		}
	}
	if(cnt != addr_nums){
		TRACE_TC("save ipaddr failed,all: %d, cnt: %d\n",addr_nums,cnt);
	}
	return 0;
}

static int TcExecUpdateSport(TcConfig * tc,TcSport * sport,uint16_t portid)
{
	if(tc->tcswitch == 0 || tc->tcp[portid].enable == 0 || sport->forbid == 1) return 0;
	
	char cmdstr[MAX_TC_CMD_STR];
	uint32_t ratebw,ceilbw;
	ratebw = sport->surebw[TC_DN_LINK]!=0 ? sport->surebw[TC_DN_LINK] : sport->ceilbw[TC_DN_LINK];
	ceilbw = sport->ceilbw[TC_DN_LINK]!=0 ? sport->ceilbw[TC_DN_LINK] : sport->surebw[TC_DN_LINK];
	sprintf(cmdstr,"%s class change dev %s parent %u:%u classid %u:%u htb rate %uKbit ceil %uKbit prio %u %s",
					TC_CMD,tc->tcp[portid].eth,
					tc->tcp[portid].handleid,tc->virline[sport->virindex].handleid,
					tc->tcp[portid].handleid,sport->handleid,
					ratebw,ceilbw,sport->priority,TC_QUANTUM);
	
	TcExecCmdAndPrint(cmdstr);

	uint16_t outportid = tc->virline[sport->virindex].outportid;
	ratebw = sport->surebw[TC_UP_LINK]!=0 ? sport->surebw[TC_UP_LINK] : sport->ceilbw[TC_UP_LINK];
	ceilbw = sport->ceilbw[TC_UP_LINK]!=0 ? sport->ceilbw[TC_UP_LINK] : sport->surebw[TC_UP_LINK];
	sprintf(cmdstr,"%s class change dev %s parent %u:%u classid %u:%u htb rate %uKbit ceil %uKbit prio %u %s",
					TC_CMD,tc->tcp[outportid].eth,
					tc->tcp[outportid].handleid,tc->virline[sport->virindex].handleid,
					tc->tcp[outportid].handleid,sport->handleid,
					ratebw,ceilbw,sport->priority,TC_QUANTUM);
	
	TcExecCmdAndPrint(cmdstr);

	return 0;
}

static void TcPrint(TcConfig *tc,TcPort *port)
{
	int pos;
	TRACE_TC("Forward\n");
	ARRAY_FOREACH(pos,&port->sportlist,sportchain,tc->sport){
		TRACE_TC("index:%d pret:%d next:%d %u %u %u\n",
			tc->sport[pos].sportchain.index,
			tc->sport[pos].sportchain.pret,
			tc->sport[pos].sportchain.next,
			tc->sport[pos].prior,
			tc->sport[pos].priority,
			tc->sport[pos].sportid);
	}
	TRACE_TC("Back   \n");
	ARRAY_FOREACH_BACK(pos,&port->sportlist,sportchain,tc->sport){
		TRACE_TC("index:%d pret:%d next:%d %u %u %u\n",
			tc->sport[pos].sportchain.index,
			tc->sport[pos].sportchain.pret,
			tc->sport[pos].sportchain.next,
			tc->sport[pos].prior,
			tc->sport[pos].priority,
			tc->sport[pos].sportid);
	}
}

static int TcSportInstall(TcConfig * tc,TcSport * sport,uint16_t portid)
{
	TcPort * tcp = &tc->tcp[portid];
	
	sport->sportchain.pret = -1;
	sport->sportchain.next  = -1;
	sport->priority = 0;
	if(tcp->sportlist.head == -1 && tcp->sportlist.tail == -1){
		tcp->sportlist.head = sport->sportchain.index;
		tcp->sportlist.tail = sport->sportchain.index;
		return 0;
	}
	int pos;
	for(pos = tcp->sportlist.head; pos != -1; pos = tc->sport[pos].sportchain.next){
		if(sport->prior <= tc->sport[pos].prior){
			break;
		}
	}
	if(pos == tcp->sportlist.head){
		sport->priority = tc->sport[pos].priority;
		tc->sport[pos].sportchain.pret = sport->sportchain.index;
		sport->sportchain.next = tc->sport[pos].sportchain.index;
		tcp->sportlist.head = sport->sportchain.index;
	}else if(pos == -1){
		sport->priority = tc->sport[tcp->sportlist.tail].priority + 1;
		tc->sport[tcp->sportlist.tail].sportchain.next = sport->sportchain.index;
		sport->sportchain.pret = tc->sport[tcp->sportlist.tail].sportchain.index;
		tcp->sportlist.tail = sport->sportchain.index;
	}else{
		sport->priority = tc->sport[pos].priority;
		sport->sportchain.pret = tc->sport[pos].sportchain.pret;
		sport->sportchain.next = tc->sport[pos].sportchain.index;
		tc->sport[sport->sportchain.pret].sportchain.next = sport->sportchain.index;
		tc->sport[sport->sportchain.next].sportchain.pret = sport->sportchain.index;
	}

	int start = pos;
	while(pos != -1){
		tc->sport[pos].priority++;
		tc->sport[pos].prior++;
		TcExecUpdateSport(tc,&tc->sport[pos],portid);
		pos = tc->sport[pos].sportchain.next;
	}
	//update other veth user priority
	uint16_t index;
	for(index = 0; index < MAX_ETHPORTS; index++){
		if(index == portid) continue;	
		ARRAY_FOREACH(pos, &tc->tcp[index].sportlist, sportchain, tc->sport){
			if(tc->sport[pos].prior >= sport->prior)
				tc->sport[pos].prior++;
		}
	}
	return 0;
}

static int TcSportUnInstall(TcConfig * tc,TcSport * sport,uint16_t portid)
{
	TcPort * tcp = &tc->tcp[portid];
	int pos = sport->sportchain.next;
	ARRAY_REMOVE(&tcp->sportlist,sport,sportchain,tc->sport);
	while(pos != -1){
		tc->sport[pos].priority--;
		tc->sport[pos].prior--;
		TcExecUpdateSport(tc,&tc->sport[pos],portid);
		pos = tc->sport[pos].sportchain.next;
	}
	//update other veth user priority
	uint16_t index;
	for(index = 0; index < MAX_ETHPORTS; index++){
		if(index == portid) continue;	
		ARRAY_FOREACH(pos, &tc->tcp[index].sportlist, sportchain, tc->sport){
			if(tc->sport[pos].prior > sport->prior)
				tc->sport[pos].prior--;
		}
	}
	return 0;
}

static int TcUpdatePrio(TcConfig * tc,TcCtlParam * tp)
{
	if (!(tp->cmdvalue & TC_VALUE_TCID) || !(tp->cmdvalue & TC_VALUE_PRIOR)){
		printf("%s -S vEth0 -g(tc id) -o (new priority)\n",gTc.program_name);
		return -1;
	}
	TcSport * sport = TcFindSport(tc,tp->sportid,tp->portid);
	if (sport == NULL){
		printf("Don't find the TC of %u !\n",tp->sportid);
		return -1;
	}
	if (sport->prior == tp->priority) return 0;
	
	TcSportUnInstall(tc,sport,tp->portid);
	sport->prior = tp->priority;
	TcSportInstall(tc,sport,tp->portid);
	TcExecUpdIptables(tc,sport,tp->portid);
	return 0;
}

static int TcAddSport(TcConfig * tc,TcCtlParam * tp)
{
	TcSport   * sport;
	TcVirline * virline;
	TcPort * tcp = &tc->tcp[tp->portid];
	
	sport = TcFindSport(tc,tp->sportid,tp->portid);
	if(sport != NULL){
		TRACE_TC("traffic channel %u have existed\n",tp->sportid);
		return -1;
	}
	
	virline = TcFindVirline(tc,tp->virid,tp->portid);
	if(virline == NULL){
		TRACE_TC("virtual line %u have not existed\n",tp->virid);
		return -1;
	}
	if(TcSportBwCheck(virline,tp,TC_UP_LINK) < 0 ||
	   TcSportBwCheck(virline,tp,TC_DN_LINK) < 0){
	    return -1;
	}
	
	sport = TcAllocSport(tc);
	if(sport == NULL) {
		TRACE_TC("alloc traffic channel %u fail\n",tp->sportid);
		return -1;
	}
	
	sport->sportid   = tp->sportid;
	sport->prior     = tp->priority;
	sport->virindex  = virline->virchain.index;
	sport->forbid    = !TC_SUBPORT_FUN_FORBID;
	sport->addr_nums = tp->addr_nums;
	sport->handleid  = sport->sportchain.index + MAX_HANDLE_POS + MAX_ETHPORTS + MAX_TC_VIRLINE;
	sport->shandleid = sport->handleid + MAX_TC_SPORT;
	sport->type      = (tp->cmdvalue & TC_VALUE_SINGLE_UP) ? 1 : 0;
	sport->iptype    = tp->iptype;
    //memcpy(sport->protomask,tp->protomask,sizeof(tp->protomask));
    //new add 2 lines
    sport->appid     = tp->appid;
    sport->apptype   = TcGetAppType(tp->appid);
	
	sport->surebw[TC_UP_LINK] = tp->rate[TC_UP_LINK];
	sport->surebw[TC_DN_LINK] = tp->rate[TC_DN_LINK];
	sport->ceilbw[TC_UP_LINK] = tp->ceil[TC_UP_LINK];
	sport->ceilbw[TC_DN_LINK] = tp->ceil[TC_DN_LINK];
	sport->sigebw[TC_UP_LINK] = tp->sceil[TC_UP_LINK];
	sport->sigebw[TC_DN_LINK] = tp->sceil[TC_DN_LINK];

	virline->usedbw[TC_UP_LINK]  += sport->surebw[TC_UP_LINK];
	virline->usedbw[TC_DN_LINK]  += sport->surebw[TC_DN_LINK];

	sport->userlist.head = -1;
	sport->userlist.tail = -1;
	switch(sport->iptype){
		case IP_MASK:
			TcSportAddr(tc,tp,sport);
			break;
		case IP_RANGE:
			memcpy(sport->iprange,tp->iprange,sizeof(tp->iprange));
			break;
		case IP_SET:
			strncpy(sport->ipset,tp->ipset,MAX_IPSET_NAME-1);
			break;
	}
	
	TcSportInstall(tc,sport,tp->portid);

	TcExecAddSport(tc,sport,tp->portid);

	ARRAY_INSERT_TAIL(&virline->virsport, sport, virsportchain, tc->sport);
	return 0;
}

static int TcDelSport(TcConfig * tc,TcCtlParam * tp)
{
	TcSport   * sport;
	TcVirline * vir;
	TcPort * tcp = &tc->tcp[tp->portid];
	
	sport = TcFindSport(tc,tp->sportid,tp->portid);
	if(sport == NULL){
		TRACE_TC("traffic channel %u have not existed\n",tp->sportid);
		return -1;
	}

	vir = &tc->virline[sport->virindex];

	TcExecDelSport(tc,sport,tp->portid);
	
	vir->usedbw[TC_UP_LINK] -= sport->surebw[TC_UP_LINK];
	vir->usedbw[TC_DN_LINK] -= sport->surebw[TC_DN_LINK];
	ARRAY_REMOVE(&vir->virsport,sport,virsportchain,tc->sport);
	TcSportUnInstall(tc,sport,tp->portid);
	TcSportAddrFree(tc,sport);
	TcFreeSport(sport);
	return 0;	
}

static int TcRulesAdd(TcConfig * tc,TcCtlParam * tp)
{
	int ret;
	int outportid;
	if((tp->cmdvalue & TC_VALUE_VIRLINE)&&(tp->cmdvalue & TC_VALUE_VIRLINE_RATE)){
		if(tp->cmdvalue & TC_VALUE_OUTDEV){
			outportid = TcPortLook(tc,tp->outeth);
			if(outportid < 0) {
				TRACE_TC("you appoint -O %s which is not exist\n",tp->outeth);
				return -1;
			}
			tp->outportid = outportid;	
 			return TcAddVirline(tc,tp);
		}
		else {
			TRACE_TC("you should appoint -O [outdev] when add virtual line\n");
			return -1;
		}
	}
	
	if(tp->cmdvalue & TC_VALUE_FILE && TcParseFile(tp->configfile,tp,1) < 0){
		return -1;
	}
	
	if(TcCheckCmdline(tp) < 0) return -1;
	if(TcAddSport(tc,tp) < 0) return -1;
	return 0;
}

static int TcRulesDel(TcConfig * tc,TcCtlParam * tp)
{
	int ret;
	if (tp->cmdvalue & TC_VALUE_TCID){
		ret = TcDelSport(tc,tp);
	}
	else if(tp->cmdvalue & TC_VALUE_VIRLINE){
		ret = TcDelVirline(tc,tp);
	}
	else{
		printf("%s -D %s -g(TC id) or -l(VL id)\n",gTc.program_name,tc->tcp[tp->portid].eth);
		ret = -1;
	}
	return ret;
}

static int TcRulesUpdate(TcConfig * tc, TcCtlParam *tp)
{
	if (!(tp->cmdvalue & TC_VALUE_TCID)){
		printf("%s -U vEth0 [UP/DOWN] -g(groupid) -crsto\n",gTc.program_name);
		return -1;
	}
	uint32_t cmdvalue	= tp->cmdvalue;

	TcSport   * sport = TcFindSport(tc,tp->sportid,tp->portid);
	TcVirline * vir   = &tc->virline[sport->virindex];
	if (sport == NULL){
		printf("Traffic Channel id %u is not found!\n",tp->sportid);
		return -1;
	}
	if(cmdvalue & TC_VALUE_RATE && cmdvalue & TC_VALUE_CEIL){
		if(tp->ceil[TC_UP_LINK] < tp->rate[TC_UP_LINK] ||
		   tp->ceil[TC_DN_LINK] < tp->rate[TC_DN_LINK] ){
			printf("uplink or downlink assure rate is bigger than ceil rate!\n");
			return -1;
		}
	}

	TcVirline tvir;
	memcpy(&tvir,vir,sizeof(TcVirline));
	if(cmdvalue & TC_VALUE_RATE || cmdvalue & TC_VALUE_CEIL){
		tvir.usedbw[TC_UP_LINK] -= sport->surebw[TC_UP_LINK];
		tvir.usedbw[TC_DN_LINK] -= sport->surebw[TC_DN_LINK];
		if(TcSportBwCheck(&tvir,tp,TC_UP_LINK) == 0 &&
		   TcSportBwCheck(&tvir,tp,TC_DN_LINK) == 0)
		{
			TcExecDelSport(tc,sport,tp->portid);
			if(cmdvalue & TC_VALUE_RATE){
				vir->usedbw[TC_UP_LINK] = tvir.usedbw[TC_UP_LINK] + tp->rate[TC_UP_LINK];
				vir->usedbw[TC_DN_LINK] = tvir.usedbw[TC_DN_LINK] + tp->rate[TC_DN_LINK];
				sport->surebw[TC_UP_LINK] = tp->rate[TC_UP_LINK];
				sport->surebw[TC_DN_LINK] = tp->rate[TC_DN_LINK];
			}
			if(cmdvalue & TC_VALUE_RATE){
				sport->ceilbw[TC_UP_LINK] = tp->ceil[TC_UP_LINK];
				sport->ceilbw[TC_DN_LINK] = tp->ceil[TC_DN_LINK];				
			}
			TcExecAddSport(tc,sport,tp->portid);
			return 0;
		}
		else return -1;
	}
	if(cmdvalue & TC_VALUE_VIRLINE_RATE){
		printf("system don't support update virtual line rate!\n");
		return -1;
	}
	if(cmdvalue & TC_VALUE_SUBPORT_UP){
		if(sport->forbid==0) return 0;
		sport->forbid = !TC_SUBPORT_FUN_FORBID;
		TcExecAddSport(tc,sport,tp->portid);
		return 0;
	}
	if(cmdvalue & TC_VALUE_SUBPORT_DOWN){
		if(sport->forbid==1) return 0;
		TcExecDelSport(tc,sport,tp->portid);
		sport->forbid = TC_SUBPORT_FUN_FORBID;
		return 0;
	}
	if(cmdvalue & TC_VALUE_SINGLE_UP){
		if(sport->type == 1) return 0;
		if(sport->ceilbw[TC_UP_LINK] < tp->sceil[TC_UP_LINK] ||
		   sport->ceilbw[TC_DN_LINK] < tp->sceil[TC_DN_LINK]){
			printf("single ip rate is too high!\n");
			return -1;
		}
		else {
			TcExecDelSport(tc,sport,tp->portid);
			sport->type = 1;
			sport->sigebw[TC_UP_LINK] = tp->sceil[TC_UP_LINK];
			sport->sigebw[TC_DN_LINK] = tp->sceil[TC_DN_LINK];
			TcExecAddSport(tc,sport,tp->portid);
			return 0;
		}
	}
	if(cmdvalue & TC_VALUE_SINGLE_DOWN){
		if(sport->type == 0) return 0;
		TcExecDelSport(tc,sport,tp->portid);
		sport->type = 0;
		memset(sport->sigebw,0,sizeof(sport->sigebw));
		TcExecAddSport(tc,sport,tp->portid);
		return 0;
	}
	return 0;
}

static int TcEthUp(TcConfig * tc,uint16_t portid)
{
	if(tc->tcswitch == 0) return 0;
	char cmdstr[MAX_TC_CMD_STR];
	TcPort * port = &tc->tcp[portid];

	if(tc->tcp[portid].qdisccfg==0){
		sprintf(cmdstr,"%s qdisc del dev %s root 2> /dev/null",TC_CMD,port->eth);
		system(cmdstr);

		sprintf(cmdstr,"%s qdisc add dev %s root handle %d:0 htb default 1",
			        	TC_CMD,port->eth,port->handleid);
		if(TcExecCmd(cmdstr) < 0){
			TRACE_TC("FAIL: %s\n",cmdstr);
			return -1;
		}
		else TRACE_TC("OK  : %s\n",cmdstr);
		tc->tcp[portid].qdisccfg = 1;
	}
	
	char chainname[MAX_TC_CMD_STR];
	sprintf(chainname,"%s_%d",IPTABLES_CHAIN,portid);
	sprintf(cmdstr,"%s -t %s -N %s",IPTABLES_CMD,TABLES,chainname);
	TcExecCmdAndPrint(cmdstr);
	sprintf(cmdstr,"%s -t %s -A %s -j %s",IPTABLES_CMD,TABLES,IPTABLES_CHAIN,chainname);
	TcExecCmdAndPrint(cmdstr);
	
#if POINT_OUTDEV==0
	sprintf(cmdstr,"%s qdisc add dev %s ingress",TC_CMD,port->eth);
	if(TcExecCmd(cmdstr) < 0){
		TRACE_TC("FAIL: %s\n",cmdstr);
	}
	else TRACE_TC("OK  : %s\n",cmdstr);

	sprintf(cmdstr,"%s filter add dev %s parent ffff: protocol ip u32 match u32 0 0 flowid 1:1 action mirred egress redirect dev %s",
			        TC_CMD,port->eth,TC_VIR_NIC);
	if(TcExecCmd(cmdstr) < 0){
		TRACE_TC("FAIL: %s\n",cmdstr);
	}
	else TRACE_TC("OK  : %s\n",cmdstr);
#endif
	int pos;
	TcVirline * vir;
	ARRAY_FOREACH(pos, &port->virlinelist, virchain, tc->virline){
		vir = &tc->virline[pos];
		TcExecAddVirine(tc,vir,portid);
	}
	
	TcSport * sport;
	ARRAY_FOREACH(pos, &port->sportlist, sportchain, tc->sport){
		sport = &tc->sport[pos];
		TcExecAddSport(tc,sport,portid);
	}
	tc->tcp[portid].ifcfg = 1;
	return 0;
	
}

static int TcEthDown(TcConfig * tc,uint16_t portid)
{
	if(tc->tcswitch == 0) return 0;
	TcPort * port = &tc->tcp[portid];
	int pos;
	TcSport * sport;
	ARRAY_FOREACH(pos, &tc->tcp[portid].sportlist, sportchain, tc->sport){
		sport = &tc->sport[pos];
		TcExecDelSport(tc,sport,portid);
	}
	TcVirline * vir;
	ARRAY_FOREACH(pos, &port->virlinelist, virchain, tc->virline){
		vir = &tc->virline[pos];
		TcExecDelVirline(tc,vir,portid);
	}
	tc->tcp[portid].ifcfg = 0;

	char cmdstr[MAX_TC_CMD_STR];
	char chainname[MAX_TC_CMD_STR];
	sprintf(chainname,"%s_%d",IPTABLES_CHAIN,portid);
	sprintf(cmdstr,"%s -t %s -D %s -j %s",IPTABLES_CMD,TABLES,IPTABLES_CHAIN,chainname);
	TcExecCmdAndPrint(cmdstr);
	sprintf(cmdstr,"%s -t %s -F %s",IPTABLES_CMD,TABLES,chainname);
	TcExecCmdAndPrint(cmdstr);
	sprintf(cmdstr,"%s -t %s -X %s",IPTABLES_CMD,TABLES,chainname);
	TcExecCmdAndPrint(cmdstr);
	
	if(tc->tcp[portid].qdisccfg==1 && tc->tcp[portid].upvirline_ref==0){
		sprintf(cmdstr,"%s qdisc del dev %s root",TC_CMD,tc->tcp[portid].eth);
		if(TcExecCmd(cmdstr) < 0){
			TRACE_TC("FAIL: %s\n",cmdstr);
			return -1;
		}
		TRACE_TC("OK  : %s\n",cmdstr);
		tc->tcp[portid].qdisccfg = 0;
	}
	
#if POINT_OUTDEV==0
	sprintf(cmdstr,"%s qdisc del dev %s ingress",TC_CMD,tc->tcp[portid].eth);
	if(TcExecCmd(cmdstr) < 0){
		TRACE_TC("FAIL: %s\n",cmdstr);
		return -1;
	}
	TRACE_TC("OK  : %s\n",cmdstr);
#endif	
	return 0;
}

static int TcEthEnable(TcConfig * tc,uint16_t portid)
{
	if(tc->tcp[portid].enable == 1){
		TRACE_TC("TC: %s Tc have enabled!\n",tc->tcp[portid].eth);
		return -1;
	}
	tc->tcp[portid].enable = 1;
	TcEthUp(tc,portid);
	tc->tcpons++;
	return 0;

}

static int TcEthDisable(TcConfig * tc,uint16_t portid)
{
	if(tc->tcp[portid].enable == 0){
		TRACE_TC("TC: %s Tc have disabled!\n",tc->tcp[portid].eth);
		return 0;
	}
	TcEthDown(tc,portid);
	tc->tcp[portid].enable = 0;
	tc->tcpons--;
	return 0;
}

static int TcSwitchOn(TcConfig * tc)
{
	if(tc->tcswitch == 1) {
		TRACE_TC("TC: Tc have switched on!\n");
		return 0;
	}
	int index;
	int cnt = 0;
	tc->tcswitch = 1;
	
#if POINT_OUTDEV == 0
	char cmdstr[256];
	sprintf(cmdstr,"%s qdisc add dev %s root handle 1:0 htb default 1",TC_CMD,TC_VIR_NIC);
	if(TcExecCmd(cmdstr) < 0){
		tc->tcswitch = 0;
		TRACE_TC("FAIL: %s\n",cmdstr);
		return -1;
	}
	TRACE_TC("OK  : %s\n",cmdstr);
#endif

	for(index = 0; index < MAX_ETHPORTS; index++){
		if(tc->tcp[index].enable == 1 && TcEthUp(tc,index) < 0){
			continue;
		}
		cnt++;
	}
	TRACE_TC("TC: Tc switch on ok,%d-%d!\n",tc->tcpons,cnt);
	return 0;
}

static int TcSwitchOff(TcConfig * tc)
{
	if(tc->tcswitch == 0) {
		TRACE_TC("TC: Tc have switched off!\n");
		return 0;
	}
	int index;
	int cnt = 0;
	for(index = 0; index < MAX_ETHPORTS; index++){
		if(tc->tcp[index].enable == 1 && TcEthDown(tc,index) < 0){
			continue;
		}
		cnt++;
	}
	TRACE_TC("TC: Tc switch off ok,%d-%d!\n",tc->tcpons,cnt);
#if POINT_OUTDEV == 0
		char cmdstr[256];
		sprintf(cmdstr,"%s qdisc del dev %s root handle 1:0 htb default 1",TC_CMD,TC_VIR_NIC);
		if(TcExecCmd(cmdstr) < 0){
			TRACE_TC("FAIL: %s\n",cmdstr);
		}
		TRACE_TC("OK  : %s\n",cmdstr);	
#endif
	tc->tcswitch = 0;
	return 0;
}

static TcConfig * TcConfigInit()
{
	TcConfig * tc;
	gTc.shmid = shmget((key_t)TC_SHM_KEY_ID, sizeof(TcConfig), 0666|IPC_CREAT|IPC_EXCL);
	if(gTc.shmid < 0){
		gTc.newflag = 0;
		gTc.shmid = shmget((key_t)TC_SHM_KEY_ID, sizeof(TcConfig), 0666);
	}
	else {
		gTc.newflag = 1;
	}
	
	if(gTc.shmid < 0) {
		TRACE_TC("Get shared memory failed!\n");
		exit(EXIT_FAILURE);
	}
	tc = (TcConfig*)shmat(gTc.shmid,NULL,0);
	if(tc == (TcConfig*)-1){
		TRACE_TC("Bind addr failed!\n");
		exit(EXIT_FAILURE);
	}

	if(gTc.newflag == 0) return tc;
	
	memset(tc,0,sizeof(TcConfig));

	int index = 0;
	while ( index < MAX_ETHPORTS ){
		tc->tcp[index].sportlist.head = -1;
		tc->tcp[index].sportlist.tail = -1;
		tc->tcp[index].virlinelist.head = -1;
		tc->tcp[index].virlinelist.tail = -1;
		index++;
	}
#if POINT_OUTDEV == 0
	char cmdstr[256];
	//insert module ifb
	if(TcExecCmd("modprobe ifb") < 0){
		TRACE_TC("FAIL: modprobe ifb\n");
		shmctl(gTc.shmid,IPC_RMID,NULL);
		return NULL;
	}
	else TRACE_TC("OK  : modprobe ifb\n");
	
	sprintf(cmdstr,"ip link set dev %s up txqueuelen 1000",TC_VIR_NIC);
	if(TcExecCmd(cmdstr) < 0){
		TRACE_TC("FAIL: %s\n",cmdstr);
		shmctl(gTc.shmid,IPC_RMID,NULL);
		return NULL;
	}
	else TRACE_TC("OK  : %s\n",cmdstr);
#endif	
	return tc;
}


static void TcPortInit(struct system_info *sysinfo,TcConfig * tc)
{
	struct 	portinfo * pf = &sysinfo->portinfos;
	int ret   = -1;
	
	int index = 0;
	while ( index < MAX_ETHPORTS ){
		if(pf->kni[index] != NULL && pf->kni[index]->name != NULL)
		{
			strncpy(tc->tcp[index].eth,pf->kni[index]->name,MAX_NAME_STRING-1);
			if(pf->status_uk[index]&USER_STATUS) 
				tc->tcp[index].inuse = 1;
			tc->tcp[index].mode     = pf->mode[index].mode;
			tc->tcp[index].value    = pf->mode[index].value;	
			tc->tcp[index].portid   = index;
			tc->tcp[index].handleid = index + MAX_HANDLE_POS;
			tc->tcp[index].linkspeed[TC_UP_LINK] = 1000 * 1000;
			tc->tcp[index].linkspeed[TC_DN_LINK] = 1000 * 1000;
		}
		index++;
	}
}

static void TcInfoDump(TcConfig * tc,TcCtlParam * tp)
{
	TcPort * tcp = &tc->tcp[tp->portid];
	TcSport * sport;
	TcVirline * vir;
	
	if(tp->cmdvalue & TC_VALUE_TCID){
		sport = TcFindSport(tc,tp->sportid,tp->portid);
		if(sport == NULL){
			printf("Don't have this traffic channel %u\n",tp->sportid);
			return;
		}

		if(tp->cmdvalue & TC_VALUE_VIRLINE){
			if(tc->virline[sport->virindex].virid != tp->virid){
				printf("Virtual line %u don't have this traffic channel %u\n",
						tp->virid,tp->sportid);
				return;
			}
		}
		vir = &tc->virline[sport->virindex];
		TcPrintOnlyVirline(vir);
		TcPrintSport(tc,sport);
		return;
	}
	else if ((tp->cmdvalue & TC_VALUE_VIRLINE)){
		vir = TcFindVirline(tc,tp->virid,tp->portid);
		if(vir == NULL){
			printf("Don't have this virtual line %u\n",tp->virid);
			return;
		}
		TcPrintVirline(tc,vir);
	}
	else{
		int pos;
		ARRAY_FOREACH(pos,&tcp->virlinelist,virchain,tc->virline){
			TcPrintOnlyVirline(&tc->virline[pos]);
		}
	}
}

static void TcListPort(struct system_info * sysinfo,TcConfig * tc)
{
	struct portinfo * pf = &sysinfo->portinfos;
	int index = 0;
	uint32_t unit = 1000;
	printf("QOS:%s\n",tc->tcswitch ? "on":"off");
	printf("There are %d ports.\n",pf->portn);
	while ( index < RTE_MAX_ETHPORTS ){
		if(pf->kni[index]->name!=NULL){
			printf("Port: ID=%d,name=%s,(rxrings %d: txrings:%d)",
				    index,pf->kni[index]->name,pf->rxrings[index],pf->txrings[index]);
			printf(",mode %s,value %d,",portmode[pf->mode[index].mode],pf->mode[index].value);
			if(pf->status_uk[index]&USER_STATUS){
				printf("Status Link Up,is IXGBE:%s,",(pf->status_uk[index]&IS_IXGBE)?"yes":"no");
				printf("LinkSpeed:%d QOS:%s\n",(tc->tcp[index].linkspeed[TC_DN_LINK] / unit),
					                           tc->tcp[index].enable==1 ? "UP" : "DOWN");
			}
			else {
				printf("Status Link Down,is IXGBE:%s,",(pf->status_uk[index]&IS_IXGBE)?"yes":"no");
				printf("LinkSpeed:%d QOS:%s\n",(tc->tcp[index].linkspeed[TC_DN_LINK] / unit),
					                           tc->tcp[index].enable==1 ? "UP" : "DOWN");
			}
		}
		index++;
	}
}

static void TcReSet(TcConfig * tc)
{
	memset(tc,0,sizeof(TcConfig));
	int index = 0;
	while ( index < MAX_ETHPORTS ){
		tc->tcp[index].sportlist.head = -1;
		tc->tcp[index].sportlist.tail = -1;
		tc->tcp[index].virlinelist.head = -1;
		tc->tcp[index].virlinelist.tail = -1;
		index++;
	}
	char cmdstr[MAX_TC_CMD_STR];
	sprintf(cmdstr,"%s -t %s -F %s",IPTABLES_CMD,TABLES,IPTABLES_CHAIN);
	TcExecCmd(cmdstr);

#if POINT_OUTDEV == 0
	if(TcExecCmd("modprobe ifb") < 0) TRACE_TC("FAIL: modprobe ifb\n");
	else TRACE_TC("OK  : modprobe ifb\n");

	sprintf(cmdstr,"ip link set dev %s up txqueuelen 1000",TC_VIR_NIC);
	if(TcExecCmd(cmdstr) < 0) TRACE_TC("FAIL: %s\n",cmdstr);
	else TRACE_TC("OK  : %s\n",cmdstr);
#endif

	printf("Clear Data Ok!\n");
}

/*cmd lines parse*/
int do_command(int argc,char *argv[])
{
	int opt;
	int ret;
	int option_index;
	
	uint32_t command      = 0;
	
	const char * argvalue = NULL;
	const char * ethvalue = NULL;
	const char * outether = NULL;
	const char * ipaddr   = NULL;
	char 	   * appproto;
	const char * configfile = NULL;
	const char * unit;
	int   pr;    
	int   value;
	
	TcCtlParam * tp = &gTc.cmdtc;
	
	tp->portid = USHRT_MAX;

	struct system_info *sysinfo = gTc.sysinfo;
	
	while ((opt = getopt_long(argc,argv,
			                  tcs_short_options,
			                  tcs_long_options,
			                  &option_index))!=EOF){

		ret = 0;
		
		switch (opt) {
				/*
				 * Command selection
				 */
			case 'T':
				argvalue = optarg;
				if(strcmp(argvalue,"on")==0){
					add_command(&command, TC_CMD_SWITCHON,TC_CMD_NONE);
				}
				else if(strcmp(argvalue,"off")==0){
					add_command(&command, TC_CMD_SWITCHOFF,TC_CMD_NONE);
				}
				else {
					printf("please input %s -T [on|off]\n",gTc.program_name);
					return -1;
				}
				break;
				
			case 'I':
				ethvalue = optarg;
				strncpy(tp->eth,ethvalue,MAX_NAME_STRING-1);
				if (optind < argc && argv[optind][0] != '-'){
					argvalue = argv[optind++];
				}
				else break;
				if (strcmp(argvalue,"UP")==0){
					add_command(&command, TC_CMD_ENABLE,TC_CMD_NONE);
				}
				else if (strcmp(argvalue,"DOWN")==0){
					add_command(&command, TC_CMD_DISABLE,TC_CMD_NONE);
				}
				else {
					printf("please input %s -I [eth0] [UP/DOWN]\n",gTc.program_name);
					return -1;
				}
				break;
				
			case 'A':
				ethvalue = optarg;
				strncpy(tp->eth,ethvalue,MAX_NAME_STRING-1);
				add_command(&command,TC_CMD_ADD,TC_CMD_NONE);
				break;
				

			case 'D':
				ethvalue = optarg;
				strncpy(tp->eth,ethvalue,MAX_NAME_STRING-1);
				add_command(&command,TC_CMD_DELETE,TC_CMD_NONE);
				break;
				
			case 'U':
				ethvalue = optarg;
				strncpy(tp->eth,ethvalue,MAX_NAME_STRING-1);
				add_command(&command,TC_CMD_UPDATE,TC_CMD_NONE);
				if (optind < argc && argv[optind][0] != '-'){
					argvalue = argv[optind++];
					if (strcmp(argvalue,"UP")==0){
						tp->cmdvalue |= TC_VALUE_SUBPORT_UP;
					}
					else if (strcmp(argvalue,"DOWN")==0){
						tp->cmdvalue |= TC_VALUE_SUBPORT_DOWN;
					}
				}
				break;

			case 'S':
				ethvalue = optarg;
				strncpy(tp->eth,ethvalue,MAX_NAME_STRING-1);
				add_command(&command,TC_CMD_SHIFT,TC_CMD_NONE);			
				break;
				
			case 'L':
				ethvalue = optarg;
				strncpy(tp->eth,ethvalue,MAX_NAME_STRING-1);
				add_command(&command,TC_CMD_LIST,TC_CMD_NONE);
				break;
				
			case 'E':
				add_command(&command,TC_CMD_PORT_USED,TC_CMD_NONE);
				break;

			case 'R':
				add_command(&command,TC_CMD_RESET,TC_CMD_NONE);
				break;

			case 'P':
				ethvalue = optarg;
				strncpy(tp->eth,ethvalue,MAX_NAME_STRING-1);
				add_command(&command,TC_CMD_PRINT,TC_CMD_NONE);
				break;
				
			case 'h':
				exit_printhelp();
				break;

			case 'O':
				outether = optarg;
				strncpy(tp->outeth,outether,MAX_NAME_STRING-1);
				tp->cmdvalue |= TC_VALUE_OUTDEV;
				break;

			case 'u': //user equal ip addr
				ipaddr = optarg;
			    if(TcAddrParse(ipaddr,tp) < 0) return -1;
				tp->iptype = IP_MASK;
				tp->cmdvalue |= TC_VALUE_USE;
				break;
			case 'e':
				ipaddr = optarg;
				strncpy(tp->ipset,ipaddr,MAX_IPSET_NAME-1);
				tp->iptype = IP_SET;
				tp->cmdvalue |= TC_VALUE_USE;
				break;
			case 'd':
				ipaddr = optarg;
				if(TcAddrRangeParse(ipaddr,tp) < 0) return -1;
				tp->iptype = IP_RANGE;
				tp->cmdvalue |= TC_VALUE_USE;
				break;
			case 'p': //app or proto
                /*
				appproto = optarg;
				if(TcProtoParse(appproto,tp->protomask) < 0) return -1;
				*/
				//new add
				value = atoi(optarg);
                tp->appid = (uint32_t)value;
                    
				tp->cmdvalue |= TC_VALUE_PROTOCOL;
				break;	
			case 'r': //assure rate
				argvalue = optarg;
				if (optind < argc && argv[optind][0] != '-'){
					unit = argv[optind++];
				}else {
					unit = NULL;
				}
				if(TcGetUnit(unit,&pr) < 0) return -1;
				if(TcRateParse(argvalue,pr,tp->rate) < 0) return -1;
				tp->cmdvalue |= TC_VALUE_RATE;
				break;
				
			case 'c': //ceil rate
				argvalue = optarg;
				if (optind < argc && argv[optind][0] != '-'){
					unit = argv[optind++];
				}else {
					unit = NULL;
				}
				if(TcGetUnit(unit,&pr) < 0) return -1;
				if(TcRateParse(argvalue,pr,tp->ceil) < 0) return -1;
				tp->cmdvalue |= TC_VALUE_CEIL;
				break;

			case 't':
				tp->cmdvalue |= TC_VALUE_SINGLE_DOWN;
				break;

			case 's':
				argvalue = optarg;
				if (optind < argc && argv[optind][0] != '-'){
					unit = argv[optind++];
				}else {
					unit = NULL;
				}
				if(TcGetUnit(unit,&pr) < 0) return -1;
				if(TcRateParse(argvalue,pr,tp->sceil) < 0) return -1;		
				tp->cmdvalue |= TC_VALUE_SINGLE_UP;
				break;
				
			case 'g': //traffic unique id   
				value = atoi(optarg);
				tp->sportid = value;
				tp->cmdvalue |= TC_VALUE_TCID;
				break;
			case 'o': //dynamic priority
				value = atoi(optarg);
				tp->priority = value;
				tp->cmdvalue |= TC_VALUE_PRIOR;
				break;
			case 'f': 
				configfile = optarg;
				strncpy(tp->configfile,configfile,MAX_FILE_PATH-1);
				tp->cmdvalue |= TC_VALUE_FILE;
				break;
			case 'l': 
				value = atoi(optarg);
				tp->virid =(uint32_t)value;
				tp->cmdvalue |= TC_VALUE_VIRLINE;
				break;
			case 'v':
				argvalue = optarg;
				if (optind < argc && argv[optind][0] != '-'){
					unit = argv[optind++];
				}else {
					unit = NULL;
				}
				if(TcGetUnit(unit,&pr) < 0) return -1;
				if(TcRateParse(argvalue,pr,tp->vir_rate) < 0) return -1;	
				tp->cmdvalue |= TC_VALUE_VIRLINE_RATE;
				break;
			default:
				printf("There is not a option -%c! Please %s -h for help!\n",opt,argv[0]);
				return -1;	
		}
	}
	
	int portid = TcPortLook(gTc.stc,tp->eth);
	if(portid < 0) return -1;
	tp->portid = portid;

	switch (command) {

		case TC_CMD_SWITCHON:
			TcSwitchOn(gTc.stc);
			break;
			
		case TC_CMD_SWITCHOFF:
			TcSwitchOff(gTc.stc);
			break;
			
		case TC_CMD_ENABLE:
			TcEthEnable(gTc.stc,portid);
			break;
			
		case TC_CMD_DISABLE:
			TcEthDisable(gTc.stc,portid);
			break;
			
		case TC_CMD_ADD:
			ret = TcRulesAdd(gTc.stc,tp);
			break;
			
		case TC_CMD_DELETE:
			ret = TcRulesDel(gTc.stc,tp);
			break;

		case TC_CMD_UPDATE:
			ret = TcRulesUpdate(gTc.stc,tp);
			break;
			
		case TC_CMD_SHIFT:
			TcUpdatePrio(gTc.stc,tp);			
			break;
			
		case TC_CMD_LIST:
			TcInfoDump(gTc.stc,tp);
			break;
			
		case TC_CMD_PRINT:
			TcPrint(gTc.stc,&(gTc.stc->tcp[tp->portid]));
			break;
			
		case TC_CMD_PORT_USED:
			TcListPort(gTc.sysinfo,gTc.stc);
			break;
			
		case TC_CMD_RESET:
			TcReSet(gTc.stc);
			break;
	}

	return ret; 
}

static void tc_ctl_exit(int signal){
	exit(0);
}

int main(int argc, char *argv[])
{
	int ret = 0;

	char * name = strrchr(argv[0], '/');
	if(name)
		name++;
	else
		name = argv[0];

	
	gTc.program_name = name;
	
	gTc.sysinfo= get_dpdkshm(name, (char*)"program1");
	if(!gTc.sysinfo){
		printf("get sharemeory 1 fail.exit!\n");
		exit(-1);
	}
	
	signal(SIGINT, tc_ctl_exit);
	signal(SIGQUIT,tc_ctl_exit);
	signal(SIGABRT,tc_ctl_exit);
	signal(SIGKILL,tc_ctl_exit);

	gTc.stc = TcConfigInit();
	if(gTc.stc == NULL){
		printf("Init sharemeory fail.exit!\n");
		exit(-1);		
	}
	TcPortInit(gTc.sysinfo,gTc.stc);
	gTc.pidid = getpid();
	
	ret = do_command(argc,argv);

	if ( ret < 0 ){
		exit(-1);
	}
	
	return 0;
}


