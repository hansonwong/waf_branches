
/*
 * Copyright (C) Igor Sysoev
 * Copyright (C) Nginx, Inc.
 */


#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>
#include <nginx.h>
#include "ngx_http_request.h"

//add by vincent
static ngx_int_t
ngx_http_send_special_error_page(ngx_http_request_t *r, u_char* pdata, size_t data_len);

static size_t
ngx_http_send_special_error_page_header_handler(u_char* p, size_t content_len);

//end add by vincent

static ngx_int_t ngx_http_send_error_page(ngx_http_request_t *r,
        ngx_http_err_page_t *err_page);
static ngx_int_t ngx_http_send_special_response(ngx_http_request_t *r,
        ngx_http_core_loc_conf_t *clcf, ngx_uint_t err);
static ngx_int_t ngx_http_send_refresh(ngx_http_request_t *r);


static u_char ngx_http_error_full_tail[] =
    "<hr><center>" NGINX_VER "</center>" CRLF
    "</body>" CRLF
    "</html>" CRLF
    ;


static u_char ngx_http_error_tail[] =
    "<hr><center>nginx</center>" CRLF
    "</body>" CRLF
    "</html>" CRLF
    ;


static u_char ngx_http_msie_padding[] =
    "<!-- a padding to disable MSIE and Chrome friendly error page -->" CRLF
    "<!-- a padding to disable MSIE and Chrome friendly error page -->" CRLF
    "<!-- a padding to disable MSIE and Chrome friendly error page -->" CRLF
    "<!-- a padding to disable MSIE and Chrome friendly error page -->" CRLF
    "<!-- a padding to disable MSIE and Chrome friendly error page -->" CRLF
    "<!-- a padding to disable MSIE and Chrome friendly error page -->" CRLF
    ;


static u_char ngx_http_msie_refresh_head[] =
    "<html><head><meta http-equiv=\"Refresh\" content=\"0; URL=";


static u_char ngx_http_msie_refresh_tail[] =
    "\"></head><body></body></html>" CRLF;


static char ngx_http_error_301_page[] =
    "<html>" CRLF
    "<head><title>301 Moved Permanently</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>301 Moved Permanently</h1></center>" CRLF
    ;


static char ngx_http_error_302_page[] =
    "<html>" CRLF
    "<head><title>302 Found</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>302 Found</h1></center>" CRLF
    ;


static char ngx_http_error_303_page[] =
    "<html>" CRLF
    "<head><title>303 See Other</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>303 See Other</h1></center>" CRLF
    ;


static char ngx_http_error_307_page[] =
    "<html>" CRLF
    "<head><title>307 Temporary Redirect</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>307 Temporary Redirect</h1></center>" CRLF
    ;


static char ngx_http_error_400_page[] =
    "<html>" CRLF
    "<head><title>400 Bad Request</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>400 Bad Request</h1></center>" CRLF
    ;


static char ngx_http_error_401_page[] =
    "<html>" CRLF
    "<head><title>401 Authorization Required</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>401 Authorization Required</h1></center>" CRLF
    ;


static char ngx_http_error_402_page[] =
    "<html>" CRLF
    "<head><title>402 Payment Required</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>402 Payment Required</h1></center>" CRLF
    ;


static char ngx_http_error_403_page[] =
    "<html>" CRLF
    "<head><title>403 Forbidden</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>403 Forbidden</h1></center>" CRLF
//add by vincent
    "<center><h2>Intercepted by bdwaf</h2></center>" CRLF
//end by vincent
    ;


static char ngx_http_error_404_page[] =
    "<html>" CRLF
    "<head><title>404 Not Found</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>404 Not Found</h1></center>" CRLF
    ;


static char ngx_http_error_405_page[] =
    "<html>" CRLF
    "<head><title>405 Not Allowed</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>405 Not Allowed</h1></center>" CRLF
    ;


static char ngx_http_error_406_page[] =
    "<html>" CRLF
    "<head><title>406 Not Acceptable</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>406 Not Acceptable</h1></center>" CRLF
    ;


static char ngx_http_error_408_page[] =
    "<html>" CRLF
    "<head><title>408 Request Time-out</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>408 Request Time-out</h1></center>" CRLF
    ;


