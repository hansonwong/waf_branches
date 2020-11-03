#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define SIZE_LINE		1024	//max length every line
#define SIZE_FILENAME	256		//max file name length

#define min(x, y)		(x <= y) ? x : y

typedef enum _ELineType_ {
    LINE_IDLE,		//not processing line
	LINE_ERROR,		//error line
	LINE_EMPTY,		//blank line or comment line
	LINE_SECTION,	//section
	LINE_VALUE		//value
} ELineType ;


static char gFilename[SIZE_FILENAME];
static char *gBuffer;
static int gBuflen;

//trim left and right space
static char *StrStrip(char *s)
{
	size_t size;
	char *p1, *p2;

	size = strlen(s);
	if (!size)
		return s;

	p2 = s + size - 1;

	while ((p2 >= s) && isspace(*p2))
		p2 --;
	*(p2 + 1) = '\0';

	p1 = s;
	while (*p1 && isspace(*p1))
		p1 ++;
	if (s != p1)
		memmove(s, p1, p2 - p1 + 2);
	return s;
}

static int StriCmp(const char *s1, const char *s2)
{
	int ch1, ch2;
	do
	{
		ch1 = (unsigned char)*(s1++);
		if ((ch1 >= 'A') && (ch1 <= 'Z'))
			ch1 += 0x20;

		ch2 = (unsigned char)*(s2++);
		if ((ch2 >= 'A') && (ch2 <= 'Z'))
			ch2 += 0x20;
	} while ( ch1 && (ch1 == ch2) );
	return(ch1 - ch2);
}

static int GetLine(char *buf, int buflen, char *content, char **rem1, char **rem2, char **nextline)
{
	char *cont1, *cont2;
	int cntblank, cntCR, cntLF;
	char isQuot1, isQuot2;
	int i;
	char *p;
	
	cntblank = 0;
	cntCR = cntLF = 0;
	isQuot1 = isQuot2 = 0;
	cont1 = *rem1 = 0;
	content[0] = 0;
	for (i = 0, p = buf; i < buflen; i ++, p ++)
	{
		if (*p == 0) {
			p ++;
			break;
		}
		if (cntCR == 2 || cntLF == 2) {
			p --;
			break;
		}
		if (cntCR + cntLF >= 2) {
			break;
		}
		if ((cntCR || cntLF) && *p != '\r' && *p != '\n')
			break;

		switch (*p) {
		case '\r':
			cntCR ++;
			break;
		case '\n':
			cntLF ++;
			break;
		case '\'':
			if (!isQuot2)
				isQuot1 = 1 - isQuot1;
			break;
		case '\"':
			if (!isQuot1)
				isQuot2 = 1 - isQuot2;
			break;
		case ';':
		case '#':
			if (isQuot1 || isQuot2)
				break;
			if (*rem1 == NULL)
				*rem1 = p - cntblank;
			break;
		default:
			if (isspace((unsigned char)*p)) {
				cntblank ++;
			} else {
				cntblank = 0;
				if ((*rem1 == NULL) && (cont1 == NULL))
					cont1 = p;
			}
			break;
		}
	}

	*nextline = p;
	*rem2 = p - cntCR - cntLF;
	if (*rem1 == NULL)
		*rem1 = *rem2;
	cont2 = *rem1 - cntblank;

	if (cont1 == NULL) {
		cont1 = cont2;
		return LINE_EMPTY;
	}

	i = (int)(cont2 - cont1);
	if (i >= SIZE_LINE)
		return LINE_ERROR;

	memcpy(content, cont1, i);
	content[i] = 0;

	if (content[0] == '[' && content[i - 1] == ']')
		return LINE_SECTION;
	if (strchr(content, '=') != NULL)
		return LINE_VALUE;
	
	return LINE_ERROR;
}

static int FindSection(const char *section, char **sect1, char **sect2, char **cont1, char **cont2, char **nextsect)
{
	int type;
	char content[SIZE_LINE];
	char *rem1, *rem2, *nextline;

	char *p;
	char *empty;
	int uselen = 0;
	char found = 0;

	if (gBuffer == NULL) {
		return 0;
	}

	while (gBuflen - uselen > 0) {
		p = gBuffer + uselen;
		type = GetLine(p, gBuflen - uselen, content, &rem1, &rem2, &nextline);
		uselen += (int)(nextline - p);

		if (LINE_SECTION == type) {
			if (found || section == NULL) break;
			content[strlen(content) - 1] = 0;
			StrStrip(content + 1);
			if (StriCmp(content + 1, section) == 0) {
				found = 1;
				*sect1 = p;
				*sect2 = rem1;
				*cont1 = nextline;
			}
			empty = nextline;
		} else
		if (LINE_VALUE == type) {
			if (!found && section == NULL) {
				found = 1;
				*sect1 = p;
				*sect2 = p;
				*cont1 = p;
			}
			empty = nextline;
		}
	}
	
	if (!found) return 0;

	*cont2 = empty;
	*nextsect = nextline;
	return 1;
}

static void GetKeyValue(char *content, char **key, char **value)
{
	char *p;

	p = strchr(content, '=');
	*p = 0;
	StrStrip(content);
	StrStrip(p + 1);
	*key = content;
	*value = p + 1;
}

void iniFileFree()
{
	if (gBuffer != NULL) {
		free(gBuffer);
		gBuffer = 0;
		gBuflen = 0;
	}
}

