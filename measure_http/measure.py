def show_stats( start_time, end_time, num_requests ):
    time = end_time - start_time
    rps = num_requests / float(time)
    print 'Sent %s requests in %s seconds at a %s req/s rate' % (num_requests, time, rps)
