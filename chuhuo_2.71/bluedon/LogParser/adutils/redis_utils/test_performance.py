#!/usr/bin/env python
# coding=utf-8

import sys
import redis
import time
from redis_config import *
from contextlib import contextmanager


# subscribe redis channel
@contextmanager
def subscribe_channel(redis_obj, chn):
    try:
        # setup
        ps = redis_obj.pubsub()
        ps.subscribe(chn)
        yield ps.listen()
    except (KeyboardInterrupt, RuntimeError) as e:
        print e
        print 'exit subscribe_channel'
    finally:
        # cleanup
        ps.unsubscribe(chn)


def publish_channel(redis_obj, chn, content):
    redis_obj.publish(chn, content)


def create_redis(host=HOST, port=PORT, db=DB):
    try:
        re = redis.Redis(host=host, port=port, db=db)
    except Exception as e:
        re = None
        print e
    return re

d = {"AppProto":"POP","Date":"2016-9-19 9:4:13",
     "SrcMac":"b8-88-e3-df-1d-87","SrcIP":"192.168.11.104",
     "SrcPort":"62690","DstMac":"0-10-f3-51-3e-a8",
     # "DstIP":"220.181.12.101","DstPort":"110",
     "DstIP":"108.61.214.131","DstPort":"110",
     "MailFrom":"'liukai_mr@163.com' <liukai_mr@163.com> ",
     "MailTo":"'18942557667@163.com' <18942557667@163.com> ",
     "MailCc":"'liukai_mr@126.com' <liukai_mr@126.com> ",
     "MailBcc":"","MailSubject":"绝密文档 邮件",
     "MailContent":"pop_content_1477558380609109.txt",
     "MailContentPath":'/var/log/suricata/content/',
     "MailAttach":"mail_test_attach01.txt,mail_test_attach02.txt",
     "MailAttachPath":'/home/cyren/checkfile/',
     "MailMatch":{"Sendbox": "","Recbox": "","Subject": "","Content": "","Filename": "#病毒","Virus": ""}}

f = {"AppProto": "FTP", "Date": "2016-9-13 19:28:27",
    "SrcMac": "74-d4-35-7a-f1-3f", "SrcIP": "172.16.3.141",
    "SrcPort": "52618","DstMac": "80-f6-2e-87-14-1f",
    # "DstIP": "220.181.124.36","DstPort": "80",
    "DstIP": "108.61.214.131","DstPort": "80",
    "Action": "STOR","Para": "/home/cyren/checkfile/1477995920-5237-ftp_132ftpsd.txt",
     "Display": "132ftpsd.txt"}

w = {
    "SrcIP":"172.16.3.141",
    "SrcPort":"52618",
    "SrcMac":"74-d4-35-7a-f1-3f",
    # "DstIP":"220.181.124.36",
    "DstIP":"108.61.214.131",
    "DstPort":"80",
    "DstMac":"80-f6-2e-87-14-1f",
    "AppProto":"HTTP",
    "Type":"search",
    "SiteName":"百度搜索",
    "Host":"baidu.com",   "Uri":"/s?wd=中国&rsv_spt=1&rsv_iqid=0xd5d5c1dc0000b7c0&issp=1&f=8&rsv_bp=0&rsv_idx=2&ie=utf-8&tn=baiduhome_pg&rsv_enter=1&rsv_sug3=4&rsv_sug1=4&rsv_sug7=100&rsv_t=2d43603JgfgVkvPtTiQEqIYr403xUajJeE4V5lO0Ihp62mzjncSUEMG%2F0GxvncYxpyUw&rsv_sug2=0&inputT=2798&rsv_sug4=2798",
    "Method":"POST",
    "Date":"2016-09-14 10:12:30",
    "Fields":[
            {"Field":"req_hdr_uri_param","Name":"kw","Value":"中国"}
        ]
}

s = {
    "AppProto":"DBAudit",
    "Date":"2016-09-14 10:12:30",
    "SrcMac":"74-d4-35-7a-f1-3f",
    "SrcIP":"172.16.3.141",
    "SrcPort":"52618",
    "DstMac":"80-f6-2e-87-14-1f",
    # "DstIP":"220.181.124.36",
    "DstIP":"108.61.214.131",
    "DstPort":"80",
    "Database":"OneOfActionList",
    "DbType":"Mysql",
    # "Sql":"select * from studentInfo\r\n"
    "Sql":"select value from v$sesstat where sid = :sid order by statistic#\n# Binds:1"
}

