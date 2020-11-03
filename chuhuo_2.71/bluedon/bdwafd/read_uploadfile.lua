--
--                  jianghaoliang 20161121
--  调用此脚本用于从debug日志中找到原上传文件的url,原文件名，上传时间等信息，记录在文件名上并转移到相关的路径
--
--
local send_file_to_path = "/root/uploadfile/";
local upload_file_path = "/tmp/haoliang/";
local modsecurity_debug_path="/usr/local/bluedon/bdwaf/logs/modsec_debug.log"

function get_sid(my_filename)
  assert(os.execute(string.format("grep %s %s  | awk -F 'sid#' '{printf $2}' | awk -F ']' '{printf $1}'",my_filename,modsecurity_debug_path)));
  return sid;
end 

function get_sid2(my_filename)
  local t = io.popen(string.format("grep %s %s  | awk -F 'sid#' '{printf $2}' | awk -F ']' '{printf $1}'",my_filename,modsecurity_debug_path));
  local sid = t:read("*all");
  if(sid=="")
  then
--error can't find string in debuglog
	return nil;
  end 
--print(string.format("#sid%s",sid));
  return sid;
end 

function get_time(unid)
  local t = io.popen(string.format("grep \"%s\" %s | awk -F ']' 'NR==1{printf $1}' | awk -F ' ' '{printf $1}' | awk -F '[' '{printf $2}'",unid,modsecurity_debug_path));
--print(string.format("grep \"%s\" %s | awk -F ']' 'NR==1{printf $1}' | awk -F ' ' '{printf $1}' | awk -F '[' '{printf $2}'",unid,modsecurity_debug_path));  
  local log_time = t:read("*all");
--print("log_time:",log_time)
  return log_time;
end

function get_filename(time_string,sid)
  print("get_filename-time_string:",time_string)
  print("get_filename-sid:",sid)
  local t = io.popen(string.format("grep \"%s\" %s| grep \"sid#%s\"  |awk -F 'Content-Disposition filename: ' '{printf $2}'",time_string,modsecurity_debug_path,sid,modsecurity_debug_path));
  print(string.format("grep \"%s\" %s| grep \"sid#%s\" |sed -n '/Content-Disposition filename/p' %s| awk -F 'Content-Disposition filename: ' '{printf $2}'",time_string,modsecurity_debug_path,sid,modsecurity_debug_path))
  local file_name = t:read("*all");
  print("file name:",file_name)
  print(string.format("#%s#",file_name))
  return file_name;
end



function  timestamp(year,month,day,hour,min,sec)
  local y_to_day = 0;
  y_to_day = (year-1970)*365
  y_to_day = y_to_day + ((year-year%4)-1972)/4
--print("day of year:",y_to_day)
--  month = {"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"}
  local m=month;
  local m_to_day=0
--print("m:",m)
  if(m=="Jan")
then
  m_to_day=0;
 
elseif(m=="Feb")
then
  m_to_day=31;

elseif(m=="Mar")
then
  m_to_day=31+28;

elseif(m=="Apr")
then
  m_to_day=31+28+31;

elseif(m=="May")
then
  m_to_day=31+28+31+30;

elseif(m=="Jun")
then
  m_to_day=31+28+31+30+31;

elseif(m=="Jul")
then
  m_to_day=31+28+31+30+31+30;

elseif(m=="Aug")
then
  m_to_day=31+28+31+30+31+30+31;

elseif(m=="Sep")
then
  m_to_day=31+28+31+30+31+30+31+31;

elseif(m=="Oct")
then
  m_to_day=31+28+31+30+31+30+31+31+30;

elseif(m=="Nov")
then
  m_to_day=31+28+31+30+31+30+31+31+30+31;

elseif(m=="Dec")
then
  m_to_day=31+28+31+30+31+30+31+31+30+31+30;
end
--print(m_to_day)
  if((year)%4==0)
then
  m_to_day = m_to_day+1;