int iniFileLoad(const char *filename)
{
	FILE *file;
	int len;

	iniFileFree();
	if(filename == NULL) return -1;
	if (strlen(filename) >= sizeof(gFilename))
		return -1;
	strcpy(gFilename, filename);

	file = fopen(gFilename, "rb");
	if (file == NULL) 
		return -1;

	fseek(file, 0, SEEK_END);
	len = ftell(file);
	gBuffer = malloc(len);
	if (gBuffer == NULL) {
		fclose(file);
		return -1;
	}

	fseek(file, 0, SEEK_SET);
	len = fread(gBuffer, 1, len, file);
	fclose(file);
	gBuflen = len;
	return 0;
}

static int iniGetValue(const char *section, const char *key, char *value, int maxlen, const char *defvalue)
{
	int type;
	char content[SIZE_LINE];
	char *rem1, *rem2, *nextline;
	char *key0, *value0;

	char *p;
	int uselen = 0;
	char found = 0;

	int len;

	if (gBuffer == NULL || key == NULL) {
		if (value != NULL)
			value[0] = 0;
		return 0;
	}

	while (gBuflen - uselen > 0) {
		p = gBuffer + uselen;
		type = GetLine(p, gBuflen - uselen, content, &rem1, &rem2, &nextline);
		uselen += (int)(nextline - p);

		if (LINE_SECTION == type) {
			if (found || section == NULL) break;
			content[strlen(content) - 1] = 0;
			StrStrip(content + 1);
			if (StriCmp(content + 1, section) == 0) {
				found = 1;
			}
		} else
		if (LINE_VALUE == type) {
			if (!found && section == NULL) {
				found = 1;
			}
			if (!found)
				continue;
			GetKeyValue(content, &key0, &value0);
			if (StriCmp(key0, key) == 0) {
				len = strlen(value0);
				if (len == 0) break;
				if (value != NULL) {
					len = min(len, maxlen - 1);
					strncpy(value, value0, len);
					value[len] = 0;
				}
				return 1;
			}
		}
	}
	if (value != NULL) {
		if (defvalue != NULL) {
			len = min(((int)strlen(defvalue)), maxlen - 1);
			strncpy(value, defvalue, len);
			value[len] = 0;
		} else {
			value[0] = 0;
		}
	}
	return 0;
}
int iniGetString(const char *section, const char *key, char *value, int maxlen, const char *defvalue)
{
	int ret;
	int len;

	ret = iniGetValue(section, key, value, maxlen, defvalue);
	if (!ret)
		return ret;
	
	len = strlen(value);
	if (value[0] == '\'' && value[len - 1] == '\'') {
		value[len - 1] = 0;
		memmove(value, value + 1, len - 1);
	} else
	if (value[0] == '\"' && value[len - 1] == '\"') {
		value[len - 1] = 0;
		memmove(value, value + 1, len - 1);
	}
	return ret;
}

int iniGetInt(const char *section, const char *key, int defvalue)
{
	char valstr[64];

	if (iniGetValue(section, key, valstr, sizeof(valstr), NULL))
	    return (int)strtol(valstr, NULL, 0);
	return defvalue;
}

double iniGetDouble(const char *section, const char *key, double defvalue)
{
	char valstr[64];

	if (iniGetValue(section, key, valstr, sizeof(valstr), NULL))
	    return (int)atof(valstr);
	return defvalue;
}

int iniSetString(const char *section, const char *key, const char *value)
{
	FILE *file;
	char *sect1, *sect2, *cont1, *cont2, *nextsect;
	char *p;
	int len, type;
	char content[SIZE_LINE];
	char *key0, *value0;
	char *rem1, *rem2, *nextline;

	cont1 = NULL;
	if (gBuffer == NULL) {
		return 0;
	}

	if (FindSection(section, &sect1, &sect2, &cont1, &cont2, &nextsect) == 0)
	{
		if (value == NULL) 
			return 0;
		
		file = fopen(gFilename, "ab");
		if (file == NULL) 
			return 0;
		fprintf(file, "\n[%s]\n%s = %s\n", section, key, value);
		fclose(file);
		iniFileLoad(gFilename);
		return 1;
	}
	
	p = cont1;
	len = (int)(cont2 - cont1);
	while (len > 0) {
		type = GetLine(p, len, content, &rem1, &rem2, &nextline);

		if (LINE_VALUE == type) {
			GetKeyValue(content, &key0, &value0);
			if (StriCmp(key0, key) == 0) {

				file = fopen(gFilename, "wb");
				if (file == NULL)
					return 0;
				len = (int)(p - gBuffer);
				fwrite(gBuffer, 1, len, file);
				if (value == NULL) {
					len = (int)(nextline - gBuffer);	
				} else {
					fprintf(file, "%s = %s", key, value);
					len = (int)(rem1 - gBuffer);			
				}
				fwrite(gBuffer + len, 1, gBuflen - len, file);
				fclose(file);
				iniFileLoad(gFilename);
				return 1;
			}	
		}

		len -= (int)(nextline - p);
		p = nextline;
	}

	if (value == NULL) 
		return 0;

	file = fopen(gFilename, "wb");
	if (file == NULL) 
		return 0;
	len = (int)(cont2 - gBuffer);
	fwrite(gBuffer, 1, len, file);
	fprintf(file, "%s = %s\n", key, value);
	fwrite(gBuffer + len, 1, gBuflen - len, file);
	fclose(file);
	iniFileLoad(gFilename);
	return 1;
}

int iniSetInt(const char *section, const char *key, int value, int base)
{
	char valstr[64];

	switch (base) {
	case 16:
		sprintf(valstr, "0x%x", value);
		return iniSetString(section, key, valstr);
	case 8:
		sprintf(valstr, "0%o", value);
		return iniSetString(section, key, valstr);
	default:
		sprintf(valstr, "%d", value);
		return iniSetString(section, key, valstr);
	}
}

