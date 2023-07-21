import cantools

db: cantools.db.can.database.Database = cantools.db.load_file('main.dbc')  # type: ignore

if (isinstance(db, cantools.db.can.database.Database)):
    messages = db.messages
    for m in messages:
        for s in m.signals:
            if s.is_multiplexer:
                continue
            dataType = "INTEGER"
            if s.is_float or isinstance(s.scale , float):
                dataType = "NUMERIC"
            print(f"\"{s.name}\" {dataType},")