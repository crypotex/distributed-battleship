MAX_PDU_SIZE = 200*1024*1024
# Requests --------------------------------------------------------------------
QUERY_NICK = '1'
QUERY_SERVERS = '2'

CTR_MSGS = {QUERY_NICK: 'Get nick available',
            QUERY_SERVERS: 'Get last N messages'}
# Responses--------------------------------------------------------------------
RSP_OK = '0'
ERR_MSGS = {RSP_OK: 'No Error'}
# Field separator for sending multiple values ---------------------------------
MSG_FIELD_SEP = ':'