t = {
    "AppProto":"TELNET",
    "Date":"2016-10-19 15:36:13",
    "SrcMac":"74-27-ea-a8-f8-45",
    "SrcIP":"172.16.3.37",
    "SrcPort":"60300",
    "DstMac":"80-f6-2e-87-14-1f",
    "DstIP":"183.60.56.21",
    "DstPort":"23",
    "UserName":"",
    "PassWord":"",
    "Action":"logout",
    "FileName":"/var/log/suricata/telnet_files/2016/10/19/15/telnet_1476862426_140737197719218.txt"
}

w = {
    "AppProto":"HTTP",
    "SrcIP":"172.16.3.141","SrcPort":"49385","SrcMac":"74-d4-35-7a-f1-3f",
    # "DstIP":"220.181.15.150","DstPort":"80","DstMac":"80-f6-2e-87-14-1f",
    "DstIP":"108.61.214.131","DstPort":"80","DstMac":"80-f6-2e-87-14-1f",
    "Date":"2016-11-09 10:57:41","Type":"webmail","SiteName":"126webmail标准版",
    "Host":"mail.126.com","Uri":"/js6/s?sid=HBegLVaWfISfknwlPCWWepqYgqykTxyb&func=mbox:compose&deftabclick=t0&LeftNavGotoComposeClick=1&cl_compose=1&cl_send=1&l=compose&action=deliver",
    "Method":"POST",
    "Fields":[
        {"Field":"req_body","Name":"from","Value":"'longsy'&lt;longsy1986@126.com&gt;"},
        {"Field":"req_body","Name":"to","Value":"<string>'longsy1986@163.com'&lt;longsy1986@163.com&gt;</string>"},
        {"Field":"req_body","Name":"subject","Value":"test2"},
        {"Field":"req_body","Name":"content","Value":"&lt;div style='line-height:1.7;color:#000000;font-size:14px;font-family:Arial'&gt;test222222&lt;/div&gt;"}
    ],
    "Atts":[
        {"filename":"IPS测试问题-回复.txt","filesize":"1152","storepath":"/var/suricata/audit/http/20161109/2-1478660260844595"},
        {"filename":"1471828696.log.pcap","filesize":"14402","storepath":"/var/suricata/audit/http/20161109/3-1478660260845675"}
    ]

}

w = {
    "AppProto":"HTTP",
    "SrcIP":"172.16.3.141","SrcPort":"61358","SrcMac":"80-f6-2e-87-14-1f",
    "DstIP":"60.28.228.9","DstPort":"80","DstMac":"00-10-f3-51-40-3c",
    "Date":"2016-11-11 15:13:11","Type":"webmail","SiteName":"163webmail标准版",
    "Host":"m0.mail.sina.com.cn","Uri":"/classic/send.php?ts=1478848393671",
    "Method":"POST",
    "Fields":[
        {"Field":"req_body","Name":"from","Value":"longsy1986@163.com"},
        {"Field":"req_body","Name":"to","Value":"'e05620110' <e05620110@163.com>"},
        {"Field":"req_body","Name":"chao","Value":"'longsy1986' <longsy1986@163.com>, <string>'lb'&lt;e05620110@163.com&gt;</string>"},
        {"Field":"req_body","Name":"subject","Value":"testaaaaa"},
        {"Field":"req_body","Name":"content","Value":"&nbsp;aaaaaaaaaaaaa"}
    ],
    "Atts":[
        {"filename":"IPS测试问题-回复.txt","filesize":"1152","storepath":"/var/suricata/audit/http/20161111/9-1478848384120372.txt"},
        {"filename":"IPS测试问题-回复.txt","filesize":"1152","storepath":"/var/suricata/audit/http/20161111/10-1478848384127810.txt"},
        {"filename":"IPS测试问题-回复.txt","filesize":"1152","storepath":"/var/suricata/audit/http/20161111/11-1478848385847457.txt"}
    ]
}

w2 = {
    "AppProto":"HTTP",
    "SrcIP":"192.168.11.141","SrcPort":"61830","SrcMac":"74-d4-35-7a-f1-3f",
    "DstIP":"108.61.214.131","DstPort":"80","DstMac":"00-10-f3-51-3e-a8",
    "Date":"2016-11-09 10:52:00","Type":"httpurl","Host":"search.suning.com",
    "Uri":"/%E4%BD%A0%E5%A5%BD2/","Method":"GET","Title":"你好2_你好2推荐 - 苏宁易购"
}

