cmd_eal.o = gcc -Wp,-MD,./.eal.o.d.tmp -m64 -pthread  -march=native -DRTE_MACHINE_CPUFLAG_SSE -DRTE_MACHINE_CPUFLAG_SSE2 -DRTE_MACHINE_CPUFLAG_SSE3 -DRTE_MACHINE_CPUFLAG_SSSE3 -DRTE_MACHINE_CPUFLAG_SSE4_1 -DRTE_MACHINE_CPUFLAG_SSE4_2 -DRTE_MACHINE_CPUFLAG_AES -DRTE_MACHINE_CPUFLAG_PCLMULQDQ -DRTE_MACHINE_CPUFLAG_AVX -DRTE_COMPILE_TIME_CPUFLAGS=RTE_CPUFLAG_SSE,RTE_CPUFLAG_SSE2,RTE_CPUFLAG_SSE3,RTE_CPUFLAG_SSSE3,RTE_CPUFLAG_SSE4_1,RTE_CPUFLAG_SSE4_2,RTE_CPUFLAG_AES,RTE_CPUFLAG_PCLMULQDQ,RTE_CPUFLAG_AVX  -I/home/ng_platform/dpdk-1.8.0/x86_64-native-linuxapp-gcc/include -include /home/ng_platform/dpdk-1.8.0/x86_64-native-linuxapp-gcc/include/rte_config.h -I/home/ng_platform/dpdk-1.8.0/lib/librte_eal/linuxapp/eal/include -I/home/ng_platform/dpdk-1.8.0/lib/librte_eal/common -I/home/ng_platform/dpdk-1.8.0/lib/librte_eal/common/include -I/home/ng_platform/dpdk-1.8.0/lib/librte_ring -I/home/ng_platform/dpdk-1.8.0/lib/librte_mempool -I/home/ng_platform/dpdk-1.8.0/lib/librte_malloc -I/home/ng_platform/dpdk-1.8.0/lib/librte_ether -I/home/ng_platform/dpdk-1.8.0/lib/librte_ivshmem -I/home/ng_platform/dpdk-1.8.0/lib/librte_pmd_ring -I/home/ng_platform/dpdk-1.8.0/lib/librte_pmd_pcap -I/home/ng_platform/dpdk-1.8.0/lib/librte_pmd_af_packet -I/home/ng_platform/dpdk-1.8.0/lib/librte_pmd_xenvirt -W -Wall -Werror -Wstrict-prototypes -Wmissing-prototypes -Wmissing-declarations -Wold-style-definition -Wpointer-arith -Wcast-align -Wnested-externs -Wcast-qual -Wformat-nonliteral -Wformat-security -Wundef -Wwrite-strings -O3 -D_GNU_SOURCE  -o eal.o -c /home/ng_platform/dpdk-1.8.0/lib/librte_eal/linuxapp/eal/eal.c 