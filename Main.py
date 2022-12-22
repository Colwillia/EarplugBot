#Author: Colin Williams
#This is a bot that replies to comments that mentions disposable earplugs
#with a youtube link on properly inserting them

import praw,datetime,time,re,prawcore
from modules import TC, SecondsToMins
from modules import ClientInfo #module that stores client auth information
from praw.models import MoreComments






#arg: a string
#return val: True or False
#searches input string for words related to disposable/foam earplugs
def phraseMatch(instr):

    x = re.search('(3M|foam|disposable).*(earplug|ear.*plug|plug)', instr, re.IGNORECASE)
    #x = re.search('sauce', instr, re.IGNORECASE)
    
    if x:
        return True

    return False

#arg: a string
#return: list of usernames
#Finds users that have interacted with input user's comments and return list of usernames
def discover(inUser):
    
    userComment = 0
    users = {}
    
    

    redditor = reddit.redditor(inUser)
    for top_comments in redditor.comments.new(limit=1000):#limit=1000

        try:
            userComment += 1

            top_comments.refresh()
            #top_comments.replace_more(limits=None)
           # print(f"top_comments: {type(top_comments)}")

            for child_comment in top_comments.replies:
                #pprint.pprint(vars(child_comment))
                #print(f"child_comment: {type(child_comment)}")
                #return
                # if(type(child_comment) is praw.MoreComments):
                #     vals = users.values()
                #     return vals

                if isinstance(child_comment,MoreComments):
                    continue

                author = str(child_comment.author)
                authHash = hash(author)

                if users.get(authHash) == None:
                    users.update({authHash:author})

        except praw.exceptions.ClientException:
            continue

   

    vals = users.values()
    #names = sorted(vals, key=str.casefold)
    # i = 0
    # for usr in names:
    #     print(f"u/{usr}, ", end = "")
    #     i+=1
    #     if i % 5 == 0:
    #         print("")

    # print("\n")
    # print(f"Saved Users: {len(users)}")

    return list(vals)


#arg: string, int
#return: Nothing
#Searches user's comment history until specified date for matching comments
def findInUser(inUser,maxDays):
    redditor = reddit.redditor(inUser)
    
    try:
        for userComment in redditor.comments.new(limit = 200): #Might lower amount to
                                                                #prevent getting bogged down by bot accounts
            
            ageLimit = time.time() - userComment.created_utc > TC.DAY*maxDays
            if ageLimit: #reached comments older than ten days
                # print(f"days: {TC.DAY*maxDays}")
                # print(f"Current time: {datetime.datetime.fromtimestamp(time.time())}")
                # print(f"reached comment age limit: {datetime.datetime.fromtimestamp(userComment.created_utc)}")
                return

            if phraseMatch(userComment.body):

                post = userComment.submission
                submissId = post.id
                subTitle = post.subreddit
                subUTC = post.created_utc
                
                #print(submissId)
                try:
                    rdlogfile = open("logs/idlog.txt","r")
                except:
                    rdlogfile = open("logs/idlog.txt","x")
                    rdlogfile.close
                    rdlogfile = open("logs/idlog.txt","r")

                if(rdlogfile.read().find(submissId) < 0): #checking 
                    rdlogfile.close()
                    
                    #log before sending reply to avoid unlogged events
                    #writting submission ID to the logfile
                    idLogFile = open("logs/idlog.txt","a")
                    idLogFile.write(submissId + "\n")
                    idLogFile.close()

                    subLogFile = open("logs/sublog.txt", "a")
                    subLogFile.write("r\\" + str(subTitle) + ":" + str(subUTC) + ":" + "\n" )
                    subLogFile.close

                    commentLogFile = open("logs/commentlog.txt", "a")
                    commentLogFile.write("###############################################################\n")
                    commentLogFile.write("Subreddit: " + "r\\" + str(subTitle) + "\n")
                    commentLogFile.write("User: " + " u\\" + inUser + "\n")
                    commentLogFile.write("Date: " + str(datetime.datetime.fromtimestamp(userComment.created_utc)) + "\n\n")
                    commentLogFile.write(userComment.body + "\n")
                    commentLogFile.close
                    #send reply
                else:
                    rdlogfile.close()
                
                return
        #print(f"reached end of comments")
    except prawcore.exceptions.Forbidden:
        print("403 error")
    except prawcore.exceptions.NotFound:
        print("404 error")
    except:
        print("Other error")

    
    return





#######################################################
## Main
#######################################################
print(f"Starting Earplug Bot")


reddit = praw.Reddit(
    client_id= ClientInfo.CLIENT_ID,
    client_secret= ClientInfo.CLIENT_SECRET,
    user_agent= ClientInfo.USER_AGENT,
    password= ClientInfo.PASSWORD,
    username= ClientInfo.USERNAME
)

userList = {}
pastAncestors = {}
pastSubID = ""
while(True):
    totalStart = time.time()
    if len(userList) == 0:
        ancestralUser = ""      
        print(f"Finding Ancestral User...")                         #finding ancestor for discover()
        for submission in reddit.subreddit("all").hot(limit=1):
            while True:
                submission.comments.replace_more(limit=5) #Change to 5
                for top_level_comment in submission.comments:
                    
                   
                    if not top_level_comment.stickied:

                        currentSubID = submission.id
                        if pastSubID != currentSubID:

                            pastSubID = currentSubID
                            pastAncestors.clear()

                        ancestralUser = str(top_level_comment.author)
                        if not pastAncestors.get(hash(ancestralUser)):
                            break
                break
        
        pastAncestors.update({hash(ancestralUser):ancestralUser})
        print(f"ancestalUser: {ancestralUser}")
        start = time.time()

        print("Discovering more users...\n")

        userList = discover(ancestralUser)                  #Discovery mode
        end = time.time()

        i = 0
        for usr in userList:
            print(f"u/{usr}, ", end = "")
            i+=1
            if i % 5 == 0:
                print("")

        print("\n")
        print(f"Saved Users: {len(userList)}")
        print(f"elapsed time: {SecondsToMins.secsToMins(end-start)}")
        print("\n")




    print("Searching user comments...")

    findUserStartTime = time.time()
    elapsedTime = time.time() - findUserStartTime 

    while(len(userList) > 0 and elapsedTime < TC.TEN_MINUTES):  #searching user comments
        usr = userList.pop(0)
        findInUser(usr, 10)

        elapsedTime = time.time() - findUserStartTime 
        # print(f"u/{usr}, ", end = "")
        # i+=1
        # if i % 5 == 0:
        #     print("")

    print(f"userList length: {len(userList)}")
    totalEnd = time.time()
    print(f"Total Elapsed time: {SecondsToMins.secsToMins(totalEnd-totalStart)}")
