

def check(time_wins, win_len, times):

	n=len(time_wins)
	for start in times:
		ends = start + win_len
		cnt = 0
		for interval in time_wins:
			if(interval[0] > ends or interval[1] < start):
				continue
			else:
				cnt += 1
		if(cnt == n):
			return (True, (start, ends))

	return (False, (0, 30))



def get_time_windows(time_wins, horizon):

	n = len(time_wins)
	time_points = []
	for j in time_wins:
		time_points.append(j[0])
		time_points.append(j[1])
	time_points.sort()
	lo = 0
	hi = horizon		# ensures resulting window size is lesser than horizon

	# binary search on the smallest possible window size that satisfies all passengers
	while hi>lo:
		mid = lo + (hi - lo) // 2
		possible, window = check(time_wins, mid, time_points)
		if(possible):
			hi = mid
		else:
			lo = mid + 1


	possible, window = check(time_wins, lo, time_points)

	# keeping the time window real
	final_window = (max(0, window[0]-15) , window[1]+ 15)
	
	return final_window


# def main():
# 	win = get_time_windows([(0, 40), (0, 30), (10, 50), (20, 50), (23, 40), (30, 70), (20, 60), (40, 80), (35, 45), (40, 60)], 5000)
# 	print(win)

# if __name__ == '__main__':
# 	main()

