cmd_i40e_hmc.o = gcc -Wp,-MD,./.i40e_hmc.o.d.tmp -m64 -pthread  -march=native -DRTE_MACHINE_CPUFLAG_SSE -DRTE_MACHINE_CPUFLAG_SSE2 -DRTE_MACHINE_CPUFLAG_SSE3 -DRTE_MACHINE_CPUFLAG_SSSE3 -DRTE_MACHINE_CPUFLAG_SSE4_1 -DRTE_MACHINE_CPUFLAG_SSE4_2 -DRTE_MACHINE_CPUFLAG_AES -DRTE_MACHINE_CPUFLAG_PCLMULQDQ -DRTE_MACHINE_CPUFLAG_AVX -DRTE_COMPILE_TIME_CPUFLAGS=RTE_CPUFLAG_SSE,RTE_CPUFLAG_SSE2,RTE_CPUFLAG_SSE3,RTE_CPUFLAG_SSSE3,RTE_CPUFLAG_SSE4_1,RTE_CPUFLAG_SSE4_2,RTE_CPUFLAG_AES,RTE_CPUFLAG_PCLMULQDQ,RTE_CPUFLAG_AVX  -I/home/ng_platform/dpdk-1.8.0/x86_64-native-linuxapp-gcc/include -include /home/ng_platform/dpdk-1.8.0/x86_64-native-linuxapp-gcc/include/rte_config.h -O3 -W -Wall -Werror -Wstrict-prototypes -Wmissing-prototypes -Wmissing-declarations -Wold-style-definition -Wpointer-arith -Wcast-align -Wnested-externs -Wcast-qual -Wformat-nonliteral -Wformat-security -Wundef -Wwrite-strings -Wno-sign-compare -Wno-unused-value -Wno-unused-parameter -Wno-strict-aliasing -Wno-format -Wno-missing-field-initializers -Wno-pointer-to-int-cast -Wno-format-nonliteral -Wno-format-security -Wno-unused-but-set-variable  -o i40e_hmc.o -c /home/ng_platform/dpdk-1.8.0/lib/librte_pmd_i40e/i40e/i40e_hmc.c 
