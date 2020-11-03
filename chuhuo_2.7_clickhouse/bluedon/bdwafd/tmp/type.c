#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <math.h>
#include <pthread.h>
#include <sys/select.h>
#include <stdarg.h>
#include "vseos.h"
#include "vseapi.h"

//#define MY_DEBUG 

#ifdef MY_DEBUG
#define d(x) x
#else
#define d(x)
#endif

const char defpath[100] = "/usr/local/bluedon/cyren/deff/";

/*
 *Global initialization of the scan engine
 *This must be done once only for every process using the scan engine	
**/
VSERESULT AVSDK_vseGlobalInit(const void *license){
	VSERESULT result = vseGlobalInit(license);
	if(result){
		printf("AVSDK_vseGlobalInit  failed!\n");
		return result;
	}
	printf("AVSDK_vseGlobalInit  OK!\n");
	return result;
}

VSERESULT AVSDK_vseInitRelease(void){
	VSEHANDLE handle;
	VSERESULT result;
	result = vseInit( vseOnDemandEngineId, vseInitModeSpeed | vseInitModeDefsVersion2, defpath, NULL, NULL, &handle);
	if ( result ){
		printf("AVSDK_vseInit %s*-v2.def  failed!\n",defpath);
		vseGlobalRelease();
		return result;
	}
	vseRelease( handle );
	printf("AVSDK_vseInitRelease %s*-v2.def  OK!\n",defpath);
	return result;
}

/*
 *Global release of scan engine
 *This must be called once only for every process that called vseGlobalInit
**/
void AVSDK_vseGlobalRelease(void){
	vseGlobalRelease();
	printf("AVSDK_vseGlobalRelease  OK!\n");
}