static char ngx_http_error_409_page[] =
    "<html>" CRLF
    "<head><title>409 Conflict</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>409 Conflict</h1></center>" CRLF
    ;


static char ngx_http_error_410_page[] =
    "<html>" CRLF
    "<head><title>410 Gone</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>410 Gone</h1></center>" CRLF
    ;


static char ngx_http_error_411_page[] =
    "<html>" CRLF
    "<head><title>411 Length Required</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>411 Length Required</h1></center>" CRLF
    ;


static char ngx_http_error_412_page[] =
    "<html>" CRLF
    "<head><title>412 Precondition Failed</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>412 Precondition Failed</h1></center>" CRLF
    ;


static char ngx_http_error_413_page[] =
    "<html>" CRLF
    "<head><title>413 Request Entity Too Large</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>413 Request Entity Too Large</h1></center>" CRLF
    ;


static char ngx_http_error_414_page[] =
    "<html>" CRLF
    "<head><title>414 Request-URI Too Large</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>414 Request-URI Too Large</h1></center>" CRLF
    ;


static char ngx_http_error_415_page[] =
    "<html>" CRLF
    "<head><title>415 Unsupported Media Type</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>415 Unsupported Media Type</h1></center>" CRLF
    ;


static char ngx_http_error_416_page[] =
    "<html>" CRLF
    "<head><title>416 Requested Range Not Satisfiable</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>416 Requested Range Not Satisfiable</h1></center>" CRLF
    ;
//add by vincent
static char ngx_http_error_417_page[] =
    "<html>" CRLF
    "<head><title>417 Close links</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>417 Close links</h1></center>" CRLF
    "<center><h2>Intercepted by bdwaf</h2></center>" CRLF
    ;

static char ngx_http_error_418_page[] =
    "<html>" CRLF
    "<head><title>418 URL Violation</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>418 URL Violation</h1></center>" CRLF
    "<center><h2>Filtered By The Bdwaf</h2></center>" CRLF
    ;

//end add

static char ngx_http_error_494_page[] =
    "<html>" CRLF
    "<head><title>400 Request Header Or Cookie Too Large</title></head>"
    CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>400 Bad Request</h1></center>" CRLF
    "<center>Request Header Or Cookie Too Large</center>" CRLF
    ;


static char ngx_http_error_495_page[] =
    "<html>" CRLF
    "<head><title>400 The SSL certificate error</title></head>"
    CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>400 Bad Request</h1></center>" CRLF
    "<center>The SSL certificate error</center>" CRLF
    ;


static char ngx_http_error_496_page[] =
    "<html>" CRLF
    "<head><title>400 No required SSL certificate was sent</title></head>"
    CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>400 Bad Request</h1></center>" CRLF
    "<center>No required SSL certificate was sent</center>" CRLF
    ;


static char ngx_http_error_497_page[] =
    "<html>" CRLF
    "<head><title>400 The plain HTTP request was sent to HTTPS port</title></head>"
    CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>400 Bad Request</h1></center>" CRLF
    "<center>The plain HTTP request was sent to HTTPS port</center>" CRLF
    ;


static char ngx_http_error_500_page[] =
    "<html>" CRLF
    "<head><title>500 Internal Server Error</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>500 Internal Server Error</h1></center>" CRLF
    ;


static char ngx_http_error_501_page[] =
    "<html>" CRLF
    "<head><title>501 Not Implemented</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>501 Not Implemented</h1></center>" CRLF
    ;


static char ngx_http_error_502_page[] =
    "<html>" CRLF
    "<head><title>502 Bad Gateway</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>502 Bad Gateway</h1></center>" CRLF
    ;


static char ngx_http_error_503_page[] =
    "<html>" CRLF
    "<head><title>503 Service Temporarily Unavailable</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>503 Service Temporarily Unavailable</h1></center>" CRLF
    ;


static char ngx_http_error_504_page[] =
    "<html>" CRLF
    "<head><title>504 Gateway Time-out</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>504 Gateway Time-out</h1></center>" CRLF
    ;


static char ngx_http_error_507_page[] =
    "<html>" CRLF
    "<head><title>507 Insufficient Storage</title></head>" CRLF
    "<body bgcolor=\"white\">" CRLF
    "<center><h1>507 Insufficient Storage</h1></center>" CRLF
    ;


