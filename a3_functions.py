import csv
import re
import operator
import math
import os


def readData(tfile, skipline):
    print("Reading: " + tfile)
    file = open(tfile, "r", encoding="utf8")
    reader = csv.reader(file, delimiter="\t")
    xrow = []
    lcount = -1
    for row in reader:
        lcount = lcount + 1
        if(skipline and lcount == 0):
            continue

        tweetid = row[0]

        # Does the tweet contain a verifiable factual claim?
        isfactual = False
        if(row[2] == "yes"):
            isfactual = True

        frow = [row[1], isfactual, tweetid]

        # if(lcount < 15):
        #     print(frow)

        xrow.append(frow)
    file.close()

    # print(xrow)
    return xrow

stopwords = [
    '', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
]

def tweetFilter(tweet):
    tweet = re.sub('https?://[^\s]+',' ', tweet)
    tweet = re.sub('[^\sa-zA-Z1-9]',' ', tweet)
    for i in range(20):
        tweet = re.sub('\s\s',' ', tweet)
        tweet = re.sub('^\s','', tweet)
        tweet = re.sub('\s$','', tweet)
    return tweet


def parseTraining(tdata):
    xwords = {}
    fwords = {}
    lcount = -1
    factual_count = 0
    for d in tdata:
        lcount = lcount + 1
        

        tweet = d[0].lower()
        factual = d[1]
        if(factual):
            factual_count = factual_count + 1

        # if(lcount > 8):
        #     continue
        # if(lcount < 5):
        #     print(tweet)
        # print(tweet)
        tweet = tweetFilter(tweet)
        split_tweet = tweet.split(" ")

        for w in split_tweet:
            wcount = 0
            fcount = 0
            if w not in xwords.keys():
                wcount = 1
                if(factual):
                    fcount = 1
            else:
                wcount = xwords[w][0] + 1
                if(factual):
                    fcount = xwords[w][1] + 1
            xwords[w] = [wcount, fcount]


        # if(lcount < 5):
        #     print(split_tweet)

    for delw in stopwords:
        if delw in xwords.keys():
            del xwords[delw]


    for w in xwords.items():
        # print(w)
        if(w[1][0] > 1):
            fwords[w[0]] = w[1]

    original_sorted = sorted(xwords.items(), key=operator.itemgetter(1))
    final_sorted = sorted(fwords.items(), key=operator.itemgetter(1))

    # print(original_sorted)

    xwords = {}
    fwords = {}
    for w in original_sorted:
        xwords[w[0]] = w[1]
    for w in final_sorted:
        fwords[w[0]] = w[1]

    # print(xwords)
    datacount = lcount + 1

    return xwords, fwords, datacount, factual_count


