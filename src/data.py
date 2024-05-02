import json
import random
from pathlib import Path
from typing import Optional
from filelock import FileLock

### PATHS INITIALIZATION ### ---------------------------------------------

DATA_PATH = Path(__file__).parent.parent / "data"
USERS_PATH = Path(__file__).parent.parent / "users"

TWEETS = DATA_PATH / "tweets.json"
TRAINING = DATA_PATH / "training.json"
CONTROLS = DATA_PATH / "controls.json"
SEEDS = DATA_PATH / "seeds.json"

USERS = USERS_PATH / "users.json"
USERS_LOCK = FileLock(USERS.with_suffix(".lock"))

users = list(USERS_PATH.glob("*.json"))
lock_per_user = {user.stem: FileLock(user.with_suffix(".lock")) for user in users}


### JSON LOCK ### --------------------------------------------------------

def json_read(path, lock: FileLock = None):
    """lock a file while reading it, to avoid conflicts"""
    if lock is None:
        lock = get_user_lock(path)
    with lock:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def json_write(data, path, lock: FileLock = None, **kwargs):
    """lock a file while writing it, to avoid conflicts"""
    if lock is None:
        lock = get_user_lock(path)
    with lock:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                file_data = json.load(f)
            file_data.update(data)
        else:
            file_data = data
        with open(path, "w", encoding="utf-8") as f:
            json.dump(file_data, f, **kwargs)


def get_user_lock(path):
    """get an user's lock"""
    if not isinstance(path, Path):
        path = Path(path)
    return lock_per_user.get(path.stem, FileLock(path.with_suffix(".lock")))


### GET AND SAVE FUNCTIONS ### -------------------------------------------

def getUsers():
    """get id, name and password of every users from data/users.json"""
    with USERS_LOCK:
        with open(USERS, "r", encoding="utf-8") as f:
            return json.load(f)


def saveUsers(users):
    """saves in data/users.json file, which contains users ids, names and passwords"""
    json_write(users, USERS, USERS_LOCK, indent=4, ensure_ascii=False)


def getSeeds():
    """get our dict of seeds from data/seeds.json"""
    with open(SEEDS, "r", encoding="utf-8") as f:
        return json.load(f)


def getTweets():
    """get ou dict of tweets from data/tweets.json"""
    with open(TWEETS, "r", encoding="utf-8") as f:
        return json.load(f)


def getTrainingTweets():
    """get our dict of training tweets from data/train.json"""
    with open(TRAINING, "r", encoding="utf-8") as f:
        return json.load(f)


def getControlsTweets():
    """get our dict of training tweets from data/train.json"""
    with open(CONTROLS, "r", encoding="utf-8") as f:
        return json.load(f)


### VARIABLES INITIALIZATION ### -----------------------------------------


tweets = getTweets()
seeds = getSeeds()

training = getTrainingTweets()
training_ids = set(training.keys())

controls = getControlsTweets()
controls_ids = set(controls.keys())


### USER FILES MANAGMENT ### ---------------------------------------------

def getUserData(user_id, dataType="annotations"):
    """get either an user's annotations or score data"""
    path = USERS_PATH / f"{user_id.id}_{dataType}.json"
    return json_read(path)


def saveUserData(user_id, user_data, dataType="annotations"):
    """save either an user's annotations or score data"""
    path = USERS_PATH / f"{user_id.id}_{dataType}.json"
    json_write(user_data, path)


def getUserDataAlternate(user_id, dataType="annotations"):
    """get either an user's annotations or score data, user_id is an int here, only for tableScores()"""
    path = USERS_PATH / f"{user_id}_{dataType}.json"
    return json_read(path)


def createUserFile(user_id):
    """create a json file with an user's score and annotations"""
    path_annotations = USERS_PATH / f"{user_id.id}_annotations.json"
    path_score = USERS_PATH / f"{user_id.id}_score.json"
    if path_score.exists():
        return
    userFileScore = {"user_id": user_id.id, "score": 0, "badges": []}
    userFileAnnot = {"user_id": user_id.id, "coordinates": {"block": 0, "tweet": 0}, "annotations": []}
    json_write(userFileAnnot, path_annotations)
    json_write(userFileScore, path_score)
    addFirstBlock(user_id)


### BLOCK MANAGMENT ### --------------------------------------------------

