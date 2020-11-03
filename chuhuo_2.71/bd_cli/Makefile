#
# Bluedon bd_cli - Makefile
# -------------------
#
# Author: Gaobo
#
# Copyright. All Rights Reserved.
#
#

PROGNAME   = bdcli
VERSION    = 1.0

SRCDIR     = $(shell pwd)
SFILES     = bd_cli.c cli.c cli_cmd.c cli_util.c cmdedit.c cli_log.c inifile.c
IFILES     = cli.h cmdedit.h cli_log.h inifile.h

OBJFILES   = $(patsubst %,$(SRCDIR)/%,$(SFILES))
INCFILES   = $(patsubst %,$(SRCDIR)/%,$(IFILES))

CFLAGS 	  += -D CLI_CMD_EDIT
LDFLAGS   += -I. -I/usr/include/mysql
LIBS      += -L. -L/usr/lib64/mysql -L/usr/local/lib  -lcrypto -lmysqlclient

all: $(PROGNAME)

$(PROGNAME): $(OBJFILES) $(INCFILES)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(PROGNAME) $(OBJFILES) $(LIBS)
	chmod +x ./setup.sh
	exec ./setup.sh

clean:
	rm -f $(PROGNAME) *.o *~ a.out core core.[1-9][0-9]* *.stackdump 

