from datetime import datetime, timezone, timedelta

epoch_time = 920572800
converted_time = datetime.fromtimestamp(epoch_time)

print(converted_time)