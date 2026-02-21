from datetime import datetime

date1 = datetime(2026, 2, 21, 12, 0, 0) 
date2 = datetime(2026, 2, 20, 12, 0, 0) 

duration = date1 - date2
seconds_diff = duration.total_seconds()

print(f"Difference between {date1} and {date2}:")
print(f"{int(seconds_diff)} seconds")