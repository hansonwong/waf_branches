#############################################################################
# Default syslog-ng.conf file which collects all local logs into a
# single file called /var/log/messages.
#

@version: 3.6
@include "scl.conf"

options {
    chain_hostnames(off);
    log_msg_size(81920);
    flush_lines(0);
    log_fifo_size(204800);
    time_reopen(10);
    use_dns(yes);
    dns_cache(yes);
    use_fqdn(yes);
    keep_hostname(yes);
    chain_hostnames(no);
    perm(0644);
    stats_freq(43200);
    create_dirs(yes);
};

source s_sys { file ("/proc/kmsg" program_override("kernel: ")); unix-stream ("/dev/log"); internal(); };
template t_syslog  { template("WAF $YEAR-$MONTH-$DAY $HOUR:$MIN:$SEC $HOST $PROGRAM [$LEVEL]: $MSG\n"); };
destination d_mesg { file("/var/log/messages" template(t_syslog)); };
destination d_auth { file("/var/log/secure" template(t_syslog)); };
destination d_mail { file("/var/log/maillog" template(t_syslog)); };
destination d_spol { file("/var/log/spooler" template(t_syslog)); };
destination d_boot { file("/var/log/boot.log" template(t_syslog)); };
destination d_cron { file("/var/log/cron" template(t_syslog)); };
destination d_ddos { file("/var/log/ddoslog" template(t_syslog)); };
destination d_webl { file("/var/log/weboutlog" template(t_syslog)); };
#filter f_filter1   { not (facility(mail) or facility(authpriv) or facility(cron)) and not message("Probable ddos") and not message("weboutlog"); };
filter f_filter1   { not (facility(mail) or message("Probable ddos") or message("weboutlog")); };
filter f_filter2   { facility(authpriv); };
filter f_filter3   { facility(mail); };
filter f_filter4   { facility(uucp) or (facility(news) and level(crit)); };
filter f_filter5   { facility(local7); };
filter f_filter6   { facility(cron); };
filter f_filter7   { message("Probable ddos"); };
filter f_filter8   { message("weboutlog"); };
log { source(s_sys); filter(f_filter1); destination(d_mesg); };
log { source(s_sys); filter(f_filter2); destination(d_auth); };
log { source(s_sys); filter(f_filter3); destination(d_mail); };
log { source(s_sys); filter(f_filter4); destination(d_spol); };
log { source(s_sys); filter(f_filter5); destination(d_boot); };
log { source(s_sys); filter(f_filter6); destination(d_cron); };
log { source(s_sys); filter(f_filter7); destination(d_ddos); };
log { source(s_sys); filter(f_filter8); destination(d_webl); };

template t_iptables-ng { template("$YEAR-$MONTH-$DAY:$HOUR:$MIN:$SEC $MSG\n"); };
destination d_iptables-ng { file("/var/log/fw/iptables-ng.log" template(t_iptables-ng)); };
filter f_iptables-ng { message("ipt_log") or message("ebt_log"); };
log { source(s_sys); filter(f_iptables-ng); destination(d_iptables-ng); };

{% for logs in ("logs_bridge", "logs_tproxy", "logs_porxy") %}
source   s_access_{{logs}}     { file("/usr/local/bdwaf/{{logs}}/access.log"); };
template t_access_{{logs}}     { template("$MSG\n"); };
destination d_access_{{logs}}  { file("/usr/local/bdwaf/{{logs}}/access/$MSGHDR/$YEAR$MONTH/access_$DAY.log" template(t_access_{{logs}})); };
log { source(s_access_{{logs}}); destination(d_access_{{logs}}); };

filter f_access_{{logs}} {match("GET ") or match("POST ") or match("HEAD"); };
template t_access2_{{logs}}     { template("WAF $YEAR-$MONTH-$DAY $HOUR:$MIN:$SEC $MSG\n"); };
destination d_access2_{{logs}}  { file("/usr/local/bdwaf/{{logs}}/syslog/access_syslog.log" template(t_access2_{{logs}})); };
log { source(s_access_{{logs}}); filter(f_access_{{logs}}); destination(d_access2_{{logs}}); };

source s_error_{{logs}} { file("/usr/local/bdwaf/{{logs}}/error.log"); };
filter f_error_{{logs}} { level(info..emerg)and match('ModSecurity'); };
template t_error_{{logs}}     { template("WAF $YEAR-$MONTH-$DAY  $MSG\n"); };
destination d_error_{{logs}}  { file("/usr/local/bdwaf/{{logs}}/syslog/error_syslog.log" template(t_error_{{logs}})); };
log { source(s_error_{{logs}}); filter(f_error_{{logs}}); destination(d_error_{{logs}}); };


{% endfor %}

source s_local {
    #system();
    #internal();
    file("/proc/kmsg");
};
#server log
source s_all {
    file("/var/log/apply_controls/app_mgt_.log");
    file("/var/log/bdwaf/logs/url_filter.log");
    file("/var/log/ddos/bd_ddos.log");
    file("/var/log/suricata/AvScan.log");
    file("/var/log/suricata/fast.log");
    file("/var/log/suricata/smtp.log");
    file("/var/log/fw/iptables-ng.log");
    # waf
    file("/var/log/messages");
    file("/usr/local/bdwaf/logs/syslog/access_syslog.log");
    file("/usr/local/bdwaf/logs/syslog/error_syslog.log");
};

source s_waf {
    file("/var/log/bdwaf/logs/error.log");
};

filter f_waf {  level(info..emerg)and match('ModSecurity'); };


source s_ipt {
    file("/proc/kmsg");
};

source s_network {
    udp();
};

destination d_local {
    file("/var/log/messages");
};

#server log
destination d_all {
{% for conf in syslog_conf %}
      {{ conf.proto }}("{{ conf.ip  }}" port({{ conf.port  }}));
{% endfor %}
};

#bd iptables log
#begin
#filter f_iptables { facility(kern) and message("ipt_log="); };
#destination d_iptables { file("/var/log/fw/iptables-ng.log"); };
#log { source(s_local); filter(f_iptables); destination(d_iptables); };
#end

#log {
#    source(s_local);

    # uncomment this line to open port 514 to receive messages
    #source(s_network);
#    destination(d_local);
#};

#server log
log { source(s_all); destination(d_all); };
log { source(s_waf); filter(f_waf); destination(d_all); };
