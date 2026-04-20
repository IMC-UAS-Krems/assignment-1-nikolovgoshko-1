class User:
    def __init__(self, user_id, name, age):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions = []

    def add_session(self, session):
        self.sessions.append(session)

    def total_listening_seconds(self):
        total = 0
        for session in self.sessions:
            total += session.duration_listened_seconds
        return total

    def total_listening_minutes(self):
        return self.total_listening_seconds() / 60

    def unique_tracks_listened(self):
        track_ids = set()
        for session in self.sessions:
            track_ids.add(session.track.track_id)
        return track_ids

    def __str__(self):
        return self.name


class FreeUser(User):
    MAX_SKIPS_PER_HOUR = 6

    def __init__(self, user_id, name, age):
        User.__init__(self, user_id, name, age)


class PremiumUser(User):
    def __init__(self, user_id, name, age, subscription_start):
        User.__init__(self, user_id, name, age)
        self.subscription_start = subscription_start


class FamilyAccountUser(User):
    def __init__(self, user_id, name, age, subscription_start=None):
        User.__init__(self, user_id, name, age)
        self.subscription_start = subscription_start
        self.sub_users = []

    def add_sub_user(self, member):
        if member not in self.sub_users:
            self.sub_users.append(member)

    def all_members(self):
        members = [self]
        for sub_user in self.sub_users:
            members.append(sub_user)
        return members


class FamilyMember(User):
    def __init__(self, user_id, name, age, parent):
        User.__init__(self, user_id, name, age)
        self.parent = parent
