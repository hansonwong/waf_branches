
#ifndef __UTIL_H__
#define __UTIL_H__


#define IPQUAD_FORMAT "%u.%u.%u.%u"

#ifdef __BIG_ENDIAN
#define IPQUAD(addr) \
((unsigned char *)&addr)[3], \
((unsigned char *)&addr)[2], \
((unsigned char *)&addr)[1], \
((unsigned char *)&addr)[0]
#else
#define IPQUAD(addr) \
((unsigned char *)&addr)[0], \
((unsigned char *)&addr)[1], \
((unsigned char *)&addr)[2], \
((unsigned char *)&addr)[3]
#endif


const char * hook_type2str(uint16_t type);

int ByteExtractString(uint64_t *res, int base, uint16_t len, const char *str);

int ByteExtractStringUint16(uint16_t *res, int base, uint16_t len, const char *str);

#endif /*__UTIL_H__*/