w3 = {"AppProto":"HTTP",
      "SrcIP":"172.16.3.141","SrcPort":"61015","SrcMac":"74-d4-35-7a-f1-3f",
      # "DstIP":"180.97.36.26","DstPort":"80","DstMac":"80-f6-2e-87-14-1f",
      "DstIP":"108.61.214.131","DstPort":"80","DstMac":"80-f6-2e-87-14-1f",
      "Date":"2016-11-09 16:03:34","Type":"netstore","SiteName":"百度网盘上传",
      "Host":"c.pcs.baidu.com","Uri":"/rest/2.0/pcs/superfile2?method=upload&app_id=250528&channel=chunlei&clienttype=0&web=1&BDUSS=pansec_DCb740ccc5511e5e8fedcff06b081203-%2BxDr8nbsdcw954%2BO8r%2FHhBGS3Zri5wOqUE1IPx5rdzFh98LRLfYiAUDnnOuk7kTWxLpaviwnicftOhe%2BiJuZW%2F8dbP%2FL1c%2FF6mQF%2FoiiKUmZGt%2Fhhm6CynWpcd9O%2F8TOuNWcokV8QUmmiBgQ7k2rm%2FvmHHfjou8Xp9ZfNyyFrXGPCAajjZHXqwf1s%2FbwcpWF7zH1FhVeSVdw6koXuhONsrgU7vg%2FWx6zGqFMnytDFukZCFS2%2FJElOhv%2F0mlC9mwZGEZs%2FkE1lsKFf0qpj4lcnA%3D%3D&logid=MTQ3ODY2MDg3NjgxNjAuOTM1NjE4OTM1MTUyODg4Mw==&path=%2FRemapKey.zip&uploadid=N1-MTgzLjYyLjI1MS40NToxNDc4NjYxMjcyOjcyNzAyMTgwNjMzMzQ3NDQxMDI=&partseq=0",
      "Method":"POST",
      "Fields":[
          {"Field":"req_hdr_uri_param","Name":"filename","Value":"/RemapKey.zip"}
      ],
      "Atts":[
          {"filename":"RemapKey.zip","filesize":"165442","storepath":"/var/suricata/audit/http/20161109/0-1478678614518572"}]
}

w4 =  {
    "AppProto":"HTTP",
    "SrcIP":"172.16.2.180","SrcPort":"56532","SrcMac":"80-f6-2e-87-14-1f",
    "DstIP":"183.60.15.162","DstPort":"80","DstMac":"00-10-f3-51-40-3c",
    "Date":"2016-11-11 11:48:34","Type":"webmail","SiteName":"qqwebmail",
    "Host":"set1.mail.qq.com",
    "Uri":"/cgi-bin/compose_send?sid=a5nDScPxN1p-QDtj","Method":"POST",
    "Fields":[
        {"Field":"req_body","Name":"from","Value":"2070776562@qq.com"},
        {"Field":"req_body","Name":"to","Value":"'mailfotestt'<mailfotestt@21cn.com>"},
        {"Field":"req_body","Name":"subject","Value":" 30WebmailTest1148"},
        {"Field":"req_body","Name":"content","Value":"<div>asd </div><div>df</div><div>asd</div><div>fasd</div><div>fa</div><div>sdf</div><div>asd</div><div>fas</div><div>dg</div><div>a</div>"}
    ],
    # "Atts":[
    #     {"filename":"test--修改.log","filesize":"0","storepath":""}
    # ]
}

w4 = {"AppProto":"HTTP",
      "SrcIP":"172.16.3.141","SrcPort":"59324","SrcMac":"80-f6-2e-87-14-1f",
      "DstIP":"220.181.12.207","DstPort":"80","DstMac":"00-10-f3-51-40-3c",
      "Date":"2016-11-15 08:52:10","Type":"webmail","SiteName":"163网络邮箱标准版",
      "Host":"mail.163.com","Uri":"/js6/s?sid=MCffSlaCXfOnsaZDxFCCuHXrGuENOJaR&func=mbox:compose&cl_compose=1&cl_send=1&l=compose&action=deliver",
      "Method":"POST",
      "Fields":[
          {"Field":"req_body","Name":"from","Value":"'黎兵'&lt;longsy1986@163.com&gt;"},
          {"Field":"req_body","Name":"to","Value":"<string>'lb'&lt;e05620110@163.com&gt;</string>"},
          {"Field":"req_body","Name":"subject","Value":"aaaaaaaaa"},
          {"Field":"req_body","Name":"content","Value":"&lt;div style='line-height:1.7;color:#000000;font-size:14px;font-family:Arial'&gt;aaaaaaaaaaaaaaa&lt;/div&gt;"}
      ]
}

