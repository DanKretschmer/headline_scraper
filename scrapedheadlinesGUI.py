import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup
import openpyxl
from collections import Counter
import re
from datetime import datetime

# Create a list to store scraped headlines and most frequent words
scraped_headlines = []

# Function to scrape and collect data
def scrape_and_collect():
    global scraped_headlines  # Use the global list

    url = entry.get()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    headlines = soup.find_all(class_="card--lite")

    scraped_headlines = []  # Clear the list

    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    headlines_text = f"Headlines for {current_datetime}"

    
    for headline in headlines:
        headline_text = headline.find('a').get_text()
        scraped_headlines.append(headline_text)

    scraped_headlines.insert(0, headlines_text) 

    # Update the text widget
    text_widget.config(state=tk.NORMAL)  # Enable the text widget for editing
    text_widget.delete(1.0, tk.END)  # Clear the existing content
    text_widget.insert(tk.END, '\n'.join(scraped_headlines))  # Insert the scraped data
    text_widget.config(state=tk.DISABLED)  # Disable the text widget for editing

    # Calculate and display the most frequent words
    update_most_frequent_words()

# Function to save scraped data to an XLSX file
def save_to_excel():
    warning_label =""
    if not scraped_headlines:
        # Show a warning dialog if there's nothing to save
        warning_label.config(text="Nothing to save.", fg="red")
        return

    # Ask the user to select a file path for saving
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

    if file_path:
        # Create an XLSX file and save the data
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Scraped Headlines"
        for i, headline in enumerate(scraped_headlines, start=1):
            sheet.cell(row=i, column=1, value=headline)
        workbook.save(file_path)
        warning_label.config(text=f"Data saved to {file_path}", fg="green")