/*
 * \brief Called when something is detected
 * \param hScan Scan Engine handle
**/
void handleDetect( VSEHANDLE hScan ,void *resultbuf){
	VSERESULT result;
	vseDetectionType detectionType;
	char malname[VSE_MAX_PATH] = {0};
	char Levbuf[10] = {0};
	char Virusname[50] = {0};
	//char Virustype[255] = {0};
    char * Virustype;
	
	/*Get the filename,prepare for creating the log*/
	result = vseGet( hScan, vsePropIdDetectionName, 0, malname, VSE_MAX_PATH );   /*Get the virus's name*/
	if ( result ){
		d(printf("Failed to get detection name,result = %d\n",result));
		sprintf(Virusname,"ERROR");
	}else{
		d(printf("Detection_Name: %s\n",malname));
		sprintf(Virusname,"%s",malname);
	}
	
	result = vseGet( hScan, vsePropIdDetectionType, 0, &detectionType, sizeof( detectionType ) );
	if ( result ){
		d(printf("Failed to get detection type,result = %d\n",result));
		strcat(Levbuf,"ERROR");
	}else{
		switch ( detectionType ){
			case vseDetectionTypeNone:
				d(printf("none\n"));
				strcpy(Levbuf,"low");
                Virustype = "vseDetectionTypeNone";
				break;
			case vseDetectionTypeVirus:
				d(printf("virus\n"));
				strcpy(Levbuf,"high");
                Virustype = "Virus";
				break;		
			case vseDetectionTypeAdware:
				d(printf("adware\n"));
				strcpy(Levbuf,"low");
                Virustype = "Adware";
				break;			
			case vseDetectionTypeApplication:
				d(printf("application\n"));
				strcpy(Levbuf,"low");
                Virustype = "Application";
				break;
			case vseDetectionTypeBackdoor:
				d(printf("backdoor\n"));
				strcpy(Levbuf,"high");
                Virustype = "Backdoor";
				break;				
			case vseDetectionTypeBomb:
				d(printf("bomb\n"));
				strcpy(Levbuf,"medium");
                Virustype = "Bomb";
				break;	
			case vseDetectionTypeBootVirus:
				d(printf("boot virus\n"));
				strcpy(Levbuf,"medium");
                Virustype = "BootVirus";
				break;
			case vseDetectionTypeDenial:
				d(printf("DOS\n"));
				strcpy(Levbuf,"medium");
                Virustype = "Denial";
				break;
			case vseDetectionTypeDialer:
				d(printf("dialer\n"));
				strcpy(Levbuf,"medium");
                Virustype = "Dialer";
				break;
			case vseDetectionTypeDownloader:
				d(printf("downloader\n"));
				strcpy(Levbuf,"high");
                Virustype = "Downloader";
				break;
			case vseDetectionTypeExploit:
				d(printf("exploit\n"));
				strcpy(Levbuf,"medium");
                Virustype = "Exploit";
				break;
			case vseDetectionTypeIntended:
				d(printf("intended\n"));
				strcpy(Levbuf,"low");
                Virustype = "Intended";
				break;			
			case vseDetectionTypeJoke:
				d(printf("joke\n"));
				strcpy(Levbuf,"low");
                Virustype = "Joke";
				break;
			case vseDetectionTypeMacro:
				d(printf("macro\n"));
				strcpy(Levbuf,"medium");
                Virustype = "Macro";
				break;
			case vseDetectionTypeMassMailer:
				d(printf("mass mailer\n"));
				strcpy(Levbuf,"medium");
                Virustype = "MassMailer";
				break;
			case vseDetectionTypeMisDisinfection:
				d(printf("mis disinfection\n"));
				strcpy(Levbuf,"low");
                Virustype = "Mis-disinfection";
				break;
			case vseDetectionTypeNetWorm:
				d(printf("networm\n"));
				strcpy(Levbuf,"high");
                Virustype = "NetworkWorm";
				break;
			case vseDetectionTypeP2PWorm:
				d(printf("P2P Worm\n"));
				strcpy(Levbuf,"high");
                Virustype = "P2PWorm";
				break;
			case vseDetectionTypeProxy:
				d(printf("proxy\n"));
				strcpy(Levbuf,"high");
                Virustype = "Proxy";
				break;
			case vseDetectionTypePasswordStealer:
				d(printf("password stealer\n"));
				strcpy(Levbuf,"high");
                Virustype = "PasswordStealer";
				break;
			case vseDetectionTypeRemote:
				d(printf("remote\n"));
				strcpy(Levbuf,"medium");
                Virustype = "Remote";
				break;
			case vseDetectionTypeRisk:
				d(printf("risk\n"));
				strcpy(Levbuf,"high");
                Virustype = "Risk";
				break;
			case vseDetectionTypeSpyware:
				d(printf("spyware\n"));
				strcpy(Levbuf,"high");
                Virustype = "Spyware";
				break;
			case vseDetectionTypeTool:
				d(printf("tool\n"));
				strcpy(Levbuf,"low");
                Virustype = "Tool";
				break;
			case vseDetectionTypeTrojan:
				d(printf("trojan\n"));
				strcpy(Levbuf,"high");
                Virustype = "Trojan";
				break;
			case vseDetectionTypeHiddenProcess:
				d(printf("hidden process\n"));
				strcpy(Levbuf,"medium");
                Virustype = "HiddenProcess";
				break;
			case vseDetectionTypeInjectedCode:
				d(printf("injected code\n"));
				strcpy(Levbuf,"high");
                Virustype = "InjectedCode";
				break;
                        case vseDetectionTypePacker:
                                d(printf("packer\n"));
                                strcpy(Levbuf,"medium");
                Virustype = "Packer";
                                break;
			default:
				d(printf("other\n"));
				strcpy(Levbuf,"low");
                Virustype = "other";
				break;
		}
	}
    printf("%s %s %s\n", Virustype, Virusname, Levbuf);
	//sprintf(resultbuf,"T %s %s",Virusname,Levbuf);
	sprintf(resultbuf,"T");
}

/*!
 * \brief Event handler. Called by scan engine
 * \param hScan Scan engine handle
 * \param evId Event ID
 * \param context Context pointer
 * \return Should return 0 most of the time 
 */