static ngx_str_t ngx_http_error_pages[] = {

    ngx_null_string,                     /* 201, 204 */

#define NGX_HTTP_LAST_2XX  202
#define NGX_HTTP_OFF_3XX   (NGX_HTTP_LAST_2XX - 201)

    /* ngx_null_string, */               /* 300 */
    ngx_string(ngx_http_error_301_page),
    ngx_string(ngx_http_error_302_page),
    ngx_string(ngx_http_error_303_page),
    ngx_null_string,                     /* 304 */
    ngx_null_string,                     /* 305 */
    ngx_null_string,                     /* 306 */
    ngx_string(ngx_http_error_307_page),

#define NGX_HTTP_LAST_3XX  308
#define NGX_HTTP_OFF_4XX   (NGX_HTTP_LAST_3XX - 301 + NGX_HTTP_OFF_3XX)

    ngx_string(ngx_http_error_400_page),
    ngx_string(ngx_http_error_401_page),
    ngx_string(ngx_http_error_402_page),
    ngx_string(ngx_http_error_403_page),
    ngx_string(ngx_http_error_404_page),
    ngx_string(ngx_http_error_405_page),
    ngx_string(ngx_http_error_406_page),
    ngx_null_string,                     /* 407 */
    ngx_string(ngx_http_error_408_page),
    ngx_string(ngx_http_error_409_page),
    ngx_string(ngx_http_error_410_page),
    ngx_string(ngx_http_error_411_page),
    ngx_string(ngx_http_error_412_page),
    ngx_string(ngx_http_error_413_page),
    ngx_string(ngx_http_error_414_page),
    ngx_string(ngx_http_error_415_page),
    ngx_string(ngx_http_error_416_page),
	//add by vincent
	ngx_string(ngx_http_error_417_page),
	ngx_string(ngx_http_error_418_page),	
#define NGX_HTTP_LAST_4XX  419
	//end add by vincent
	
#define NGX_HTTP_OFF_5XX   (NGX_HTTP_LAST_4XX - 400 + NGX_HTTP_OFF_4XX)

    ngx_string(ngx_http_error_494_page), /* 494, request header too large */
    ngx_string(ngx_http_error_495_page), /* 495, https certificate error */
    ngx_string(ngx_http_error_496_page), /* 496, https no certificate */
    ngx_string(ngx_http_error_497_page), /* 497, http to https */
    ngx_string(ngx_http_error_404_page), /* 498, canceled */
    ngx_null_string,                     /* 499, client has closed connection */

    ngx_string(ngx_http_error_500_page),
    ngx_string(ngx_http_error_501_page),
    ngx_string(ngx_http_error_502_page),
    ngx_string(ngx_http_error_503_page),
    ngx_string(ngx_http_error_504_page),
    ngx_null_string,                     /* 505 */
    ngx_null_string,                     /* 506 */
    ngx_string(ngx_http_error_507_page)

#define NGX_HTTP_LAST_5XX  508

};


static ngx_str_t  ngx_http_get_name = { 3, (u_char *) "GET " };


