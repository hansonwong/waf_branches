/*
 * qqgame.c
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

#ifdef NDPI_PROTOCOL_QQGAME

static void 
ndpi_int_qqgame_add_connection(struct ndpi_detection_module_struct *ndpi_struct,
                                         struct ndpi_flow_struct *flow)
{
	ndpi_set_detected_protocol(ndpi_struct, flow, NDPI_PROTOCOL_QQGAME, NDPI_PROTOCOL_UNKNOWN);
}

static void 
ndpi_check_qqgame_tcp(struct ndpi_detection_module_struct *ndpi_struct,
                              struct ndpi_flow_struct *flow)
{
	struct ndpi_packet_struct *packet = &flow->packet;

	if (packet->payload_packet_len > 120){

		if(packet->payload[0] == 0x0 && 
		   packet->payload[2] == 0x2d &&
		   get_u_int32_t(packet->payload,3) == 0x0){
		    goto checkok;
		}
		
		if(memcmp(packet->payload, "GET /", 5) == 0){

			ndpi_parse_packet_line_info(ndpi_struct, flow);

			if(packet->empty_line_position_set == 0) return;
			
			if(packet->host_line.ptr != NULL &&
			    strstr(packet->host_line.ptr,"minigame.qq") != NULL){
			    goto checkok;
			}	

			if(packet->referer_line.ptr != NULL &&
			   (strstr(packet->referer_line.ptr,"minigame.qq") != NULL ||
			    strstr(packet->referer_line.ptr,"qqgameplatcdn.qq") != NULL)){
			    goto checkok;
			}

			if(packet->user_agent_line.ptr != NULL &&
			   packet->user_agent_line.len >= 7	 &&
		       memcmp(packet->user_agent_line.ptr,"QQGame",6) == 0){
		        goto checkok;
			}
			
		}
	}
	
	return;
	
checkok:
	NDPI_LOG(NDPI_PROTOCOL_QQGAME, ndpi_struct, NDPI_LOG_DEBUG, "found qq game tcp.\n");
	ndpi_int_qqgame_add_connection(ndpi_struct, flow);
	return;
}

static void 
ndpi_check_qqgame_udp(struct ndpi_detection_module_struct *ndpi_struct,
                               struct ndpi_flow_struct *flow)
{
	return;
}


void 
ndpi_search_qqgame(struct ndpi_detection_module_struct *ndpi_struct,
                          struct ndpi_flow_struct *flow)
{
	struct ndpi_packet_struct *packet = &flow->packet;

	if(packet->tcp != NULL)
	{
		ndpi_check_qqgame_tcp(ndpi_struct, flow);
	}
	else if(packet->udp != NULL)
	{
		ndpi_check_qqgame_udp(ndpi_struct, flow);
	}
}


void
init_qqgame_dissector(struct ndpi_detection_module_struct *ndpi_struct,
                            u_int32_t *id, 
                            NDPI_PROTOCOL_BITMASK *detection_bitmask)
{
	ndpi_set_bitmask_protocol_detection("qqgame",
		                                ndpi_struct,
		                                detection_bitmask,
		                                *id,
				      					NDPI_PROTOCOL_QQGAME,
				                        ndpi_search_qqgame,
				                        NDPI_SELECTION_BITMASK_PROTOCOL_TCP_OR_UDP_WITH_PAYLOAD_WITHOUT_RETRANSMISSION,
				                        SAVE_DETECTION_BITMASK_AS_UNKNOWN,
				                        ADD_TO_DETECTION_BITMASK);
	*id += 1;
}

#endif