def createBlockData(alreadyAnnotated, max_size=10, max_control=5):
    """create a list of tweets to annotate, randomly chosen"""

    # variable initialization #

    tweets = getTweets()
    block_seed = random.choice(list(getSeeds().keys()))

    # block creation with controls #

    block_control = [{"id": k, "type": "control"} for k, v in controls.items() if
                     v["seed_id"] == block_seed and k not in alreadyAnnotated]
    if len(block_control) > max_control:
        try:
            block_control = random.sample(block_control, max_control)
        except:
            block_control = []

    block_annotate = [{"id": k, "type": "annotation"} for k, v in tweets.items() if
                      v["seed_id"] == block_seed and k not in alreadyAnnotated and v["shadowBan"] == False]
    if len(block_annotate) > max_size - len(block_control):
        try:
            block_annotate = random.sample(block_annotate, max_size - len(block_control))
        except:
            block_annotate = []

    block = block_annotate + block_control

    # return or recursive #

    if len(block) == 0 and len(alreadyAnnotated) < len(tweets) + len(controls):
        return createBlockData(alreadyAnnotated)

    else:
        return random.sample(block, len(block)), block_seed


def addBlock(user_id):
    """create an user's file if not exist and add a block to it"""
    user_data = getUserData(user_id)
    alreadyAnnotated = {v["tweet_id"] for v in sum([i["tweets_ids"] for i in user_data["annotations"][1:]], []) if
                        v["scored"] == True}
    tweets_ids, seed_id = createBlockData(alreadyAnnotated)
    block = {
        "seed_id": seed_id,
        "tweets_ids": [
            {"tweet_id": i["id"], "UMWE_identified": 4, "MWE_recognized": 4, "scored": False, "type": i["type"]} for i
            in tweets_ids]}
    user_data["annotations"].append(block)
    saveUserData(user_id, user_data)
    return user_data


def addFirstBlock(user_id):
    """The very first block for an user"""
    user_data = getUserData(user_id)
    first_block = random.sample(list(training_ids), len(list(training_ids)))
    block = {
        "seed_id": "-1",
        "tweets_ids": [{"tweet_id": i, "UMWE_identified": 4, "MWE_recognized": 4, "scored": False, "type": "training"}
                       for i in first_block]
    }
    user_data["annotations"].append(block)
    saveUserData(user_id, user_data)
    return user_data


def BlockPointer(user_id):
    """point to the current block + get its coordinates"""
    user_data = getUserData(user_id)
    currentBlockId = user_data["coordinates"]["block"]
    currentTweetId = user_data["coordinates"]["tweet"]
    currentBlock = user_data["annotations"][currentBlockId]
    return currentBlock, currentBlockId, currentTweetId


def generateData(user_id):
    "generate data for frontend according to annotated tweet's type"

    block, currentBlockId, currentTweetId = BlockPointer(user_id)
    tweet_id = block["tweets_ids"][currentTweetId]["tweet_id"]

    data = {
        "seed_id": block["seed_id"],
        "block_id": currentBlockId,
        "tweet_id": tweet_id,
        "current_tweet_index": currentTweetId,
        "total_block": len(block["tweets_ids"]),
        "shown_tweet_id": currentTweetId + 1,
        "UMWE_identified_answer": str(block["tweets_ids"][currentTweetId]["UMWE_identified"]),
        "MWE_recognized_answer": str(block["tweets_ids"][currentTweetId]["MWE_recognized"])
    }

    if tweet_id in training_ids:
        tweet = training[tweet_id]
        data["seed_text"] = seeds[str(tweet["seed_id"])]["content"]
        data["tweet_text"] = tweet["tweet"]
        data["MWE_recognized_correction"] = str(int(tweet["MWE_recognized"]))
        data["UMWE_identified_correction"] = str(int(tweet["UMWE_identified"]))
        data["correction"] = tweet["correction"]
        data["__type__"] = "training"

    elif tweet_id in controls_ids:
        tweet = controls[tweet_id]
        data["seed_text"] = seeds[str(tweet["seed_id"])]["content"]
        data["tweet_text"] = tweet["tweet"]
        data["MWE_recognized_correction"] = str(int(tweet["MWE_recognized"]))
        data["UMWE_identified_correction"] = str(int(tweet["UMWE_identified"]))
        data["__type__"] = "control"

    else:
        data["seed_text"] = seeds[str(block["seed_id"])]["content"]
        data["tweet_text"] = tweets[block["tweets_ids"][currentTweetId]["tweet_id"]]["tweet"]
        data["__type__"] = "annotation"

    return data


def getData(user_id, order: bool = None, tweet_id: str = None, block_id: str = None):
    createUserFile(user_id)
    data = generateData(user_id)
    return data


### SCORE AND BADGE MANAGMENT ### ----------------------------------------

def giveBadge(user_id, user_data, user_score) -> Optional[int]:
    """at the end of a block, checks % of annotated tweets for a seed and gives a badge according to it"""

    seedId = user_data["annotations"][-1]["seed_id"]

    total_annotated = 0
    for block in user_data["annotations"]:
        if block["seed_id"] == seedId:
            total_annotated += len(
                [i for i in block["tweets_ids"] if i["UMWE_identified"] != 4 and i["MWE_recognized"] != 4])

    total_to_annotate = seeds[seedId]["total"]

    if total_annotated == total_to_annotate and seedId not in user_score["badges"]:
        user_score["badges"].append(seedId)
        user_score["badges"] = list(set(user_score["badges"]))
        saveUserData(user_id, user_score, dataType="score")
        return seedId

    else:
        return None