VSERESULT VSEAPI myEvents(const VSEHANDLE hScan, const VSEDWORD evId, void *context){
	switch ( evId ){			
		case vseEvIdDetect:
			d(printf("Detect \n"));
			handleDetect( hScan, context);
			break;
		default:
			break;
	}
	return( 0 );
}

/*!
 * \brief Context structure used for scan
 * */
typedef struct {
	int pipe;
	const char * path;
	VSEHANDLE handle;
	VSERESULT result;
	VSESIZE size;
	VSECHAR *buf;
} realScan_t;

/*!
 * \brief Scanning function
 * \param data Context pointer of type \ref realScan_t
 * \return NULL
 * */ 
 /*buf查杀*/
void *realScanbuf( void *data ){	
	realScan_t * ctx = (realScan_t *)data;
	if ( !ctx ) return( NULL );
	ctx->result = vseExec( ctx->handle, vseExecProcessBuf,(void*)ctx->path,ctx->buf,&(ctx->size) );
	close( ctx->pipe );
	return( NULL );
}

/*文件查杀*/
void * realScanfile( void *data ){
	realScan_t * ctx = (realScan_t *)data;
	if ( !ctx ) return( NULL );
	ctx->result = vseExec( ctx->handle, vseExecProcessFile, (void *)ctx->path, NULL, NULL );
	close( ctx->pipe );
	return( NULL );
}

/*文件查杀,缺省值为解压层数*/
int AVSDK_ScanFile(char *resultbuf, const char *filepathname,...){
	int phandle[2];
	int retval;
	VSEHANDLE handle;
	realScan_t ctx;
	pthread_t thread;
	fd_set fds;
   	struct timeval tv;
	const float timeout = 86400;
	
	sprintf(resultbuf,"F");

	VSEDWORD depth = 0;
	
	/*判断待扫描文件是否存在*/
	if(-1 == access(filepathname,F_OK)){
		d(printf("E %s not found!",filepathname));
		sprintf(resultbuf,"E %s not found!",filepathname);
		return -1;
	}

	/*Create pipe that will be used to signal end of scan*/
	if ( pipe( phandle )){
		d(printf("E Unable to create pipe for %s.",filepathname));
		sprintf(resultbuf,"E Unable to create pipe for %s.",filepathname);
		return -2;
	}
	
	// Initialize local handle
	VSERESULT result = vseInit( vseOnDemandEngineId, vseInitModeSpeed | vseInitModeDefsVersion2, defpath, myEvents, resultbuf, &handle );
	if ( result ){
		d(printf("E vseInit %s/*-v2.def  failed!\n",defpath));
		sprintf(resultbuf,"E vseInit %s/*-v2.def  failed!\n",defpath);
		return -3;
	}

	va_list arg_ptr;
	va_start(arg_ptr,filepathname);
	depth = va_arg(arg_ptr,VSEDWORD);
	va_end(arg_ptr);
	if(depth > 0 && depth < 99){
		result = vseSet( handle, vsePropIdArchiveDepth, 0, &depth, sizeof(VSEDWORD));
	}

	// Configure context pointer
	ctx.path = filepathname;
	ctx.handle = handle;
	ctx.pipe = phandle[1];
	ctx.result = 0;
	// Configure select() data
	FD_ZERO(&fds);
	FD_SET(phandle[0], &fds);
	tv.tv_sec = (int)floor(timeout);
    tv.tv_usec = (int)ceil((timeout - floor(timeout))*1000000.0);
    // Create a thread to do the actual scanning
	if ( pthread_create( &thread, NULL, realScanfile, &ctx ) ){
		d(printf("E Unable to create thread for %s.",filepathname));
		sprintf(resultbuf,"E Unable to create thread for %s.",filepathname);
		vseRelease( handle );
		return -4;
	}
	// Wait for end of scan to be signalled or timeout
	retval = select( phandle[0]+1, &fds,NULL , &fds, &tv);
	switch ( retval ){
		case 0: // timeout
			d(printf("time out.\n"));
			sprintf(resultbuf,"E Interrupting scan for %s.",filepathname);
			vseSet( handle, vsePropIdInterruptScan, 0, NULL, 0 );
			pthread_cancel(thread);
			break;
		case 1: // thread done
			d(printf("thread done\n"));
			pthread_detach(thread);
			break;
		case -1: // error
			d(printf("E Error in select for %s.",filepathname));
			sprintf(resultbuf,"E Error in select for %s.",filepathname);
			pthread_detach(thread);
			break;
		default: // weird case. Should never get here
			d(printf("E Other value for select:%d.",retval));
			sprintf(resultbuf,"E Other value for select:%d.",retval);
			pthread_detach(thread);
			break;
	}
	// close remaining pipe
	close( phandle[0] );
	close( phandle[1] );
	// release handle
	vseRelease( handle );
	return 0;
}