ngx_int_t
ngx_http_special_response_handler(ngx_http_request_t *r, ngx_int_t error)
{
    ngx_uint_t                 i, err;
    ngx_http_err_page_t       *err_page;
    ngx_http_core_loc_conf_t  *clcf;

    ngx_log_debug3(NGX_LOG_DEBUG_HTTP, r->connection->log, 0,
                   "http special response: %d, \"%V?%V\"",
                   error, &r->uri, &r->args);

    r->err_status = error;
    //add by vincent
    if(error == 403){
	r->connection->is_forbidden = 1;
    }
    //end 

    if (r->keepalive) {
        switch (error) {
        case NGX_HTTP_BAD_REQUEST:
        case NGX_HTTP_REQUEST_ENTITY_TOO_LARGE:
        case NGX_HTTP_REQUEST_URI_TOO_LARGE:
        case NGX_HTTP_TO_HTTPS:
        case NGX_HTTPS_CERT_ERROR:
        case NGX_HTTPS_NO_CERT:
        case NGX_HTTP_INTERNAL_SERVER_ERROR:
        case NGX_HTTP_NOT_IMPLEMENTED:
            r->keepalive = 0;
        }
    }

    if (r->lingering_close) {
        switch (error) {
        case NGX_HTTP_BAD_REQUEST:
        case NGX_HTTP_TO_HTTPS:
        case NGX_HTTPS_CERT_ERROR:
        case NGX_HTTPS_NO_CERT:
            r->lingering_close = 0;
        }
    }

    r->headers_out.content_type.len = 0;

    clcf = ngx_http_get_module_loc_conf(r, ngx_http_core_module);

    if (!r->error_page && clcf->error_pages && r->uri_changes != 0) {

        if (clcf->recursive_error_pages == 0) {
            r->error_page = 1;
        }

        err_page = clcf->error_pages->elts;

        for (i = 0; i < clcf->error_pages->nelts; i++) {
            if (err_page[i].status == error) {
                return ngx_http_send_error_page(r, &err_page[i]);
            }
        }
    }

    r->expect_tested = 1;

    if (ngx_http_discard_request_body(r) != NGX_OK) {
        r->keepalive = 0;
    }

    if (clcf->msie_refresh
            && r->headers_in.msie
            && (error == NGX_HTTP_MOVED_PERMANENTLY
                || error == NGX_HTTP_MOVED_TEMPORARILY))
    {
        return ngx_http_send_refresh(r);
    }

    if (error == NGX_HTTP_CREATED) {
        /* 201 */
        err = 0;

    } else if (error == NGX_HTTP_NO_CONTENT) {
        /* 204 */
        err = 0;

    } else if (error >= NGX_HTTP_MOVED_PERMANENTLY
               && error < NGX_HTTP_LAST_3XX)
    {
        /* 3XX */
        err = error - NGX_HTTP_MOVED_PERMANENTLY + NGX_HTTP_OFF_3XX;

    } else if (error >= NGX_HTTP_BAD_REQUEST
               && error < NGX_HTTP_LAST_4XX)
    {
        /* 4XX */
        err = error - NGX_HTTP_BAD_REQUEST + NGX_HTTP_OFF_4XX;

    } else if (error >= NGX_HTTP_NGINX_CODES
               && error < NGX_HTTP_LAST_5XX)
    {
        /* 49X, 5XX */
        err = error - NGX_HTTP_NGINX_CODES + NGX_HTTP_OFF_5XX;
        switch (error) {
        case NGX_HTTP_TO_HTTPS:
        case NGX_HTTPS_CERT_ERROR:
        case NGX_HTTPS_NO_CERT:
        case NGX_HTTP_REQUEST_HEADER_TOO_LARGE:
            r->err_status = NGX_HTTP_BAD_REQUEST;
            break;
        }

    } else {
        /* unknown code, zero body */
        err = 0;
    }

    return ngx_http_send_special_response(r, clcf, err);
}


ngx_int_t
ngx_http_filter_finalize_request(ngx_http_request_t *r, ngx_module_t *m,
                                 ngx_int_t error)
{
    void       *ctx;
    ngx_int_t   rc;

    ngx_http_clean_header(r);

    ctx = NULL;

    if (m) {
        ctx = r->ctx[m->ctx_index];
    }

    /* clear the modules contexts */
    ngx_memzero(r->ctx, sizeof(void *) * ngx_http_max_module);

    if (m) {
        r->ctx[m->ctx_index] = ctx;
    }

    r->filter_finalize = 1;

    rc = ngx_http_special_response_handler(r, error);

    /* NGX_ERROR resets any pending data */

    switch (rc) {

    case NGX_OK:
    case NGX_DONE:
        return NGX_ERROR;

    default:
        return rc;
    }
}


void
ngx_http_clean_header(ngx_http_request_t *r)
{
    ngx_memzero(&r->headers_out.status,
                sizeof(ngx_http_headers_out_t)
                - offsetof(ngx_http_headers_out_t, status));

    r->headers_out.headers.part.nelts = 0;
    r->headers_out.headers.part.next = NULL;
    r->headers_out.headers.last = &r->headers_out.headers.part;

    r->headers_out.content_length_n = -1;
    r->headers_out.last_modified_time = -1;
}


