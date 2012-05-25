import re
import datetime

# 127.0.0.1 - - [27/Oct/2008:21:18:31 -0200] "GET /abcdef999 HTTP/1.1" 404 359 "-" "w3af.sf.net"
def get_time( log_line ):
  tmp = re.findall('\\[.*?/.*/....:(.*?):(.*?):(.*?) .*?\\]',log_line)[0]
  res = (int(tmp[0]), int(tmp[1]), int(tmp[2]))
  return res
  
lines = file('/var/log/apache2/access.log').readlines()
first = lines[0]
last = lines[-1]

# Now parse the time
start_time = get_time(first)
end_time = get_time(last)

# Generate the datetime objects to perform the diff
start_datetime = datetime.datetime(1981, 6, 16, start_time[0], start_time[1], start_time[2])
end_datetime = datetime.datetime(1981, 6, 16, end_time[0], end_time[1], end_time[2])
timedelta = end_datetime - start_datetime

# Report
print 'Performed %i requests in %i seconds (%f req/sec)' % (len(lines), timedelta.seconds, float(len(lines))/timedelta.seconds)



