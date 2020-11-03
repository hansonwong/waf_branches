/***********************************************************************
 *
 *  Copyright (c)
 *  All Rights Reserved
 *
 *
 ************************************************************************/

#include "cli.h"
#include <arpa/inet.h>
#include <net/if_arp.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

/*
 * These are validation commands that are only used by the CLI menu.
 */

/***************************************************************************
// Function Name: ValidateMacAddress
// Description  : validate format of the MAC address.
// Parameters   : addr - MAC address.
// Returns      : FALSE - invalid format.
//                TRUE - valid format.
****************************************************************************/
unsigned char cli_isMacAddress(char *addr) 
{
   unsigned char ret = FALSE;
   int i = 0;
   char *pToken = NULL, *pLast = NULL, *pEnd = NULL;
   char buf[18];
   long num = 0;

   if ( addr == NULL || (strlen(addr) > 18) )
      return ret;

      // need to copy since strtok_r updates string
   strcpy(buf, addr);

   // IP address has the following format
   //   xxx.xxx.xxx.xxx where x is decimal number
   pToken = strtok_r(buf, ":", &pLast);
   if ( pToken == NULL )
      return ret;
   num = strtol(pToken, &pEnd, 16);

   if ( *pEnd == '\0' && num <= 255 ) 
   {
      for ( i = 0; i < 5; i++ ) 
      {
         pToken = strtok_r(NULL, ":", &pLast);
         if ( pToken == NULL )
            break;
         num = strtol(pToken, &pEnd, 16);
         if ( *pEnd != '\0' || num > 255 )
            break;
      }
      if ( i == 5 )
         ret = TRUE;
   }
   return ret;
}

/***************************************************************************
// Function Name: isIpAddress
// Description  : validate format of the IP address.
// Parameters   : buf - IP address.
// Returns      : CLI_FALSE - invalid format.
//                CLI_TRUE - valid format.
****************************************************************************/
unsigned char cli_isIpAddress(const char *addr)
{
   if (addr != NULL)
   {
      struct in_addr inp;

      if (inet_aton(addr, &inp))
      {
         return TRUE;
      }
   }
   return FALSE;
}

/***************************************************************************
// Function Name: isNumber
// Description  : validate decimal number from string. 
// Parameters   : buf - decimal number.
// Returns      : CLI_FALSE - invalid decimal number.
//                CLI_TRUE - valid decimal number.
****************************************************************************/
unsigned char cli_isNumber(const char *buf)
{
   if ( buf != NULL )
   {
      int size = strlen(buf);
      int i;

      for ( i = 0; i < size; i++ )
      {
         if ( isdigit(buf[i]) == 0 )
         {
            break;
         }
      }
      if ( size > 0 && i == size )
      {
         return TRUE;
      }
   }
   return FALSE;
}

/***************************************************************************
// Function Name: isValidIdleTimeout
// Description  : validate PPP idle timeout.
// Parameters   : timeout - PPP idle timeout.
// Returns      : FALSE - invalid format.
//                TRUE - valid format.
****************************************************************************/
unsigned char cli_isValidIdleTimeout(const char *timeout)
{
   if ( cli_isNumber(timeout) )
   {
      int num = atoi(timeout);
      if ( num <= 1090 && num >= 0 )
         return TRUE;
      else
         printf("\nidle timeout is out of range [0-1090]\n");
   }
   else
   {
      printf("\nInvalid idle timeout %s\n", timeout? timeout : "");
   }
   return FALSE;
}
