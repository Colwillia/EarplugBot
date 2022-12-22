
import math
def secsToMins(secs):
    minutes = math.trunc(secs / 60)
    decimal = (secs/60) - minutes
    seconds = math.trunc(60*decimal)

    timeStr = ""
    

    if minutes > 0 and seconds > 0:
        timeStr =str(minutes) + " minutes" + " and " + str(seconds) + " seconds"
    elif minutes > 0 and seconds <=0:
        timeStr = str(minutes) + " minutes"
    else:
        timeStr = str(seconds) + " seconds"

    return timeStr