/*buf查杀*/
int AVSDK_ScanBuf(char *resultbuf, const char *filetype,VSECHAR *scanbuf,VSESIZE size){
	int phandle[2];
	int retval;
	VSEHANDLE handle;
	realScan_t ctx;
	pthread_t thread;
	fd_set fds;
   	struct timeval tv;
	const float timeout = 3;
	
	sprintf(resultbuf,"F ");
	
	/*Create pipe that will be used to signal end of scan*/
	if ( pipe( phandle ) ){
		d(printf("E Unable to create pipe for vseExecProcessBuf."));
		sprintf(resultbuf,"E Unable to create pipe for vseExecProcessBuf.");
		return -2;
	}
	
	// Initialize local handle
	VSERESULT result = vseInit( vseOnDemandEngineId, vseInitModeSpeed | vseInitModeDefsVersion2, defpath, myEvents, resultbuf, &handle );
	if ( result ){
		d(printf("E vseInit %s/*-v2.def  failed!\n",defpath));
		sprintf(resultbuf,"E vseInit %s/*-v2.def  failed!\n",defpath);
		return -3;
	}

	// Configure context pointer
	ctx.path = filetype;
	ctx.handle = handle;
	ctx.pipe = phandle[1];
	ctx.result = 0;
	ctx.size = size;
	ctx.buf = scanbuf;
	// Configure select() data
	FD_ZERO(&fds);
	FD_SET(phandle[0], &fds);
	tv.tv_sec = (int)floor(timeout);
    tv.tv_usec = (int)ceil((timeout - floor(timeout))*1000000.0);
    // Create a thread to do the actual scanning
	if ( pthread_create( &thread, NULL, realScanbuf, &ctx ) ){
		d(printf("E Unable to create thread for vseExecProcessBuf."));
		sprintf(resultbuf,"E Unable to create thread for vseExecProcessBuf.");
		vseRelease( handle );
		return -4;
	}
	// Wait for end of scan to be signalled or timeout
	retval = select( phandle[0]+1, &fds,NULL , &fds, &tv);
	switch ( retval ){
		case 0: // timeout
			d(printf("timeout\n"));
			sprintf(resultbuf,"E Interrupting scan for vseExecProcessBuf.");
			vseSet( handle, vsePropIdInterruptScan, 0, NULL, 0 );
			pthread_cancel(thread);
			break;
		case 1: // thread done
			d(printf("thread done\n"));
			pthread_detach(thread);
			break;
		case -1: // error
			d(printf("error\n"));
			sprintf(resultbuf,"E Error in select for vseExecProcessBuf.");
			pthread_detach(thread);
			break;
		default: // weird case. Should never get here
			d(printf("magic\n"));
			sprintf(resultbuf,"E Other value for select:%d.",retval);
			pthread_detach(thread);
			break;
	}
	// close remaining pipe
	close( phandle[0] );
	close( phandle[1] );
	// release handle
	vseRelease( handle );
	return 0;
}
