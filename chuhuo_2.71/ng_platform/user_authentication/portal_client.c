#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>          
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>

#define APPROVE_TACTICS_FILE "/etc/userauth/auth_tactics.conf"
#define APPROVE_SERVER_FILE "/etc/userauth/external_auth.conf"
#define ALINE_MAX_SIZE 512
int verbose=0;
void usage(char *argv0){
	fprintf(stderr, "\nUsage: %s -u username -p passwd -a ipaddr -n tacticsid\n", argv0);
	fprintf(stderr, "\nUsage: %s -h for this massage\n", argv0);
	exit(-1);
}

void get_line_info(char *buf,char *info,char *keywords){
	char *p=buf;
	char *p1=NULL;
	int i=0;
	while(strncmp(p,keywords,strlen(keywords))!=0){
		while(*p!=' '){
			p++;
			if((p-buf)>=strlen(buf))
				break;
		}		
		if((p-buf)>=strlen(buf))
			break;
		p++;
	}
	p=p+strlen(keywords)+1;
	p1=p;
	while(*p1!=' '&&*p1!='\n'){
		i++;
		p1++;
	}
	strncpy(info,p,i);
}

static int find_user_approve_type(char *tid,char *serverid,int *type){
	FILE *file;
	char buffer[ALINE_MAX_SIZE]={0};
	char tacticsid[16]={0};
	char approvetype[2]={0};
	char authtype[12]={0};
	if((file = fopen(APPROVE_TACTICS_FILE,"r"))==NULL){
		perror("open APPROVE_TACTICS_FILE err!");
		exit(-1);
	}
	while(fgets(buffer, ALINE_MAX_SIZE, file)!=NULL){
		memset(tacticsid,0,sizeof(tacticsid));
		get_line_info(buffer,tacticsid,"id");
		
		if(verbose)
			printf("tacticsid:%s\n",tacticsid);		
		if(strcmp(tid,tacticsid)==0){
			memset(approvetype,0,sizeof(approvetype));
			get_line_info(buffer,approvetype,"approvetype");
			if(atoi(approvetype)==2){		//local auth
				memset(authtype,0,sizeof(authtype));
				get_line_info(buffer,authtype,"authtype");
				if(strncmp(authtype,"LDAP",4)==0){
					*type=1;
				}
				else
					*type=2;
			}
			else if(atoi(approvetype)==3){
				*type=0;
				memset(serverid,0,sizeof(serverid));
				get_line_info(buffer,serverid,"authserverid");
			}
			fclose(file);
			return 0;
		}
	}
	fclose(file);
	return -1;
}

static void deal_dn_and_username(char *dn,char *username){
	char dn_temp[128]={0};
	char *p;
	p=dn;
	int i = 0;
	while(*p!='='){
		i++;
		p++;
	}
	strncpy(dn_temp,dn,i+1);
	sprintf(dn_temp+i+1,"%s",username);
	while(*p!=','){
		p++;
	}
	sprintf(dn_temp+strlen(dn_temp),"%s",p);
	memset(dn,0,strlen(dn));
	strncpy(dn,dn_temp,strlen(dn_temp));
}

static int auth_pw4user(char *servid,char *username,char *passwd,char *cmd){
	FILE *fd;
	int type;
	int found=0;
	char buffer[ALINE_MAX_SIZE] = {0};
	char auth_serverid[16]={0};
	char serverip[16]={0};
	char port[16]={0};
	char shared_pw[128]={0};
	char authtype[8]={0};
	char dn[128]={0};
	if((fd = fopen(APPROVE_SERVER_FILE,"r"))==NULL){
		perror("fopen err!");
		exit(-1);
	}
	while(fgets(buffer, ALINE_MAX_SIZE, fd)!=NULL){
		memset(auth_serverid,0,sizeof(auth_serverid));
		get_line_info(buffer,auth_serverid,"serverid");
		//printf("buffer:%s\n",buffer);
		if(strcmp(servid,auth_serverid)==0){
			found=1;
			if(strncmp(buffer,"LDAP",4)==0){
				type=0;
				memset(serverip,0,sizeof(serverip));
				get_line_info(buffer,serverip,"serverip");
				memset(port,0,sizeof(port));
				get_line_info(buffer,port,"port");
				memset(dn,0,sizeof(dn));
				get_line_info(buffer,dn,"dn");
				deal_dn_and_username(dn,username);
				memset(authtype,0,sizeof(authtype));
				get_line_info(buffer,authtype,"authtype");
			}
			else if(strncmp(buffer,"RADIUS",6)==0){
				type=1;
				memset(serverip,0,sizeof(serverip));
				get_line_info(buffer,serverip,"serverip");
				memset(shared_pw,0,sizeof(shared_pw));
				get_line_info(buffer,shared_pw,"shared_pw");
				memset(port,0,sizeof(port));
				get_line_info(buffer,port,"port");
				memset(authtype,0,sizeof(authtype));
				get_line_info(buffer,authtype,"authtype");
			}
			fclose(fd);
			break;
		}	
		else{
			found=0;
		}
	}
	if(!found){		//not found serverip
		fclose(fd);
		return -1;
	}
	if(type==1){			//radius auth type
		if(strncmp(authtype,"CHAP",4)==0){	
			sprintf(cmd,"echo \"User-Name = %s, CHAP-Password = %s\" | /usr/bin/radclient %s:%s auth %s -x",
				username,passwd,serverip,port,shared_pw);
		}
		else if(strncmp(authtype,"PAP",3)==0){
			sprintf(cmd,"echo \"User-Name = %s, User-Password = %s\" | /usr/bin/radclient %s:%s auth %s -x",
				username,passwd,serverip,port,shared_pw);
		}
		return 0;
	}
	else if(type==0){		//ldap auth type
		if(strncmp(authtype,"SIMPLE",6)==0){	
			////////////////////DN/////////DN/////////////
			sprintf(cmd,"/usr/bin/ldapwhoami -x -D \"%s\" -w %s -h %s -p %s -v",
				dn,passwd,serverip,port);
		}
	}	
}