def analyzeData(tdata, vocab, dcount, fcount, alpha, trace_file):

    print("\n=============")
    print("Analyzing test data for: " + trace_file)
    print("=============\n")
    vlen = len(vocab)
    print(vlen)

    wcount_len = 0
    is_factlen = 0
    no_factlen = 0
    lcount = -1

    final_factual_tweets = 0
    final_fake_tweets = 0
    final_correct_tweets = 0

    # GET VOCABULARY NUMBERS
    for w in vocab.items():
        totalw = w[1][0]
        is_fact = w[1][1]
        not_fact = totalw - is_fact
        wcount_len = wcount_len + totalw
        is_factlen = is_factlen + is_fact
        no_factlen = no_factlen + not_fact
        # ff = [w[0], totalw, is_fact, not_fact]
        # print(ff)
    is_factlen = is_factlen + ( alpha * vlen )
    no_factlen = no_factlen + ( alpha * vlen )

    # GET THE PROBABILTY OF ANY TWEET BEING FACT OR FAKE
    P_tweet_factual = math.log10( fcount / dcount )
    P_tweet_fake = math.log10( (dcount - fcount) / dcount )

    predicted_fact_correct = 0
    predicted_fact_but_fake = 0

    predicted_fake_correct = 0
    predicted_fake_but_fact = 0


    trace_data = []

    trace_filename = "trace_" + trace_file + ".txt"
    eval_filename = "eval_" + trace_file + ".txt"
    if os.path.exists(trace_filename):
        os.remove(trace_filename)
    if os.path.exists(eval_filename):
        os.remove(eval_filename)

    trace_file = open(trace_filename, "a+")
    eval_file = open(eval_filename, "a+")

    # FOR EACH TWEET IN THE TEST DATA
    for d in tdata:
        lcount = lcount + 1
        

        tweet = d[0].lower()
        otweet = d[0]
        tweet_check = d[1]
        tweetID = d[2]
        tweet = tweetFilter(tweet)
        split_tweet = tweet.split(" ")

        # if(lcount > 1):
        #     continue

        for delw in stopwords:
            if delw in split_tweet:
                split_tweet.remove(delw)

        # print(split_tweet)
        # print(vlen)


        P_factual_sum = 0
        P_fake_sum = 0

        # Get sum of probabilities for each word in tweet
        for w in split_tweet:
            if w in vocab.keys():
                
                # totalw = w[1][0]
                num_total = vocab[w][0]
                num_fact = vocab[w][1]
                num_fake = num_total - num_fact + alpha
                num_fact = num_fact + alpha

                P_word_factual = math.log10( num_fact / is_factlen )
                P_factual_sum = P_factual_sum + P_word_factual

                P_word_fake = math.log10( num_fake / no_factlen )
                P_fake_sum = P_fake_sum + P_word_fake
                # print(w)
                # print(num_fact)
                # print(is_factlen)
                # print(P_word_factual)
                


        
        P_fact_total = P_tweet_factual + P_factual_sum
        P_fake_total = P_tweet_fake + P_fake_sum
        tweet_is_fact = P_fact_total > P_fake_total





        isfact_text = ""
        score_text = ""

        tweet_check_text = ""
        tweet_correct_text = "wrong"
        if(tweet_check):
            tweet_check_text = "yes"
        else:
            tweet_check_text = "no"


        if(tweet_is_fact):
            final_factual_tweets = final_factual_tweets + 1
            isfact_text = "yes"
            # score_text = str(P_fact_total)
            score_text = "{:e}".format(P_fact_total)
        else:
            final_fake_tweets = final_fake_tweets + 1
            isfact_text = "no"
            # score_text = str(P_fake_total)
            score_text = "{:e}".format(P_fake_total)
        if(tweet_is_fact == tweet_check):
            final_correct_tweets = final_correct_tweets + 1
            tweet_correct_text = "correct"


        # IF PREDICTED FACT
        if(tweet_is_fact and tweet_check):
            predicted_fact_correct = predicted_fact_correct + 1
        if(tweet_is_fact and not tweet_check):
            predicted_fact_but_fake = predicted_fact_but_fake + 1

        # IF PREDICTED FAKE
        if(not tweet_is_fact and not tweet_check):
            predicted_fake_correct = predicted_fake_correct + 1
        if(not tweet_is_fact and tweet_check):
            predicted_fake_but_fact = predicted_fake_but_fact + 1


        # prff = [tweet_is_fact, tweet_check]
        # print(tweet)
        # print(prff)

        # WRITE TO TRACE FILE
        trace_file.write(
            tweetID + "  " +
            isfact_text + "  " +
            score_text + "  " +
            tweet_check_text + "  " +
            tweet_correct_text + "" +
            "\n"
        )

    trace_file.close()

    # print("predicted_fact_correct: " + str(predicted_fact_correct))
    # print("predicted_fact_but_fake: " + str(predicted_fact_but_fake))
    # print("predicted_fake_correct: " + str(predicted_fake_correct))
    # print("predicted_fake_but_fact: " + str(predicted_fake_but_fact))

    precision_fact = predicted_fact_correct / (predicted_fact_correct + predicted_fake_correct)
    precision_fake = predicted_fake_correct / (predicted_fact_correct + predicted_fake_correct)

    print("precision fact: " + str(precision_fact))
    print("precision fake: " + str(precision_fake))

    recall_fact = predicted_fact_correct / (predicted_fact_correct + predicted_fact_but_fake)
    recall_fake = predicted_fake_correct / (predicted_fake_correct + predicted_fake_but_fact)

    print("recall fact: " + str(recall_fact))
    print("recall fact: " + str(recall_fact))

    f1_fact = 2 * (precision_fact * recall_fact) / (precision_fact + recall_fact)
    f1_fake = 2 * (precision_fake * recall_fake) / (precision_fake + recall_fake)

    print("f1 fact: " + str(f1_fact))
    print("f1 fake: " + str(f1_fake))


    print("Final Factual: " + str(final_factual_tweets))
    print("Final Fake: " + str(final_fake_tweets))

    fcorrect = final_correct_tweets / (final_factual_tweets + final_fake_tweets)

    acc_text = "{:.4f}".format(fcorrect)
    precision_fact_text = "{:.4f}".format(precision_fact)
    precision_fake_text = "{:.4f}".format(precision_fake)
    recall_fact_text = "{:.4f}".format(recall_fact)
    recall_fake_text = "{:.4f}".format(recall_fake)
    f1_fact_text = "{:.4f}".format(f1_fact)
    f1_fake_text = "{:.4f}".format(f1_fake)

    print("Final Correct: " + str(final_correct_tweets) + "/" +  str(final_factual_tweets + final_fake_tweets) + " => " + str(fcorrect))

    eval_file.write(
        acc_text + "\n" + 
        precision_fact_text + "  " + precision_fake_text + "\n" + 
        recall_fact_text + "  " + recall_fake_text + "\n" + 
        f1_fact_text + "  " + f1_fake_text
    )
    eval_file.close()