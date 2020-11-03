#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>

#include "util.h"

/* IP Hooks */
/* After promisc drops, checksum checks. */
#define IP_PRE_ROUTING	0
/* If the packet is destined for this box. */
#define IP_LOCAL_IN		1
/* If the packet is destined for another interface. */
#define IP_FORWARD		2
/* Packets coming from a local process. */
#define IP_LOCAL_OUT	3
/* Packets about to hit the wire. */
#define IP_POST_ROUTING	4
#define IP_NUMHOOKS		5 

#define _PF(f) case f: str = #f ; break;

const char *
hook_type2str(uint16_t type)
{
	static char unknown[] = "IP_UNKNOW_[XXXX]";
	char * str;

	switch(type) {
	_PF(IP_PRE_ROUTING)
	_PF(IP_LOCAL_IN)
	_PF(IP_FORWARD)
	_PF(IP_LOCAL_OUT)
	_PF(IP_POST_ROUTING)
	
	default:
		sprintf(unknown, "IP_UNKNOW_[%04x]", type);
		str = unknown;
		break;
	}
	return(str);
}

int ByteExtractString(uint64_t *res, int base, uint16_t len, const char *str)
{
    const char *ptr = str;
    char *endptr = NULL;
    char strbuf[24];

    if (len > 23) {
        printf("len too large (23 max)\n");
        return -1;
    }

    if (len) {
        memcpy(strbuf, str, len);
        strbuf[len] = '\0';
        ptr = strbuf;
    }
	
    errno = 0;
    *res = strtoull(ptr, &endptr, base);

    if (errno == ERANGE) {
        printf("Numeric value out of range\n");
        return -1;
    } else if (endptr == ptr && *res == 0) {
        printf("No numeric value\n");
        return -1;
    } else if (endptr == ptr) {
        printf("Invalid numeric value\n");
        return -1;
    }
	
    return (endptr - ptr);
}

int ByteExtractStringUint16(uint16_t *res, int base, uint16_t len, const char *str)
{
    uint64_t i64;
    int ret;

    ret = ByteExtractString(&i64, base, len, str);
    if (ret <= 0) {
        return ret;
    }

    *res = (uint16_t)i64;

    if ((uint64_t)(*res) != i64) {
        printf("Numeric value out of range (%lu > %u)", i64, UINT16_MAX);
        return -1;
    }
    return ret;
}


