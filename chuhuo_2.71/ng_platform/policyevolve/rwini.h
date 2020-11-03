#ifndef _RW_INI_H_
#define _RW_INI_H_

#ifdef __cplusplus
extern "C" {
#endif


int iniFileLoad(const char *filename);
void iniFileFree();

int iniGetString(const char *section, const char *key, char *value, int size, const char *defvalue);
int iniGetInt(const char *section, const char *key, int defvalue);
double iniGetDouble(const char *section, const char *key, double defvalue);

int iniSetString(const char *section, const char *key, const char *value);
int iniSetInt(const char *section, const char *key, int value, int base);


#ifdef __cplusplus
}
#endif

#endif /*_RW_INI_H_*/