end
 local total_day = y_to_day + m_to_day + (day-1);
-- beijing +8:00;
 local total_hour = total_day * 24 + hour -8 ;
 local total_min = total_hour * 60 + min ;
 local total_sec = total_min * 60 + sec ;
--print("result:",total_sec)
  return total_sec;	
end

function change_time(old_time)

  local time_string=old_time;
  local i=string.find(time_string,"/");
  if(i==nil)
  then
print("fdasfasfa")      
	return nil;
  end
  local day=string.sub(time_string,0,i-1);
--print(day)
  time_string=string.sub(time_string,i+1,string.len(time_string));
  i=string.find(time_string,"/");
  local month=string.sub(time_string,0,i-1);
--print(month)
  time_string=string.sub(time_string,i+1,string.len(time_string));
  i=string.find(time_string,":");
  local year=string.sub(time_string,0,i-1);
--print(year)
  time_string=string.sub(time_string,i+1,string.len(time_string));
  i=string.find(time_string,":");
  local hour=string.sub(time_string,0,i-1);
--print(hour)
  time_string=string.sub(time_string,i+1,string.len(time_string));
  i=string.find(time_string,":");
  local min=string.sub(time_string,0,i-1);
--print(min)
  time_string=string.sub(time_string,i+1,string.len(time_string));
  local sec=time_string;
--print(sec)    
  local my_timestamp=timestamp(year,month,day,hour,min,sec);
 
  return my_timestamp; 
end

function get_url(sid)
  local t = io.popen(string.format("sed -n '/%s/p' %s| awk -F ']' 'NR==1{printf $4}'| awk -F '[' '{printf $2}'",sid,modsecurity_debug_path));
  local url = t:read("*all");
--print("url =",url);
  return url;
end

function get_unid(my_filename)
  local i=string.find(my_filename,"-");
  if(i==nil)
  then
        return nil;
  end
  local unid=string.sub(my_filename,i+1,string.len(my_filename));
--print("unid:",unid)
  i=string.find(unid,"-");
  unid=string.sub(unid,i+1,string.len(unid));
--print("unid:",unid)

  i=string.find(unid,"-");
  unid=string.sub(unid,1,i-1);
--print("unid:",unid)

  return unid;
end

function send_file(my_filename,time,url,filename)
  local handled_url = string.gsub(url,"/","\-")
  print("handled_url",handled_url);  
  local i = io.popen(string.format("mv %s%s %s%s__%s__%s",upload_file_path,my_filename,send_file_to_path,time,handled_url,filename));
  print(string.format("lua :::::: mv %s%s %s%s__%s__%s",upload_file_path,my_filename,send_file_to_path,time,handled_url,filename));
  return 0;
end

function main()
--local my_filename = "20161119-143243-AcFcASAcAcA8AcAfA2AcAcAc-file-mSHGR5";
  local my_filename = arg[1];
  if(arg[1]==nil)
  then
    print("<<<<<< error >>>>>> usage: lua read_uploadfile.lua $filename")
    return 0;
  end
  local F,err=io.open(string.format("%s%s",upload_file_path,my_filename),"r+");
  if(err~=nil)
  then
	print(err);
  return nil;
  end
--  get_sid(modsecurity_debug_path,my_filename);
  local sid = get_sid2(my_filename);
  local unid = get_unid(my_filename);
  if(unid==nil)
  then 
	print("<<<<<< error >>>>>> : can't find filename string in debuglog");
	return nil;
  end
  local log_time = get_time(unid);	
  local time =  change_time(log_time);
  if(time==nil)
  then
	print("can't find filename in debuglog")
	return nil;
  end
  local file_name =  get_filename(log_time,sid);
  local url = get_url(unid);  
  file_name = string.gsub(file_name," \\","\\\\");
print("log_time:",time);
print("url:",url);
print("file name:",file_name);
  local send_file = send_file(my_filename,time,url,file_name)  

  return 0;
end

main()
