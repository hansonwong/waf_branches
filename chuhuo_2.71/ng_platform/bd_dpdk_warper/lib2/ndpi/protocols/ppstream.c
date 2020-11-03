/*
 * ppstream.c
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


#include "ndpi_protocols.h"
#ifdef NDPI_PROTOCOL_PPSTREAM

static void ndpi_int_ppstream_add_connection(struct ndpi_detection_module_struct
											   *ndpi_struct, struct ndpi_flow_struct *flow)
{
  ndpi_set_detected_protocol(ndpi_struct, flow, NDPI_PROTOCOL_PPSTREAM, NDPI_PROTOCOL_UNKNOWN);
}

static int ndpi_search_ppstream_bybd(struct ndpi_detection_module_struct *ndpi_struct,
	                                           struct ndpi_flow_struct *flow)
{
	struct ndpi_packet_struct *packet = &flow->packet;
	struct IP_PORT_st *src, *dst;
	int ret;
	if(packet->iph == NULL) return 0;
	
	src = ndpi_lookup_ip_port(ndpi_struct,packet->iph->saddr,packet->udp->source,packet->iph->protocol);
	dst = ndpi_lookup_ip_port(ndpi_struct,packet->iph->daddr,packet->udp->dest,packet->iph->protocol);
	if(src != NULL && src->mark == NDPI_PROTOCOL_PPSTREAM){
		NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG, "found ppstream over tcp.\n");
		ndpi_int_ppstream_add_connection(ndpi_struct, flow);
		return 1;	
	}
	if(dst != NULL && dst->mark == NDPI_PROTOCOL_PPSTREAM){
		NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG, "found ppstream over tcp.\n");
		ndpi_int_ppstream_add_connection(ndpi_struct, flow);
		return 1;		
	}
	ret = 0;
	if(packet->payload_packet_len >= 10 &&
		packet->payload[1] == 0x80      &&
		flow->ppstream_request < 0xff){
		flow->ppstream_request++;
		ret = 1;
	}
	if(packet->payload_packet_len >= 256 &&
		packet->payload[1] == 0x84       &&
		flow->ppstream_response < 0xff){
		flow->ppstream_response++;
		ret = 1;
	}
	if(flow->ppstream_request>=2 && flow->ppstream_response>=2){
		NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG, "found ppstream over tcp.\n");
		ndpi_int_ppstream_add_connection(ndpi_struct, flow);
		if(src == NULL)
			src = ndpi_alloc_ip_port(ndpi_struct,packet->iph->saddr,packet->udp->source,packet->iph->protocol);
		if(dst == NULL)
			dst = ndpi_alloc_ip_port(ndpi_struct,packet->iph->daddr,packet->udp->dest,  packet->iph->protocol);
		src->mark = NDPI_PROTOCOL_PPSTREAM;
		dst->mark = NDPI_PROTOCOL_PPSTREAM;
		ret = 1;
	}
	return ret;
}


void ndpi_search_ppstream(struct ndpi_detection_module_struct
							*ndpi_struct, struct ndpi_flow_struct *flow)
{
	struct ndpi_packet_struct *packet = &flow->packet;
	

	// struct ndpi_id_struct *src=ndpi_struct->src;
	// struct ndpi_id_struct *dst=ndpi_struct->dst;



	/* check TCP Connections -> Videodata */
	if (packet->tcp != NULL) {
		if (packet->payload_packet_len >= 60 && get_u_int32_t(packet->payload, 52) == 0
			&& memcmp(packet->payload, "PSProtocol\x0", 11) == 0) {
			NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG, "found ppstream over tcp.\n");
			ndpi_int_ppstream_add_connection(ndpi_struct, flow);
			return;
		}
		if (packet->payload_packet_len > 100 &&
			memcmp(packet->payload, "GET /", 5) == 0) {
			ndpi_parse_packet_line_info(ndpi_struct, flow);
		
			if(packet->empty_line_position_set != 0 &&
			   packet->user_agent_line.ptr != NULL 	&&
			   packet->user_agent_line.len >= 16    &&
			   memcmp(packet->user_agent_line.ptr,"HCDNClient_WINPC",16) == 0){  
			    NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG, "found ppstream over tcp.\n");
			    ndpi_int_ppstream_add_connection(ndpi_struct, flow);
			}
		}
		return;

	}
	if (packet->udp != NULL) {
		if(ndpi_search_ppstream_bybd(ndpi_struct,flow)) return;
		
		if (packet->payload_packet_len > 2 && packet->payload[2] == 0x43
			&& ((packet->payload_packet_len - 4 == get_l16(packet->payload, 0))
				|| (packet->payload_packet_len == get_l16(packet->payload, 0))
				|| (packet->payload_packet_len >= 6 && packet->payload_packet_len - 6 == get_l16(packet->payload, 0)))) {
			flow->l4.udp.ppstream_stage++;
			if (flow->l4.udp.ppstream_stage == 5) {
				NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG,
						"found ppstream over udp pattern len, 43.\n");
				ndpi_int_ppstream_add_connection(ndpi_struct, flow);
				return;
			}
			return;
		}

		if (flow->l4.udp.ppstream_stage == 0
			&& packet->payload_packet_len > 4 && ((packet->payload_packet_len - 4 == get_l16(packet->payload, 0))
												  || (packet->payload_packet_len == get_l16(packet->payload, 0))
												  || (packet->payload_packet_len >= 6
													  && packet->payload_packet_len - 6 == get_l16(packet->payload,
																								   0)))) {

			if (packet->payload[2] == 0x00 && packet->payload[3] == 0x00 && packet->payload[4] == 0x03) {
				flow->l4.udp.ppstream_stage = 7;
				NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG, "need next packet I.\n");
				return;
			}
		}

		if (flow->l4.udp.ppstream_stage == 7
			&& packet->payload_packet_len > 4 && packet->payload[3] == 0x00
			&& ((packet->payload_packet_len - 4 == get_l16(packet->payload, 0))
				|| (packet->payload_packet_len == get_l16(packet->payload, 0))
				|| (packet->payload_packet_len >= 6 && packet->payload_packet_len - 6 == get_l16(packet->payload, 0)))
			&& (packet->payload[2] == 0x00 && packet->payload[4] == 0x03)) {
			NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG,
					"found ppstream over udp with pattern Vb.\n");
			ndpi_int_ppstream_add_connection(ndpi_struct, flow);
			return;
		}

	}
	
	NDPI_LOG(NDPI_PROTOCOL_PPSTREAM, ndpi_struct, NDPI_LOG_DEBUG, "exclude ppstream.\n");
	NDPI_ADD_PROTOCOL_TO_BITMASK(flow->excluded_protocol_bitmask, NDPI_PROTOCOL_PPSTREAM);
}


void init_ppstream_dissector(struct ndpi_detection_module_struct *ndpi_struct, u_int32_t *id, NDPI_PROTOCOL_BITMASK *detection_bitmask)
{
  ndpi_set_bitmask_protocol_detection("PPStream", ndpi_struct, detection_bitmask, *id,
				      NDPI_PROTOCOL_PPSTREAM,
				      ndpi_search_ppstream,
				      NDPI_SELECTION_BITMASK_PROTOCOL_V4_V6_TCP_OR_UDP_WITH_PAYLOAD_WITHOUT_RETRANSMISSION,
				      SAVE_DETECTION_BITMASK_AS_UNKNOWN,
				      ADD_TO_DETECTION_BITMASK);

  *id += 1;
}

#endif