static ngx_int_t
ngx_http_send_error_page(ngx_http_request_t *r, ngx_http_err_page_t *err_page)
{
    ngx_int_t                  overwrite;
    ngx_str_t                  uri, args;
    ngx_table_elt_t           *location;
    ngx_http_core_loc_conf_t  *clcf;

    overwrite = err_page->overwrite;

    if (overwrite && overwrite != NGX_HTTP_OK) {
        r->expect_tested = 1;
    }

    if (overwrite >= 0) {
        r->err_status = overwrite;
    }

    if (ngx_http_complex_value(r, &err_page->value, &uri) != NGX_OK) {
        return NGX_ERROR;
    }

    if (uri.data[0] == '/') {

        if (err_page->value.lengths) {
            ngx_http_split_args(r, &uri, &args);

        } else {
            args = err_page->args;
        }

        if (r->method != NGX_HTTP_HEAD) {
            r->method = NGX_HTTP_GET;
            r->method_name = ngx_http_get_name;
        }

        return ngx_http_internal_redirect(r, &uri, &args);
    }

    if (uri.data[0] == '@') {
        return ngx_http_named_location(r, &uri);
    }

    location = ngx_list_push(&r->headers_out.headers);

    if (location == NULL) {
        return NGX_ERROR;
    }

    if (overwrite != NGX_HTTP_MOVED_PERMANENTLY
            && overwrite != NGX_HTTP_MOVED_TEMPORARILY
            && overwrite != NGX_HTTP_SEE_OTHER
            && overwrite != NGX_HTTP_TEMPORARY_REDIRECT)
    {
        r->err_status = NGX_HTTP_MOVED_TEMPORARILY;
    }

    location->hash = 1;
    ngx_str_set(&location->key, "Location");
    location->value = uri;

    ngx_http_clear_location(r);

    r->headers_out.location = location;

    clcf = ngx_http_get_module_loc_conf(r, ngx_http_core_module);

    if (clcf->msie_refresh && r->headers_in.msie) {
        return ngx_http_send_refresh(r);
    }

    return ngx_http_send_special_response(r, clcf, r->err_status
                                          - NGX_HTTP_MOVED_PERMANENTLY
                                          + NGX_HTTP_OFF_3XX);
}


