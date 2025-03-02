from datetime import datetime, timedelta

class ResourceGrant:
    def __init__(self, deposit, corporation, duration):
        self.deposit = deposit
        self.corporation = corporation
        self.start_time = datetime.now()
        self.duration = timedelta(seconds=duration)

    @property
    def expired(self):
        return datetime.now() >= self.start_time + self.duration

    @property
    def time_remaining(self) -> timedelta:
        remaining = self.start_time + self.duration - datetime.now()
        return max(remaining, timedelta(0)) 