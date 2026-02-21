from datetime import datetime

dt = datetime.now()

dt_no_ms = dt.replace(microsecond=0)

print("With Microseconds:", dt)
print("No Microseconds:  ", dt_no_ms)