static ngx_int_t
ngx_http_send_special_response(ngx_http_request_t *r,
                               ngx_http_core_loc_conf_t *clcf, ngx_uint_t err)
{
    u_char       *tail;
    size_t        len;
    ngx_int_t     rc;
    ngx_buf_t    *b;
    ngx_uint_t    msie_padding;
    ngx_chain_t   out[3];
    //add by vincent
    u_char       p[2048];
    size_t header_len;
    //end add by vincent


    if (clcf->server_tokens) {
        len = sizeof(ngx_http_error_full_tail) - 1;
        tail = ngx_http_error_full_tail;

    } else {
        len = sizeof(ngx_http_error_tail) - 1;
        tail = ngx_http_error_tail;
    }

    msie_padding = 0;

    if (ngx_http_error_pages[err].len) {
        r->headers_out.content_length_n = ngx_http_error_pages[err].len + len;
        if (clcf->msie_padding
                && (r->headers_in.msie || r->headers_in.chrome)
                && r->http_version >= NGX_HTTP_VERSION_10
                && err >= NGX_HTTP_OFF_4XX)
        {
            r->headers_out.content_length_n +=
                sizeof(ngx_http_msie_padding) - 1;
            msie_padding = 1;
        }

        r->headers_out.content_type_len = sizeof("text/html") - 1;
        ngx_str_set(&r->headers_out.content_type, "text/html");
        r->headers_out.content_type_lowcase = NULL;

    } else {
        r->headers_out.content_length_n = 0;
    }

    if (r->headers_out.content_length) {
        r->headers_out.content_length->hash = 0;
        r->headers_out.content_length = NULL;
    }

    ngx_http_clear_accept_ranges(r);
    ngx_http_clear_last_modified(r);
    ngx_http_clear_etag(r);

    rc = ngx_http_send_header(r);

    if (rc == NGX_ERROR || r->header_only) {
        return rc;
    }

    if (ngx_http_error_pages[err].len == 0) {
        return ngx_http_send_special(r, NGX_HTTP_LAST);
    }

    b = ngx_calloc_buf(r->pool);
    if (b == NULL) {
        return NGX_ERROR;
    }

    b->memory = 1;
    b->pos = ngx_http_error_pages[err].data;
    b->last = ngx_http_error_pages[err].data + ngx_http_error_pages[err].len;

    out[0].buf = b;
    out[0].next = &out[1];

    b = ngx_calloc_buf(r->pool);
    if (b == NULL) {
        return NGX_ERROR;
    }

    b->memory = 1;

    b->pos = tail;
    b->last = tail + len;

    out[1].buf = b;
    out[1].next = NULL;

    if (msie_padding) {
        b = ngx_calloc_buf(r->pool);
        if (b == NULL) {
            return NGX_ERROR;
        }

        b->memory = 1;
        b->pos = ngx_http_msie_padding;
        b->last = ngx_http_msie_padding + sizeof(ngx_http_msie_padding) - 1;

        out[1].next = &out[2];
        out[2].buf = b;
        out[2].next = NULL;
    }

    if (r == r->main) {
        b->last_buf = 1;
    }

    b->last_in_chain = 1;

    //add by vincent
    if ((r->connection->url_filtered)||(r->connection->is_forbidden)){
		int len;
		//p = (u_char *)ngx_calloc(1024, r->connection->log);
		//if (p == NULL)
		//	return NGX_ERROR;
		ngx_memzero(p,sizeof(p));
		if(r->connection->is_forbidden){
			r->connection->is_forbidden = 0;
			//if connection status is closed,then return 417 close link error page ,else return 403 forbidden error page  
			if(r->connection->error){
				err = err + 14;
			}
		}
		if(r->connection->url_filtered ==1){
			r->connection->url_filtered = 0;
			ngx_log_debug0(NGX_LOG_DEBUG_HTTP, r->connection->log, 0,
						   "[Error Page]URL filter page!");
			char url_cat_info[128];
			char info_line[]="<center><p>___________________________________________________________________________________________</p></center> \r\n";
			sprintf(url_cat_info,"<center><p>URL Filter Category:%s</p></center> \r\n",r->connection->url_category);
			len = ngx_http_error_pages[err].len + ngx_strlen(url_cat_info)+ ngx_strlen(info_line);
			header_len = ngx_http_send_special_error_page_header_handler(p,len);
			ngx_memcpy(p + header_len, ngx_http_error_pages[err].data, ngx_http_error_pages[err].len);
			len = header_len + ngx_http_error_pages[err].len;
			ngx_memcpy(p + len,info_line,ngx_strlen(info_line));
			len += ngx_strlen(info_line);
			ngx_memcpy(p + len,url_cat_info,ngx_strlen(url_cat_info));
			len += ngx_strlen(url_cat_info);
		}else{
	        header_len = ngx_http_send_special_error_page_header_handler(p, ngx_http_error_pages[err].len);
	        ngx_memcpy(p + header_len, ngx_http_error_pages[err].data, ngx_http_error_pages[err].len);
			len = header_len + ngx_http_error_pages[err].len;
		}
		p[len] = CR;
        p[len + 1] = LF;
		//ss_print(p,len+2);
        ngx_log_debug0(NGX_LOG_DEBUG_HTTP, r->connection->log, 0,
                       "[waf]send response error page packet to the dpdk!");
        return ngx_http_send_special_error_page(r, p, len+2);
    }
    else
        // end add
        return ngx_http_output_filter(r, &out[0]);
}


