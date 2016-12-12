MAX_PDU_SIZE = 200*1024*1024
# Requests --------------------------------------------------------------------
QUERY_NICK = '1'
QUERY_SERVERS = '2'
QUERY_SHIPS = '3'
QUERY_GAMES = '4'
QUERY_NEW_GAME = '5'
QUERY_JOIN_GAME = '6'


CTR_MSGS = {QUERY_NICK: "Get nick available",
            QUERY_SERVERS: "Get available servers",
            QUERY_SHIPS: "Get if ships positions ok",
            QUERY_GAMES: "Get games available for joining",
            QUERY_NEW_GAME: "Create a new game",
            QUERY_JOIN_GAME: "Join an existing game"}
# Responses--------------------------------------------------------------------
RSP_OK = '0'
RSP_NICK_EXISTS = '1'
RSP_SHIPS_PLACEMENT = '2'
RSP_BAD_NICK = '3'
RSP_GAME_FULL = '4'
RSP_BAD_SIZE = '5'
RSP_NO_SUCH_CLIENT = '6'
RSP_GAME_STARTED = '7'
RSP_NO_SUCH_GAME = '8'

RSP_NOT_IMPLEMENTED_YET = '667'

ERR_MSGS = {RSP_OK: 'No Error',
            RSP_NICK_EXISTS: 'Such nickname already Exists',
            RSP_SHIPS_PLACEMENT: 'Ships cannot be placed in such way.',
            RSP_BAD_NICK: 'The chosen nickname is not suitable.',
            RSP_GAME_FULL: 'The game is already full.',
            RSP_BAD_SIZE: "Size cannot go out of bounds from [5,15]",
            RSP_NO_SUCH_CLIENT: "Server expects the clients nick to be in its client list",
            RSP_GAME_STARTED: "The game that client wants to join, has already started",
            RSP_NO_SUCH_GAME: "The game with such ID does not exist.",
            RSP_NOT_IMPLEMENTED_YET: "Unimplemented functionality! Implement it!"}
# Field separator for sending multiple values ---------------------------------
MSG_FIELD_SEP = ':'
