MAX_PDU_SIZE = 200*1024*1024
# Requests --------------------------------------------------------------------
QUERY_NICK = '1'
QUERY_SERVERS = '2'
QUERY_PLACE_SHIPS = '3'
QUERY_GAMES = '4'
QUERY_NEW_GAME = '5'
QUERY_JOIN_GAME = '6'
START_GAME = '7'
QUERY_SHOOT = '8'
QUERY_CONNECTION = '9'
QUERY_LEAVE = '10'

CTR_MSGS = {QUERY_NICK: "Get nick available",
            QUERY_SERVERS: "Get available servers",
            QUERY_PLACE_SHIPS: "Get if ships positions ok",
            QUERY_GAMES: "Get games available for joining",
            QUERY_NEW_GAME: "Create a new game",
            QUERY_JOIN_GAME: "Join an existing game",
            START_GAME: "Starts the current game and additionally sends all ships",
            QUERY_SHOOT: "Sends shots made to all other players",
            QUERY_CONNECTION: "Get connection to server."}
# Responses--------------------------------------------------------------------
ERR_MSGS = {}

RSP_OK = '0'
ERR_MSGS[RSP_OK] = "Response Okay."

RSP_MULTI_OK = '13'
ERR_MSGS[RSP_MULTI_OK] = "Response okay sent to multiple clients"

RSP_CLIENT_EXISTS = '1'
ERR_MSGS[RSP_CLIENT_EXISTS] = 'Such client already connected.'

RSP_SHIPS_PLACEMENT = '2'
ERR_MSGS[RSP_SHIPS_PLACEMENT] = 'Ships cannot be placed in such way.'

RSP_BAD_NICK = '3'
ERR_MSGS[RSP_BAD_NICK] = 'The chosen nickname is not suitable.'

RSP_GAME_FULL = '4'
ERR_MSGS[RSP_GAME_FULL] = "The game is full."

RSP_BAD_SIZE = '5'
ERR_MSGS[RSP_BAD_SIZE] = "Choose valid game size, between 5 and 15."

RSP_NO_SUCH_CLIENT = '6'
ERR_MSGS[RSP_NO_SUCH_CLIENT] = "Server expects the client to be in the clients list."

RSP_GAME_STARTED = '7'
ERR_MSGS[RSP_GAME_STARTED] = "Cannot join a game that has started."

RSP_NO_SUCH_GAME = '8'
ERR_MSGS[RSP_NO_SUCH_GAME] = "There is no such game with specified ID."

RSP_SHIPS_NOT_PLACED = '9'
ERR_MSGS[RSP_SHIPS_NOT_PLACED] = "Some players have not placed their ships yet or only 1 player connected."

RSP_NOT_MASTER = '10'
ERR_MSGS[RSP_NOT_MASTER] = "Not master, so cannot create game and some other stuff maybe..."

RSP_INVALID_SHOT = '11'
ERR_MSGS[RSP_INVALID_SHOT] = "Shot placed on invalid square or square has already been shot."

RSP_WAIT_YOUR_TURN = '12'
ERR_MSGS[RSP_WAIT_YOUR_TURN] = "It is not your turn, wait until it is your turn."

RSP_CONNECTION_FAILED = '15'
ERR_MSGS[RSP_CONNECTION_FAILED] = "Connection to server failed."

RSP_BAD_REQUEST = '17'
ERR_MSGS[RSP_BAD_REQUEST] = "Bad request, probably missing data."

RSP_NOT_IMPLEMENTED_YET = '667'
ERR_MSGS[RSP_NOT_IMPLEMENTED_YET] = "Unimplemented functionality"

RSP_LEAVE_GAME = '18'
ERR_MSGS[RSP_LEAVE_GAME] = "Unable to leave game."

# Alive messages -----------------------------------------------------------------
KEEP_ALIVE = '1001'
DISCONNECT = '1002'
SERVER_SHUTDOWN = '1010'
