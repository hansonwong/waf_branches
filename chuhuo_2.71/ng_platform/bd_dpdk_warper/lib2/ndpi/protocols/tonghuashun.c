/*
 * tonghuashun.c
 *
 * Copyright (C) 2009-2011 by ipoque GmbH
 * Copyright (C) 2011-15 - ntop.org
 *
 * This file is part of nDPI, an open source deep packet inspection
 * library based on the OpenDPI and PACE technology by ipoque GmbH
 *
 * nDPI is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * nDPI is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with nDPI.  If not, see <http://www.gnu.org/licenses/>.
 * 
 */

//add by bluedon

#include "ndpi_protocols.h"

#ifdef NDPI_PROTOCOL_TONGHUASHUN

static void 
ndpi_int_tonghuashun_add_connection(struct ndpi_detection_module_struct *ndpi_struct,
                                                struct ndpi_flow_struct *flow)
{
	ndpi_set_detected_protocol(ndpi_struct, flow, NDPI_PROTOCOL_TONGHUASHUN, NDPI_PROTOCOL_UNKNOWN);
}

static void 
ndpi_check_tonghuashun_tcp(struct ndpi_detection_module_struct *ndpi_struct,
                                    struct ndpi_flow_struct *flow)
{
	struct ndpi_packet_struct *packet = &flow->packet;

	if (packet->payload_packet_len > 60){
		
		if(get_u_int32_t(packet->payload,0) == 0xfdfdfdfd &&
		   get_u_int32_t(packet->payload,4) == 0x30303030){
			goto checkok;
		}
		
		if(memcmp(packet->payload, "GET /", 5) == 0 ||
		   memcmp(packet->payload, "POST /", 6) == 0 ){

			ndpi_parse_packet_line_info(ndpi_struct, flow);

			if(packet->empty_line_position_set == 0) return;

			if(packet->referer_line.ptr != NULL &&
			   (strstr(packet->referer_line.ptr,"10jqka.") != NULL ||
			    strstr(packet->referer_line.ptr,"thsi.") != NULL)){
			    goto checkok;
			}
			if(packet->host_line.ptr != NULL &&
			   (strstr(packet->host_line.ptr,"10jqka.") != NULL ||
			    strstr(packet->host_line.ptr,"thsi.") != NULL)){
			    goto checkok;
			}	
		}
	}
	
	return;
	
checkok:
	NDPI_LOG(NDPI_PROTOCOL_TONGHUASHUN, ndpi_struct, NDPI_LOG_DEBUG, "found tonghuashun tcp.\n");
	ndpi_int_tonghuashun_add_connection(ndpi_struct, flow);
	return;
}

static void 
ndpi_check_tonghuashun_udp(struct ndpi_detection_module_struct *ndpi_struct,
                                     struct ndpi_flow_struct *flow)
{
	return;
}


void 
ndpi_search_tonghuashun(struct ndpi_detection_module_struct *ndpi_struct,
                                struct ndpi_flow_struct *flow)
{
	struct ndpi_packet_struct *packet = &flow->packet;

	if(packet->tcp != NULL)
	{
		ndpi_check_tonghuashun_tcp(ndpi_struct, flow);
	}
	else if(packet->udp != NULL)
	{
		ndpi_check_tonghuashun_udp(ndpi_struct, flow);
	}
}


void
init_tonghuashun_dissector(struct ndpi_detection_module_struct *ndpi_struct,
                                  u_int32_t *id, 
                                  NDPI_PROTOCOL_BITMASK *detection_bitmask)
{
	ndpi_set_bitmask_protocol_detection("tonghuashun",
		                                ndpi_struct,
		                                detection_bitmask,
		                                *id,
				      					NDPI_PROTOCOL_TONGHUASHUN,
				                        ndpi_search_tonghuashun,
				                        NDPI_SELECTION_BITMASK_PROTOCOL_TCP_OR_UDP_WITH_PAYLOAD_WITHOUT_RETRANSMISSION,
				                        SAVE_DETECTION_BITMASK_AS_UNKNOWN,
				                        ADD_TO_DETECTION_BITMASK);
	*id += 1;
}

#endif