static ngx_int_t
ngx_http_send_refresh(ngx_http_request_t *r)
{
    u_char       *p, *location;
    size_t        len, size;
    uintptr_t     escape;
    ngx_int_t     rc;
    ngx_buf_t    *b;
    ngx_chain_t   out;

    len = r->headers_out.location->value.len;
    location = r->headers_out.location->value.data;

    escape = 2 * ngx_escape_uri(NULL, location, len, NGX_ESCAPE_REFRESH);

    size = sizeof(ngx_http_msie_refresh_head) - 1
           + escape + len
           + sizeof(ngx_http_msie_refresh_tail) - 1;

    r->err_status = NGX_HTTP_OK;

    r->headers_out.content_type_len = sizeof("text/html") - 1;
    ngx_str_set(&r->headers_out.content_type, "text/html");
    r->headers_out.content_type_lowcase = NULL;

    r->headers_out.location->hash = 0;
    r->headers_out.location = NULL;

    r->headers_out.content_length_n = size;

    if (r->headers_out.content_length) {
        r->headers_out.content_length->hash = 0;
        r->headers_out.content_length = NULL;
    }

    ngx_http_clear_accept_ranges(r);
    ngx_http_clear_last_modified(r);
    ngx_http_clear_etag(r);

    rc = ngx_http_send_header(r);

    if (rc == NGX_ERROR || r->header_only) {
        return rc;
    }

    b = ngx_create_temp_buf(r->pool, size);
    if (b == NULL) {
        return NGX_ERROR;
    }

    p = ngx_cpymem(b->pos, ngx_http_msie_refresh_head,
                   sizeof(ngx_http_msie_refresh_head) - 1);

    if (escape == 0) {
        p = ngx_cpymem(p, location, len);

    } else {
        p = (u_char *) ngx_escape_uri(p, location, len, NGX_ESCAPE_REFRESH);
    }

    b->last = ngx_cpymem(p, ngx_http_msie_refresh_tail,
                         sizeof(ngx_http_msie_refresh_tail) - 1);

    b->last_buf = 1;
    b->last_in_chain = 1;

    out.buf = b;
    out.next = NULL;

    return ngx_http_output_filter(r, &out);
}


//add by vincent
#define RESTRUCT_HEADER(pStr)   len = strlen(pStr);\
							    ngx_memcpy(p, pStr, len);\
							    p += len;\
							    *p++ = CR;\
							    *p++ = LF;

//restruct the error page response header
static size_t
ngx_http_send_special_error_page_header_handler(u_char* p, size_t content_len)
{
    size_t len = 0;
    u_char* pdata;
    char str[50],*pStr;

    pdata = p;
    pStr = str;

    strcpy(pStr,"HTTP/1.1 403 Forbidden");     
  	RESTRUCT_HEADER(pStr);

    strcpy(pStr,"Expires: ");
    len = strlen(pStr);
    ngx_memcpy(p, pStr, len);
    p += len;
    ngx_memcpy(p, ngx_cached_http_time.data, ngx_cached_http_time.len);
    p += ngx_cached_http_time.len;
    *p++ = CR;
    *p++ = LF;

    strcpy(pStr,"Server: bdwaf");
	RESTRUCT_HEADER(pStr);
	
    strcpy(pStr,"Content-Type: text/html;charset=utf-8");
	RESTRUCT_HEADER(pStr);
	
    memset(str, 0, sizeof(str));
    sprintf(str, "Content-Length: %ud", (uint32_t)content_len);
    ngx_memcpy(p, str, strlen(str));
    p += strlen(str) - 1;
    *p++ = CR;
    *p++ = LF;

    strcpy(pStr,"Connection: keep-alive");
	RESTRUCT_HEADER(pStr);

    *p++ = CR;
    *p++ = LF;

    len = p - pdata;

    return len;
}