def updateScore(user_id, user_data, user_score, currentBlockId, currentTweetId):
    """update an user's score by adding 1 when a tweet is annotated (with both UMWE and MWE annotations)"""
    tweet = user_data["annotations"][currentBlockId]["tweets_ids"][currentTweetId]
    if tweet["scored"] == False and tweet["UMWE_identified"] != 4 and tweet["MWE_recognized"] != 4:
        user_data["annotations"][currentBlockId]["tweets_ids"][currentTweetId]["scored"] = True
        user_score["score"] += 1
    saveUserData(user_id, user_score, dataType="score")
    return user_data


def tableScores():
    """create a dict with every needed informations to create a scoreboard"""
    table = []
    for k, v in getUsers().items():
        user_data = getUserDataAlternate(str(v["id"]), dataType="score")
        dict_user = {
            "username": v["username"],
            "id": v["id"],
            "score": user_data["score"],
            "badges": user_data["badges"]
        }
        table.append(dict_user)
    return table


### USER INPUT MANAGMENT ### ---------------------------------------------

def saveAnnotation(user_id, data):
    """save an user's annotation for a tweet"""
    user_data = getUserData(user_id)
    block, currentBlockId, currentTweetId = BlockPointer(user_id)
    if user_data["annotations"][currentBlockId]["tweets_ids"][currentTweetId]["type"] == "annotation":
        user_data["annotations"][currentBlockId]["tweets_ids"][currentTweetId][data["question"]] = data["annotation"]
        user_data["annotations"][currentBlockId]["tweets_ids"][currentTweetId]["timestamp"] = data["timestamp"]
    else:
        if user_data["annotations"][currentBlockId]["tweets_ids"][currentTweetId]["scored"] == False:
            user_data["annotations"][currentBlockId]["tweets_ids"][currentTweetId][data["question"]] = data["annotation"]
            user_data["annotations"][currentBlockId]["tweets_ids"][currentTweetId]["timestamp"] = data["timestamp"]
    saveUserData(user_id, user_data)


def isTutoDoneBack(user_id):
    user_data = getUserData(user_id)
    seedId = user_data["annotations"][user_data["coordinates"]["block"]]["seed_id"]
    total_annotated = sum(
        1 for block in user_data["annotations"] if block["seed_id"] == seedId
        for i in block["tweets_ids"] if i["UMWE_identified"] != 4 and i["MWE_recognized"] != 4
    )
    total_to_annotate = seeds[seedId]["total"]
    return total_annotated == total_to_annotate


def goNextGoPrevious(user_id, data):
    """allow the user to navigate through tweets and blocks"""

    # variable initialization #

    newBadge = None
    user_data = getUserData(user_id)
    user_score = getUserData(user_id, dataType="score")
    block, currentBlockId, currentTweetId = BlockPointer(user_id)

    endTweet = len(
        user_data["annotations"][user_data["coordinates"]["block"]]["tweets_ids"]) - 1  # last tweet ID in a block
    endBlock = len(user_data["annotations"]) - 1  # last block ID in annotated blocks list

    # go previous #

    if data["order"] == -1:

        user_data = updateScore(user_id, user_data, user_score, currentBlockId, currentTweetId)

        if user_data["coordinates"]["tweet"] == 0 and user_data["coordinates"]["block"] != 0:
            user_data["coordinates"]["block"] -= 1
            user_data["coordinates"]["tweet"] = len(
                user_data["annotations"][user_data["coordinates"]["block"]]["tweets_ids"]) - 1

        elif user_data["coordinates"]["tweet"] != 0:
            user_data["coordinates"]["tweet"] -= 1

    # go next #

    if data["order"] == 1:

        user_data = updateScore(user_id, user_data, user_score, currentBlockId, currentTweetId)

        if user_data["coordinates"]["tweet"] == endTweet and user_data["coordinates"]["block"] == endBlock:
            newBadge = giveBadge(user_id, user_data, getUserData(user_id, dataType="score"))
            user_data = addBlock(user_id)
            user_data["coordinates"]["block"] += 1
            user_data["coordinates"]["tweet"] = 0

        elif user_data["coordinates"]["tweet"] == endTweet and user_data["coordinates"]["block"] != endBlock:  #
            user_data["coordinates"]["block"] += 1
            user_data["coordinates"]["tweet"] = 0

        elif user_data["coordinates"]["tweet"] != endTweet:
            user_data["coordinates"]["tweet"] += 1

    # save and return #

    saveUserData(user_id, user_data)
    return newBadge

# signification des nombres dans l'annotation :
# - 0 : non
# - 1 : oui
# - 2 : je ne sais pas
# - 4 : passé / pas encore fait