# weibo
w5 = {
    "AppProto":"HTTP",
    "SrcIP":"172.16.3.141","SrcPort":"63277","SrcMac":"80-f6-2e-87-14-1f",
    "DstIP":"180.149.134.141","DstPort":"80","DstMac":"00-10-f3-51-40-3c",
    "Date":"2016-11-11 16:39:33","Type":"weibo","SiteName":"新浪微博发文",
    "Host":"weibo.com","Uri":"/aj/mblog/add?ajwvr=6&__rnd=1478853575047",
    "Method":"POST",
    "Fields":[
        {"Field":"req_body","Name":"content","Value":"中文涉密;测试"},
        {"Field":"res_body","Name":"username","Value":"上帝放电"}
    ]
}

bd1 ={
        "AppProto":"bd-local-p2p",
        "Date":"2016-10-19 15:28:14",
        "SrcMac":"74-d4-35-7c-5b-00",
        "SrcIP":"172.16.5.66",
        "SrcPort":"61930",
        "DstMac":"80-f6-2e-87-14-1f",
        "DstIP":"180.169.18.135",
        "DstPort":"80",
        "Descr":"快车登陆 我们"
    }
qq1 = {
        "AppProto":"QQ",
        "Date":"2016-10-19 15:39:09",
        "SrcMac":"80-f6-2e-87-14-1f",
        "SrcIP":"172.16.3.37",
        "SrcPort":"4024",
        "DstMac":"00-21-45-c0-fa-02",
        "DstIP":"183.60.56.21",
        "DstPort":"8000",
        "SendID":"3329806272",
        "RecvID":"3500492811",
        "Action":"Get status of friend"
    }

all_msg = {
    'netlog_bd-local-p2p': {
        "AppProto":"bd-local-p2p",
        "Date":"2016-10-19 15:28:14",
        "SrcMac":"74-d4-35-7c-5b-00",
        "SrcIP":"172.16.5.66",
        "SrcPort":"61930",
        "DstMac":"80-f6-2e-87-14-1f",
        "DstIP":"180.169.18.135",
        "DstPort":"80",
        "Descr":"快车登陆 我们"
    },
    'netlog_bd-local-proxy': {
        "AppProto":"bd-local-proxy",
        "Date":"2016-10-19 15:29:49",
        "SrcMac":"74-d4-35-7c-5b-00",
        "SrcIP":"172.16.5.66",
        "SrcPort":"49687",
        "DstMac":"80-f6-2e-87-14-1f",
        "DstIP":"96.126.108.173",
        "DstPort":"80",
        "Descr":"CCProxy代理 点击"
    },
    'netlog_bd-local-game': {
        "AppProto":"bd-local-game",
        "Date":"2016-10-19 15:30:57",
        "SrcMac":"74-d4-35-7c-5b-00",
        "SrcIP":"172.16.5.66",
        "SrcPort":"51315",
        "DstMac":"80-f6-2e-87-14-1f",
        "DstIP":"101.227.5.27",
        "DstPort":"80",
        "Descr":"大天使之剑登陆-37游戏 我们"
    },
    'netlog_bd-local-trojan': {
        "AppProto":"bd-local-trojan",
        "Date":"2016-10-19 15:31:59",
        "SrcMac":"00-21-45-c0-fa-02",
        "SrcIP":"183.60.212.53",
        "SrcPort":"80",
        "DstMac":"80-f6-2e-87-14-1f",
        "DstIP":"172.16.7.207",
        "DstPort":"19980",
        "Descr":"发现木马：阿杰 2007表格文件管理程序操作"
    },
    'netlog_telnet': t,
    'netlog_qq': {
        "AppProto":"QQ",
        "Date":"2016-10-19 15:39:09",
        "SrcMac":"80-f6-2e-87-14-1f",
        "SrcIP":"172.16.3.37",
        "SrcPort":"4024",
        "DstMac":"00-21-45-c0-fa-02",
        "DstIP":"183.60.56.21",
        "DstPort":"8000",
        "SendID":"3329806272",
        "RecvID":"3500492811",
        "Action":"Get status of friend"
    },
    'netlog_email': d,
    'netlog_http': w,
    # 'netlog_http': {
    #     "AppProto":"HTTP",
    #     "SrcIP":"192.168.11.141",
    #     "SrcPort":"61786",
    #     "SrcMac":"74-d4-35-7a-f1-3f",
    #     "DstIP":"202.89.233.104",
    #     "DstPort":"80",
    #     "DstMac":"00-10-f3-51-3e-a8",
    #     "Date":"2016-10-11 13:26:42",
    #     "Type":"httpurl",
    #     "Host":"cn.bing.com",
    #     "Uri":"/fd/游戏/lsp.aspx",
    #     "Method":"POST"
    # },
    'netlog_ftp' : f,
    'netlog_sql_log': s

}


