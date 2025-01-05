class User:
    def __init__(self, user_id, username, night=22, morning=10, minutes_offset=30, enabled=1):
        self.night = night
        self.morning = morning
        self.minutes_offset = minutes_offset
        self.user_id = user_id
        self.username = username
        self.enabled = enabled

    def __eq__(self, other):
        return self.user_id == other.user_id

    def __hash__(self):
        return hash(self.user_id)

    def __repr__(self):
        return f"User: {self.username}, User ID: {self.user_id}"
