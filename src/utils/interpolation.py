def interpolate(acc, points):
    acc = min(acc, 100)

    acc /= 100

    i = 0
    for i in range(len(points)):
        if acc < points[i][0]:
            break

    if i == 0:
        i = 1

    middle_dis = (acc - points[i - 1][0]) / (points[i][0] - points[i - 1][0])

    return points[i - 1][1] + middle_dis * (points[i][1] - points[i - 1][1])