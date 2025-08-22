BASE_URL = "https://user-api.gluehome.com/v1"
API_URL = BASE_URL + "/api-keys"
LOCKS_ID_URL = BASE_URL + "/locks"
LOCK_ID_URL = LOCKS_ID_URL + "/{lock_id}"
TOGGLE_LOCK_URL = LOCK_ID_URL + "/operations"

SUPPORTED_LOCK_TYPES = ["lock", "unlock"]
