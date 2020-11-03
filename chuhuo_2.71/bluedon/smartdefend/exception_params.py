#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os


def deal_params(data):
    if not os.path.exists("/home/ng_platform/policyevolve/"):
            os.makedirs("/home/ng_platform/policyevolve/")
    if not os.path.exists("/etc/cron.d/exception_cron"):
        fp = open("/etc/cron.d/exception_cron", "w")
        fp.write("SHELL=/bin/sh\n")
        fp.write("PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n")
        fp.close()

    cmd_path = "/home/ng_platform/policyevolve/"

    # turn_sql = "select sValue from m_tbconfig where sName = 'AutorRuleExceptionTurn' "
    # result = execute_sql(turn_sql)[0]["sValue"]
    # result = json.loads(result)
    # on_off = int(result["iExceptionStrategyOn"])
    # 协议异常 data["iProtocolException"]
    # 阻断 data["iStop"]
    # 流量异常 data["iFlowException"]
    # 端口异常 data["iPortException"]

    item = []

    if str(data["iTrigerType"]) == '2':
        if str(data["iFlowException"]) == '1':
            traffic_on_data = cmd_path + "policy-ctl -T traffic up -i %s -t %s -m %s\n" % (data["iFlowTimeInterval"], \
                                                                                   data["iFlowThreshold"], \
                                                                                   data["iFlowThresholdNum"])
            traffic_down_data = cmd_path + "policy-ctl -T traffic down\n"
            traffic_start_time = data["sFlowTimeRangeStart"].split(":")
            # print "OOO:", int(traffic_start_time[0])
            traffic_start_time_hour = int(traffic_start_time[0])
            traffic_start_time_min = int(traffic_start_time[1])
            traffic_end_time = data["sFlowTimeRangeEnd"].split(":")
            traffic_end_time_hour = int(traffic_end_time[0])
            traffic_end_time_min = int(traffic_end_time[1])
            traffic_line = "%d %d * * * root %s" % (traffic_start_time_min, traffic_start_time_hour, traffic_on_data)
            traffic_line2 = "%d %d * * * root %s" % (traffic_end_time_min, traffic_end_time_hour, traffic_down_data)
            item.append(traffic_line)
            item.append(traffic_line2)

        if str(data["iProtocolException"]) == '1':
            protocol_on_data = cmd_path + "policy-ctl -T protocol up -i %s -t %s -m %s\n" % (data["iProtocolTimeInterval"], \
                                                                                     data["iProtocolThreshold"], \
                                                                                     data["iProtocolThresholdNum"])
            protocol_down_data = cmd_path + "policy-ctl -T protocol down\n"
            protocol_start_time = data["sProtocolTimeRangeStart"].split(":")
            protocol_start_time_hour = int(protocol_start_time[0])
            protocol_start_time_min = int(protocol_start_time[1])
            protocol_end_time = data["sProtocolTimeRangeEnd"].split(":")
            protocol_end_time_hour = int(protocol_end_time[0])
            protocol_end_time_min = int(protocol_end_time[1])
            protocol_line = "%d %d * * * root %s" % (protocol_start_time_min, protocol_start_time_hour, protocol_on_data)
            protocol_line2 = "%d %d * * * root %s" % (protocol_end_time_min, protocol_end_time_hour, protocol_down_data)
            item.append(protocol_line)
            item.append(protocol_line2)

        if str(data["iStop"]) == '1':
            os.system(cmd_path + "policy-ctl -S start -r %s" % data["iStopMinute"])

        else:
            os.system(cmd_path + "policy-ctl -S stop")

        if str(data["iPortException"]) == '1':
            ports = data["sPort"]
            port_down_data = cmd_path + "policy-ctl -T port down\n"
            port_start_time = data["sPortTimeRangeStart"].split(":")
            port_start_time_hour = int(port_start_time[0])
            port_start_time_min = int(port_start_time[1])
            port_end_time = data["sPortTimeRangeEnd"].split(":")
            port_end_time_hour = int(port_end_time[0])
            port_end_time_min = int(port_end_time[1])
            val = ""
            for i in range(len(ports)):
                val += "%s-%s," % (ports[i][0], ports[i][1])
            # port_on_more = cmd_path + "policy-ctl -A port -p %s\n" % val[0:-1]
            # port_line = "%d %d * * * root %s" % (port_start_time_min, port_start_time_hour, port_on_more)
            # item.append(port_line)
            port_on_data_two = cmd_path + "policy-ctl -T port up -p %s\n" % val[0:-1]
            port_line2 = "%d %d * * * root %s" % (port_start_time_min, port_start_time_hour, port_on_data_two)
            port_line3 = "%d %d * * * root %s" % (port_end_time_min, port_end_time_hour, port_down_data)
            item.append(port_line2)
            # item.append(port_line)
            item.append(port_line3)

        # os.system("killall nftse")
        # getLogger("main").info("nftse down")
    fp = open("/etc/cron.d/exception_cron", "r")
    lines = fp.readlines()
    fp.close()

    return item, lines


def add_params(data):
    items, lines = deal_params(data)
    for item in items:
        lines.append(item)

    with open("/etc/cron.d/exception_cron", "w") as fp:
        lines = "".join(lines)
        fp.write(lines)
    # print "OOOO"


def del_params(data):
    items, lines = deal_params(data)
    for item in items:
        if item in lines:
            lines.remove(item)

    with open("/etc/cron.d/exception_cron", "w") as fp:
        lines = "".join(lines)
        fp.write(lines)


if __name__ == "__main__":
    config_exception_params()