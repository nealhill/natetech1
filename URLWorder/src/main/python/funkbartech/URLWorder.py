from flask import Flask, redirect, url_for, render_template, request, session, flash

from lxml import html
import re
import requests

app = Flask(__name__)
app.secret_key = "FUNK_BAR_TECH_SECRET_KEY_12345678"


@app.route("/")
def home():
    if "historyList" in session:
        session["historyList"] = None

    return render_template("index.html")


@app.route("/urlresults", methods=["POST", "GET"])
def urlresults():
    if "historyList" in session:
        historyList = session["historyList"]
        if historyList is None:
            print("historyList found=None value in session. Making empty list.".format(str(historyList)))
            historyList = {}
        print("historyList found={}.".format(str(historyList)))
    else:
        print("No historyList found. Empty")
        historyList = {}

    if request.method == "POST":
        url = request.form["targetURL"]

        if goodURL(url):
            print(f"good url targetURL={url}")
            session["url"] = url

            historyList[url] = 1
            session["historyList"] = historyList
            print("Appended to history url={}".format(str(historyList), url))

            if "url" in session:
                targetURL = session["url"]
                print(f"urlresults(): targetURL={targetURL}")
                wordList = getWebPageWordsLXML(targetURL)
                return render_template("urlresults.html", url=targetURL, results=wordList, history=historyList)
            else:
                print("No URL found in session")
        else:
            flash("Bad URL={}. Try using 'http://' or 'https://'".format(url), "error")
            print("Bad URL={}".format(url))

    return render_template("urlresults.html", history=historyList)


def goodURL(url):
    return url is not None and (url.lower().startswith("http://") or url.lower().startswith("https://"))


def getWebPageWordsLXML(url):
    # List of words and their word count
    wordList = {}

    # Get the web page and root of DOM tree
    page = requests.get(url)
    tree = html.fromstring(page.content)
    # Pre-compile REGEX to match individual words
    reWords = re.compile(r"([A-Za-z]+)")

    # XPath search on all text (CDATA) in HTML body
    xPathResults = tree.xpath('/html/body//text()')

    # For each text (CDATA) node, get the text, split into individual words and tally
    for textNode in xPathResults:
        # Get individual lines of text, tally each word in it
        textParts = str(textNode).split("\n")
        for text in textParts:
            # No whitespace needed in text
            text = text.strip()
            # If it's a non-empty string, tally the word
            if len(text) > 0:
                # REGEX match all the word in text line
                matchedWords = reWords.findall(text)

                # If there are words in the text line, for each word: tally their occurrence
                if len(matchedWords) > 1:
                    for matchedWord in matchedWords:
                        matchedWord = str(matchedWord).lower()
                        # Word to tally already in word list? Then increment count
                        if matchedWord in wordList:
                            wordCount = wordList[matchedWord]
                            wordCount = wordCount + 1
                            wordList[matchedWord] = wordCount
                        # Else (first time word encountered), tally count for the word is 1
                        else:
                            wordList[matchedWord] = 1
    return wordList


if __name__ == "__main__":
    app.run(debug=True)