# Function to calculate and display the most frequent words
def update_most_frequent_words():
    if not scraped_headlines:
        return  # No headlines to analyze

    # Tokenize headlines and remove stopwords
    words = []
    stopwords = ["the", "and", "in", "to", "of", "a", "for", "on", "with", "by", "0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2", "a3", "a4", "ab", "able", "about", "above", "abst", "ac", "accordance", "according", "accordingly", "across", "act", "actually", "ad", "added", "adj", "ae", "af", "affected", "affecting", "affects", "after", "afterwards", "ag", "again", "against", "ah", "ain", "ain't", "aj", "al", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "ao", "ap", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately", "ar", "are", "aren", "arent", "aren't", "arise", "around", "as", "a's", "aside", "ask", "asking", "associated", "at", "au", "auth", "av", "available", "aw", "away", "awfully", "ax", "ay", "az", "b", "b1", "b2", "b3", "ba", "back", "bc", "bd", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bi", "bill", "biol", "bj", "bk", "bl", "bn", "both", "bottom", "bp", "br", "brief", "briefly", "bs", "bt", "bu", "but", "bx", "by", "c", "c1", "c2", "c3", "ca", "call", "came", "can", "cannot", "cant", "can't", "cause", "causes", "cc", "cd", "ce", "certain", "certainly", "cf", "cg", "ch", "changes", "ci", "cit", "cj", "cl", "clearly", "cm", "c'mon", "cn", "co", "com", "come", "comes", "con", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldnt", "couldn't", "course", "cp", "cq", "cr", "cry", "cs", "c's", "ct", "cu", "currently", "cv", "cx", "cy", "cz", "d", "d2", "da", "date", "dc", "dd", "de", "definitely", "describe", "described", "despite", "detail", "df", "di", "did", "didn", "didn't", "different", "dj", "dk", "dl", "do", "does", "doesn", "doesn't", "doing", "don", "done", "don't", "down", "downwards", "dp", "dr", "ds", "dt", "du", "due", "during", "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", "ed", "edu", "ee", "ef", "effect", "eg", "ei", "eight", "eighty", "either", "ej", "el", "eleven", "else", "elsewhere", "em", "empty", "en", "end", "ending", "enough", "entirely", "eo", "ep", "eq", "er", "es", "especially", "est", "et", "et-al", "etc", "eu", "ev", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "ey", "f", "f2", "fa", "far", "fc", "few", "ff", "fi", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "fix", "fj", "fl", "fn", "fo", "followed", "following", "follows", "for", "former", "formerly", "forth", "forty", "found", "four", "fr", "from", "front", "fs", "ft", "fu", "full", "further", "furthermore", "fy", "g", "ga", "gave", "ge", "get", "gets", "getting", "gi", "give", "given", "gives", "giving", "gj", "gl", "go", "goes", "going", "gone", "got", "gotten", "gr", "greetings", "gs", "gy", "h", "h2", "h3", "had", "hadn", "hadn't", "happens", "hardly", "has", "hasn", "hasnt", "hasn't", "have", "haven", "haven't", "having", "he", "hed", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "here's", "hereupon", "hers", "herself", "hes", "he's", "hh", "hi", "hid", "him", "himself", "his", "hither", "hj", "ho", "home", "hopefully", "how", "howbeit", "however", "how's", "hr", "hs", "http", "hu", "hundred", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ibid", "ic", "id", "i'd", "ie", "if", "ig", "ignored", "ih", "ii", "ij", "il", "i'll", "im", "i'm", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc", "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "insofar", "instead", "interest", "into", "invention", "inward", "io", "ip", "iq", "ir", "is", "isn", "isn't", "it", "itd", "it'd", "it'll", "its", "it's", "itself", "iv", "i've", "ix", "iy", "iz", "j", "jj", "jr", "js", "jt", "ju", "just", "k", "ke", "keep", "keeps", "kept", "kg", "kj", "km", "know", "known", "knows", "ko", "l", "l2", "la", "largely", "last", "lately", "later", "latter", "latterly", "lb", "lc", "le", "least", "les", "less", "lest", "let", "lets", "let's", "lf", "like", "liked", "likely", "line", "little", "lj", "ll", "ll", "ln", "lo", "look", "looking", "looks", "los", "lr", "ls", "lt", "ltd", "m", "m2", "ma", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "mightn", "mightn't", "mill", "million", "mine", "miss", "ml", "mn", "mo", "more", "moreover", "most", "mostly", "move", "mr", "mrs", "ms", "mt", "mu", "much", "mug", "must", "mustn", "mustn't", "my", "myself", "n", "n2", "na", "name", "namely", "nay", "nc", "nd", "ne", "near", "nearly", "necessarily", "necessary", "need", "needn", "needn't", "needs", "neither", "never", "nevertheless", "new", "next", "ng", "ni", "nine", "ninety", "nj", "nl", "nn", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "novel", "now", "nowhere", "nr", "ns", "nt", "ny", "o", "oa", "ob", "obtain", "obtained", "obviously", "oc", "od", "of", "off", "often", "og", "oh", "oi", "oj", "ok", "okay", "ol", "old", "om", "omitted", "on", "once", "one", "ones", "only", "onto", "oo", "op", "oq", "or", "ord", "os", "ot", "other", "others", "otherwise", "ou", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "ow", "owing", "own", "ox", "oz", "p", "p1", "p2", "p3", "page", "pagecount", "pages", "par", "part", "particular", "particularly", "pas", "past", "pc", "pd", "pe", "per", "perhaps", "pf", "ph", "pi", "pj", "pk", "pl", "placed", "please", "plus", "pm", "pn", "po", "poorly", "possible", "possibly", "potentially", "pp", "pq", "pr", "predominantly", "present", "presumably", "previously", "primarily", "probably", "promptly", "proud", "provides", "ps", "pt", "pu", "put", "py", "q", "qj", "qu", "que", "quickly", "quite", "qv", "r", "r2", "ra", "ran", "rather", "rc", "rd", "re", "readily", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "research-articl", "respectively", "resulted", "resulting", "results", "rf", "rh", "ri", "right", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "run", "rv", "ry", "s", "s2", "sa", "said", "same", "saw", "say", "saying", "says", "sc", "sd", "se", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "sf", "shall", "shan", "shan't", "she", "shed", "she'd", "she'll", "shes", "she's", "should", "shouldn", "shouldn't", "should've", "show", "showed", "shown", "showns", "shows", "si", "side", "significant", "significantly", "similar", "similarly", "since", "sincere", "six", "sixty", "sj", "sl", "slightly", "sm", "sn", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "sp", "specifically", "specified", "specify", "specifying", "sq", "sr", "ss", "st", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure", "sy", "system", "sz", "t", "t1", "t2", "t3", "take", "taken", "taking", "tb", "tc", "td", "te", "tell", "ten", "tends", "tf", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "there's", "thereto", "thereupon", "there've", "these", "they", "theyd", "they'd", "they'll", "theyre", "they're", "they've", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "thou", "though", "thoughh", "thousand", "three", "throug", "through", "throughout", "thru", "thus", "ti", "til", "tip", "tj", "tl", "tm", "tn", "to", "together", "too", "took", "top", "toward", "towards", "tp", "tq", "tr", "tried", "tries", "truly", "try", "trying", "ts", "t's", "tt", "tv", "twelve", "twenty", "twice", "two", "tx", "u", "u201d", "ue", "ui", "uj", "uk", "um", "un", "under", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "uo", "up", "upon", "ups", "ur", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "ut", "v", "va", "value", "various", "vd", "ve", "ve", "very", "via", "viz", "vj", "vo", "vol", "vols", "volumtype", "vq", "vs", "vt", "vu", "w", "wa", "want", "wants", "was", "wasn", "wasnt", "wasn't", "way", "we", "wed", "we'd", "welcome", "well", "we'll", "well-b", "went", "were", "we're", "weren", "werent", "weren't", "we've", "what", "whatever", "what'll", "whats", "what's", "when", "whence", "whenever", "when's", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "where's", "whereupon", "wherever", "whether", "which", "while", "whim", "whither", "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "who's", "whose", "why", "why's", "wi", "widely", "will", "willing", "wish", "with", "within", "without", "wo", "won", "wonder", "wont", "won't", "words", "world", "would", "wouldn", "wouldnt", "wouldn't", "www", "x", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y", "y2", "yes", "yet", "yj", "yl", "you", "youd", "you'd", "you'll", "your", "youre", "you're", "yours", "yourself", "yourselves", "you've", "yr", "ys", "yt", "z", "zero", "zi", "zz",]  # Add more stopwords as needed
    for headline in scraped_headlines:
        headline = re.sub(r'[^\w\s]', '', headline)  # Remove punctuation
        words.extend(headline.lower().split())
    words = [word for word in words if word not in stopwords]

    numbers = []
    for headline in scraped_headlines:
        found_numbers = re.findall(r'\b\d+[,]*\d*\b', headline)  # Match whole numbers, potentially with commas
        numbers.extend(found_numbers)

    number_counts = Counter(numbers)
    most_frequent_numbers = number_counts.most_common(10)  # Get the top 10 numbers


    # Calculate the most frequent words
    word_counts = Counter(words)
    most_frequent_words = word_counts.most_common(10)  # Get the top 10 words

    # Display most frequent words
    # Display most frequent words
    frequent_words_text.config(state=tk.NORMAL)  # Enable the text widget for editing
    frequent_words_text.delete(1.0, tk.END)  # Clear the existing content
    frequent_words_text.insert(tk.END, "Frequent words:\n", "wrap")
    for word, count in most_frequent_words:
        frequent_words_text.insert(tk.END, f"{word}: {count} times\n", "wrap")
    frequent_words_text.insert(tk.END, "\nFrequent numbers:\n", "wrap")
    for number, count in most_frequent_numbers:
        frequent_words_text.insert(tk.END, f"{number}\n", "wrap")
    frequent_words_text.config(state=tk.DISABLED)  # Disable the text widget for editing


# Create the main window
root = tk.Tk()
root.title("Web Scraper")

# Calculate the desired window size (75% of the screen width)
screen_width = root.winfo_screenwidth()
window_width = int(screen_width * 0.75)

# Set the window size and position it in the center of the screen
root.geometry(f"{window_width}x400+{int((screen_width - window_width) / 2)}+0")

# Create an entry field for the URL
label = tk.Label(root, text="News URL:")
label.place(x=10, y=10)
label = tk.Label(root, text="https://lite.cnn.com")
label.place(x=10, y=40)

entry = tk.Entry(root, width=30)
entry.insert(0, "https://lite.cnn.com")  # Default URL
#entry.place(x=10, y=40)

# Create a "Scrape it" button
scrape_button = tk.Button(root, text="Scrape", command=scrape_and_collect)
scrape_button.place(x=10, y=70)

# Create a "Save it" button
save_button = tk.Button(root, text="Save Spreadsheet", command=save_to_excel)
save_button.place(x=100, y=70)

# Calculate the desired text widget size for the scraped headlines (65% of the GUI width)
text_widget_width = int(window_width * 0.80)

# Create a scrolled text widget for displaying scraped headlines
text_widget = scrolledtext.ScrolledText(root, width=text_widget_width, height=10, state=tk.DISABLED, wrap=tk.WORD)
text_widget.place(x=10, y=100, width=text_widget_width, height=300)


# Calculate the desired text widget size for the frequent words (15% of the GUI width)
frequent_words_text_width = int(window_width * 0.18)

# Create a scrolled text widget for displaying most frequent words
frequent_words_text = scrolledtext.ScrolledText(root, width=frequent_words_text_width, height=10, state=tk.DISABLED)
frequent_words_text.place(x=text_widget_width + 20, y=100, width=frequent_words_text_width, height=300)

# Start the Tkinter main loop
root.mainloop()