//restruct error page response packet 
static ngx_int_t
ngx_http_send_special_error_page(ngx_http_request_t *r, u_char* pdata, size_t data_len)
{
    unsigned char       *pmdata;
    ngx_connection_t    *c;
    struct ether_addr   mac_addr;
    size_t              len;
    struct pseudo_header psd_header;
    uint32_t eth_crc32, i, ip_addr, tmp,vlan_len,ether_len;
    unsigned short      port;
    u_char p[2048];
    u_char p_tmp_buf[2048];

    c = r->connection;
    len = c->dd.m->data_len;

	//calculate the length of vlan tag 
	vlan_len = 4*c->vlan_level;
	ether_len = vlan_len + sizeof(struct ether_hdr);
		
    // p = (unsigned char *)ngx_calloc(2048, c->log);
    //if (p == NULL)
    //    return NGX_ERROR;
    //p_tmp_buf = (unsigned char *)ngx_calloc(2048, c->log);
    //if (p_tmp_buf == NULL)
    //    return NGX_ERROR;

    pmdata = rte_pktmbuf_mtod(c->dd.m, unsigned char *);
    ngx_memset(p, 0, 2048);
    ngx_memcpy(p, pmdata, ether_len + sizeof(struct iphdr) + sizeof(struct tcphdr));

    struct ether_hdr *ethhdrp = (struct ether_hdr * )p;
    struct iphdr *iphdrp = (struct iphdr *) (p + ether_len);
    struct tcphdr *tcphdrp = (struct tcphdr *)(p + ether_len + sizeof(struct iphdr));
    int iph_len = iphdrp->ihl << 2;   // ip header len
    int tcph_len = tcphdrp->doff << 2;

    //modify 6 byte mac address

    for (i = 0; i < 6; i++)
    {
        mac_addr.addr_bytes[i] = ethhdrp->d_addr.addr_bytes[i];
        ethhdrp->d_addr.addr_bytes[i] = ethhdrp->s_addr.addr_bytes[i];
        ethhdrp->s_addr.addr_bytes[i] = mac_addr.addr_bytes[i];
    }

    //modify the total length of ip packet 
    int ip_tot_len = iph_len + tcph_len + data_len;
    tmp = tcphdrp->ack_seq;
    tcphdrp->ack_seq = htonl(ntohl(tcphdrp->seq) + ntohs(iphdrp->tot_len) - tcph_len - iph_len);
    ngx_log_debug3(NGX_LOG_DEBUG_HTTP, r->connection->log, 0, "[waf]seq=%d,old_tot_len=%d,ack_seq=%d", ntohs(tcphdrp->seq), ntohs(iphdrp->tot_len), tcphdrp->ack_seq);
    tcphdrp->seq = tmp;
    tcphdrp->ack = 1;
	
    //modify the port
    port = tcphdrp->source;
    tcphdrp->source = tcphdrp->dest;
    tcphdrp->dest = port;

    //modify the ip address
    ip_addr = iphdrp->saddr;
    iphdrp->saddr = iphdrp->daddr;
    iphdrp->daddr = ip_addr;

    iphdrp->id = 1;
    iphdrp->frag_off = htons(0x4000);
    iphdrp->tot_len = htons(ip_tot_len);

    //pseudo header
    psd_header.daddr = iphdrp->daddr;
    psd_header.saddr = iphdrp->saddr;
    psd_header.mbz = 0;
    psd_header.ptcl = 0x06;
    psd_header.tcpl = htons(ip_tot_len - iph_len);// data size + tcp_header len

    //calculate the tcp checksum
    ngx_memset(p_tmp_buf, 0, len);
    tcphdrp->check = 0;
    ngx_memcpy(p_tmp_buf, (unsigned char*)&psd_header, sizeof(psd_header));
    ngx_memcpy(p_tmp_buf + sizeof(psd_header), (unsigned char*)tcphdrp, tcph_len);
    ngx_memcpy(p_tmp_buf + sizeof(psd_header) + tcph_len, (unsigned char*)pdata, data_len);
    tcphdrp->check = checksum((unsigned short*)p_tmp_buf, sizeof(psd_header) + tcph_len + data_len);

    //calculate the ip checksum
    ngx_memset(p_tmp_buf, 0, len);
    iphdrp->check = 0;
    ngx_memcpy(p_tmp_buf, iphdrp, iph_len);
    iphdrp->check = checksum((unsigned short*)p_tmp_buf, iph_len);

    //calculate the FCS
    ngx_memcpy(p + ether_len + ip_tot_len - data_len, pdata, data_len);
    eth_crc32 = ngx_crc32_long(p, ether_len + ip_tot_len);
    ngx_memcpy(p + ether_len + ip_tot_len, (unsigned char*)&eth_crc32, 4);
    len = ether_len + ip_tot_len + 4;

// add by suntus
   int bridge_out;
     bridge_out = ngx_get_bridge_out(c->dd.m->port);
    if (bridge_out == -1) {
        ngx_log_debug1(NGX_LOG_DEBUG_HTTP, r->connection->log, 0,
                       "[waf] get bridge_out error: bridge_in_port: %d",
                        c->dd.m->port);
    }
// add by suntus end


    
	//send the packet to the dpdk
    ngx_dpdk_send_buf((char*)p, len, bridge_out);
    
    if(c->dd.m){
        dpdk_mbuf_drop(c->client_waf, c->dd.m);
        c->dd.m = NULL;
    }

    ngx_log_debug0(NGX_LOG_DEBUG_HTTP, r->connection->log, 0, "[waf]send error page package to the dpdk");

    return NGX_OK;
}
//end add by vincent