static int result_of_auth(char *auth_cmd){
	FILE *file;
	int i =0;
	char *p=NULL;
	char buffer[1024]={0};
	file = popen(auth_cmd,"r");
	if(file == NULL){
		perror("popen err");
		exit(-1);
	}
	while(fgets(buffer,sizeof(buffer),file)!=NULL){
		p=buffer;
		i=0;
		while(i++<strlen(buffer)){
			if(strncmp(p,"Received Access-Reject",22)==0){
			        pclose(file);
			        return -1;    
			}
			else if(strncmp(p,"Reply-Message",13)==0 || strncmp(p,"Success",7)==0 || strncmp(p,"Received Access-Accept",22)==0){
				//strcpy(resend_buff,"Authentication is Ok!");
				printf("0\n");
				pclose(file);
				return 0;
			}
			p++;
		}
	}
	pclose(file);
	return -1;
}

static void process_login_info(char *username,char *passwd,char *ipaddr,char *tacticsid){
	int ret,authtype;
	char auth_severid[16]={0};
	char cmd[256]={0};
	char ipset_cmd[256]={0};
	
	ret=find_user_approve_type(tacticsid,auth_severid,&authtype);
	if(ret == -1){
		//strcpy(resend_buff,"the ip is not allow!");
		printf("2\n");
	}
	else if(ret == 0){
		if(authtype==1){		//local ldap
			sprintf(cmd,"/usr/bin/ldapwhoami -D \"uid=%s,ou=People,dc=domain,dc=com\" -w %s -v",username,passwd);
		}
		else if(authtype==2){		//local radius
			sprintf(cmd,"echo \"User-Name = %s, CHAP-Password = %s\" | /usr/bin/radclient 127.0.0.1:1812 auth testing123 -x",
				username,passwd);
			if(verbose)
				printf("local auth cmd:%s\n",cmd);
		}
		else{
			ret = auth_pw4user(auth_severid,username,passwd,cmd);
			if(ret==-1){
				//strcpy(resend_buff,"have no match server conf!");
				printf("3\n");
			}
		}
		if(verbose)
			printf("cmd:%s\n",cmd);
		if((ret = result_of_auth(cmd))==-1){
			//strcpy(resend_buff,"failed user authentication!");
			printf("1\n");
		}
		else{
			sprintf(ipset_cmd,"/usr/local/sbin/ipset -A authed_set %s ",ipaddr);
			system(ipset_cmd);
		}
	}
}

int main(int argc,char *argv[]){
	int ch;
	char username[128]={0};
	char passwd[128] = {0};
	char ipaddr[16] = {0};
	char tacticsid[16]={0};
	char send2server_buff[2048]={0};
	while ((ch = getopt(argc, argv, "u:p:a:n:vh")) != -1) {
		//printf("optind: %d, optarg: %s\n", optind, optarg);
		switch(ch){
			case 'u':
				if(!optarg)
					usage(argv[0]);
				strcpy(username,optarg);
				break;
			case 'p':
				if(!optarg)
					usage(argv[0]);
				strcpy(passwd,optarg);
				break;
			case 'a':
				if(!optarg)
					usage(argv[0]);
				strcpy(ipaddr,optarg);
				break;
			case 'n':
				if(!optarg)
					usage(argv[0]);
				strcpy(tacticsid,optarg);
				break;
			case 'v':
				verbose=1;
				break;
			case 'h':
				usage(argv[0]);
				break;
			default:
				printf("no souch option!\n");
				usage(argv[0]);
		}
	}

	if(username[0] && passwd[0] && ipaddr[0]){
		process_login_info(username,passwd,ipaddr,tacticsid);
	}
	else {
		usage(argv[0]);
		exit(-1);
	}
	return 0;
}
