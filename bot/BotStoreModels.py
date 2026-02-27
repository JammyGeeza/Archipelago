# from .BotStore import db
# from datetime import datetime
# from pony.orm import Required, Optional, PrimaryKey, Set, composite_key

# class Binding(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     port = Required(int)
#     channel_id = Required(int)
#     created_at = Required(datetime, default=lambda: datetime.utcnow())
#     modified_at = Optional(datetime)

#     notifications = Set("NotificationSettings", cascade_delete=True)

#     composite_key(channel_id)

#     @classmethod
#     def get_or_create(cls, channel_id: int, port: int) -> "Binding":
#         return cls.get(channel_id=channel_id, port=port)

# class NotificationSettings(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     binding = Required(Binding)
#     user_id = Required(int)
#     slot_id = Required(int)
#     hint_flags = Required(int, default=0)
#     item_flags = Required(int, default=0)
#     created_at = Required(datetime, default=lambda: datetime.utcnow())
#     modified_at = Optional(datetime)

#     terms = Set("NotificationTerm", cascade_delete=True)

#     composite_key(binding, user_id, slot_id)

# class NotificationCount(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     notification = Required(NotificationSettings)
#     item_id = Required(int)
#     amount = Required(int)
#     end_amount = Required(int)

# class NotificationTerm(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     notification = Required(NotificationSettings)
#     term = Required(str)

#     composite_key(notification, term)