droplog = {
    "AppProto": "HTTP",
    "Date": "2016-11-18 16:24:47",
    "Type": "search",
    "SrcIP": "192.168.10.141",
    "SrcPort": "60432",
    "SrcMac": "74-d4-35-7a-f1-3f",
    "DstIP": "115.239.210.52",
    "DstPort": "80",
    "DstMac": "00-10-f3-51-3e-a8",
    "Host": "news.baidu.com",
    "Uri": "/ns?cl=2&rn=20&tn=news&word=%E4%BD%A0%E5%A5%BD",
    "Method": "GET",
    "SiteName": "百度搜索新闻",
    "Action": "drop"
}

if __name__ == '__main__':
    re = create_redis()
    if sys.argv[1] == 'sub':
        try:
            ch = sys.argv[2] or SUB_CHANNEL
            with subscribe_channel(re, ch) as sub:
                for i in sub:
                    print i
        except KeyboardInterrupt:
            print 'exit'
    elif sys.argv[1] == 'pub':
        # publish_channel(re, SUB_CHANNEL, 'aaa')
        with open('/usr/local/bluedon/tmp/LogParser/logs/mail.bcp.1473400424', 'r') as fp:
            l = fp.readline()
        CH = 'netlog_email'
        # publish_channel(re, SUB_CHANNEL, 'aaa')

        import json
        l = json.dumps(d)
        publish_channel(re, CH, l)

    elif sys.argv[1] == 'pubn':
        CH = 'netlog_email'
        import json
        d['Date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        l = json.dumps(d)
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count += 1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count > 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
    elif sys.argv[1] == 'pubw':
        CH = 'netlog_http'
        import json
        w4['Date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        l = json.dumps(w4)
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count += 1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count > 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
    elif sys.argv[1] == 'pubs':
        CH = 'netlog_sql_log'
        import json
        s['Date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        l = json.dumps(s)
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count += 1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count >= 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
    elif sys.argv[1] == 'pubf':
        CH = 'netlog_ftp'
        import json
        f['Date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        l = json.dumps(f)
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count +=1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count >= 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
    elif sys.argv[1] == 'puba':
        import json
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            for CH in all_msg:
                l = json.dumps(all_msg[CH])
                publish_channel(re, CH, l)
                count +=1
            time.sleep(0.0001)
            now_sec = time.time()
            if count >= 3:
            # if now_sec - start_sec > 5:
                break
        print 'endTime = %f' % now_sec
        print 'Used time = %f' % (now_sec - start_sec)
        print 'Send [%d] messages' % count
    elif sys.argv[1] == 'pubx':
        CH = 'netlog_qq'
        import json
        l = json.dumps(all_msg['netlog_qq'])
        print l
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count +=1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count >= 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
    elif sys.argv[1] == 'pubt':
        CH = 'netlog_telnet'
        import json
        t['Date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        l = json.dumps(t)
        print l
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count +=1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count >= 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
    elif sys.argv[1] == 'pubbd':
        CH = 'netlog_bd-local-p2p'
        import json
        bd1['Date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        l = json.dumps(bd1)
        print l
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count +=1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count >= 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
    elif sys.argv[1] == 'pubqq':
        CH = 'netlog_qq'
        import json
        qq1['Date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        l = json.dumps(qq1)
        print l
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count +=1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count >= 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
    elif sys.argv[1] == 'pubdrop':
        CH = 'netlog_match_http'
        import json
        droplog['Date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        l = json.dumps(droplog)
        print l
        count = 0
        start_sec = time.time()
        print 'startTime = %f' % start_sec
        while 1:
            publish_channel(re, CH, l)
            count +=1
            now_sec = time.time()
            # if now_sec - start_sec > 1:
            if count >= 3:
                print 'endTime = %f' % now_sec
                print 'Used time = %f' % (now_sec - start_sec)
                print 'Send [%d] messages' % count
                break
