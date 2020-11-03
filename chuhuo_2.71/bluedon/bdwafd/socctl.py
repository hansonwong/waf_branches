#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import commands

while 1:
   fp_read=open('/opt/controller/pipe/input_cmd','r')
   lines = fp_read.readlines()
   fp_read.close()
   lines=lines[0].split('|')
   order=lines[2]
   number=lines[0].rjust(10)
   print lines
   #if order=='reboot':
      #os.system('reboot')

   #if order=='shutdown':
      #os.system('shutdown')
   
   if order=='backup':
      filename=lines[3].split('\n')[0]
      cp_path='/opt/controller/backup'
      (status,output)=commands.getstatusoutput('cp %s %s'%(filename,cp_path))       
      fp_write=open('/opt/controller/pipe/output_cmd','w')
      if status!=0:         
         output= output.split('`')
         output=''.join(output).split('\'')
         output=''.join(output)
         remsg=number+'|'+lines[1]+'|'+lines[2]+'|'+'result=1'+'|'+'msg='+output+'\n'
         fp_write.write(remsg)
         print remsg
      else :      
         remsg=number+'|'+lines[1]+'|'+lines[2]+'|'+'result=0'+'|'+'msg=OK'+'\n'
         fp_write.write(remsg)
         print remsg
      fp_write.close()

   if order=='delete':      
      filename=lines[3].split('\n')[0]
      print filename















      
