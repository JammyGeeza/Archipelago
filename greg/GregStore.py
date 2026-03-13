from datetime import datetime

try:
    # ponyorm is a requirement for webhost, not default server, so may not be importable
    from pony.orm.dbapiprovider import OperationalError
    from pony.orm import Database, Required, db_session, PrimaryKey, Optional
except ImportError:
    OperationalError = ConnectionError

db = Database()

def init_db(args):

    db.bind(
        provider=args["provider"],
        host=args["host"],
        user=args["user"],
        password=args["password"],
        database=args["database"],
        connect_timeout=args["connect_timeout"],
        sslmode=args["sslmode"],
        options=args["options"]
    )

    db.generate_mapping(create_tables=False)

class ItemSend(db.Entity):
    _table_ = "itemlog"
    _schema_ = "gregipelago"

    id = PrimaryKey(int, auto=True)
    sender = Required(str)
    item = Required(str)
    receiver = Required(str)
    roomid = Required(str)
    timestamp = Required(datetime, default=lambda: datetime.now(datetime.UTC))

    @classmethod
    @db_session
    def send(cls, data):
        for sender, item, receiver, room_id in data:
            cls(sender=sender, item=item, receiver=receiver, room_id=room_id)

class DeathSend(db.Entity):
    _table_ = "deathlink"
    _schema_ = "gregipelago"

    id = PrimaryKey(int, auto=True)
    sender = Required(str)
    cause = Optional(str, nullable=True)
    roomid = Required(str)
    timestamp = Required(datetime, default=lambda: datetime.now(datetime.UTC))

    @classmethod
    @db_session
    def send(cls, sender, cause, roomid):
        cls(sender=sender, cause=cause, roomid=roomid)

class CompleteSend(db.Entity):
    _table_ = "completions"
    _schema_ = "gregipelago"

    id = PrimaryKey(int, auto=True)
    sender = Required(str)
    goal = Required(bool)
    roomid = Required(str)
    timestamp = Required(datetime, default=lambda: datetime.now(datetime.UTC))

    @classmethod
    @db_session
    def send(cls, sender, goal, roomid):
        cls(sender=sender, goal=goal, roomid=roomid)

class PlaylogSend(db.Entity):
    _table_ = "playlog"
    _schema_ = "gregipelago"

    id = PrimaryKey(int, auto=True)
    sender = Required(str)
    roomid = Required(str)
    timestamp = Required(datetime, default=lambda: datetime.now(datetime.UTC))
    status = Required(str)
    tags = Required(str)

    @classmethod
    @db_session
    def send(cls, sender, roomid, status, tags):
        cls(sender=sender, status=status, roomid=roomid, tags=tags)
