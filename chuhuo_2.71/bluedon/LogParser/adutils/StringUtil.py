# -*- coding:utf-8 -*-  

def subx(str, x, y):
	ret = None
	if x < 0: x = 0
	try:
		ret = str.decode('utf-8')[x:x + y].encode('utf-8')
	except Exception, e:
		try:
			ret = str.decode('gb2312')[x:x + y].encode('utf-8')
		except Exception, e:
			pass
		pass
	return ret

def get_content(str, offset, len):
	len2 = len / 2
	return subx(str, offset - len2, len)
	
	
#print get_content('a后b来c，d我e发f现g一h种i更j为5874023758934&*()&*()^&*%@&*#@)k简l单m的n方o法p', 18, 30)