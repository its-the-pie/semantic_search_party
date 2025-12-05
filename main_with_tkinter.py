"""
Semantic Search Party
CS 1210 Final Project
Amelia Partlow, Yasmin Farley, Nina Scarpato

Description: Game like Contexto and Semantle, where user tries to guess a secret word and receives semantic similarity feedback from each guess. 
Features: 
    - levels that get harder as they increment
        - harder means word gets rarer and longer
            - to assess the rareness of a word, we imported wordfreq
        - the number of levels is controlled by a constant that can always be changed
    - Semantic similarity scores between the secret word and each guess
        - Used spacy to get the scores
            - imported a spacy pretrained model that includes word vectors
            -  spacy gets the similarity score by comparing those word vectors using cosine similarity
    - Tkinter GUI
    -  Hints and letter reveal buttons to improve user experience
    - Points system based on user performance 

Libraries:
    - spacy with the model: en_core_web_lg --> to get semantic similarity
    - wordfreq to determine how common a word is and use that score (higher score meaning more common) to sort level difficulty
    - tkinter for visuals
    -tkmacosx because tkinter button widgets had issues on macOS
Resources: 
    - wordfreq document https://pypi.org/project/wordfreq/
    - spacy website https://spacy.io/
    - spacy document https://pypi.org/project/spacy/
    - spacy tutorial https://codesignal.com/learn/courses/linguistics-for-token-classification-in-spacy/lessons/understanding-semantic-similarity-in-nlp-with-spacy 
    - tkinter document https://docs.python.org/3/library/tkinter.html 
    - tkinter tutorials
        - https://www.youtube.com/watch?v=epDKamC-V-8 
        - https://www.geeksforgeeks.org/python/python-gui-tkinter/ 
        - https://realpython.com/python-gui-tkinter/ 
        - https://www.pythontutorial.net/tkinter/tkinter-after/ 
        - https://tkdocs.com/tutorial/text.html 
    - tkmacosx document https://pypi.org/project/tkmacosx/ 
    - Stack Overflow for specific questions that came up in debugging
        
"""


from wordfreq import word_frequency
import random 
import spacy  
import en_core_web_lg
import tkinter as tk
from tkmacosx import Button

# getting word frequencies from a list of words
def get_freq():
    words_only = []
    with open("cleaned_word_list.txt", "r") as word_list:
        word_list.readline()
        for line in word_list:
            word = line.strip()
            words_only.append(word)    

    word_freq_list = []
    for word in words_only:
        freq = word_frequency(word, 'en', wordlist='best', minimum=0.0)
        word_freq_list.append((word, freq))
    return word_freq_list, words_only

#scaling frequencies to be between 0 and 1
def scale(word_freq_list):
    freqs = []
    for word, freq in word_freq_list:
        freqs.append(freq)

    max_freq = max(freqs)
    min_freq = min(freqs)
    scaled_freqs = []
    for word, freq in word_freq_list:
        scaled_freq = (freq - min_freq) / (max_freq - min_freq)
        scaled_freqs.append((scaled_freq, word))
    return scaled_freqs

# adding in the length of each word as a factor that determines the difficulty level
def difficulty_score(scaled_freqs):
    max_len = 0
    for freq, word in scaled_freqs:
        if len(word) > max_len:
            max_len = len(word)

    scores = []
    for freq, word in scaled_freqs:
        difficulty = (1 - freq) + (len(word) / max_len)
        scores.append((difficulty, word))
    return scores

# sorts the words into levels corresponding to their difficulty based on the number of total levels in the game
def make_bins(scores, NUM_LEVELS):
    sorted_words = sorted(scores)
    bin_size = len(sorted_words) // NUM_LEVELS
    bin_dict = {}
    for i in range(NUM_LEVELS):
        if i == NUM_LEVELS - 1:
            words_in_bin = sorted_words[i * bin_size:]
        else:
            words_in_bin = sorted_words[i * bin_size : (i + 1) * bin_size]

        word_list = []
        for w in words_in_bin:
            word_list.append(w[1])
        bin_dict[i + 1] = word_list
    return bin_dict

# choosing a word based on the difficulty of the current level
def choose_word(bin_dict, level):
    word = random.choice(bin_dict[level])
    return word

# using spacy to get similarity scores
def semantic_similarity(doc1, guess, nlp):
    doc2 = nlp(guess)
    if doc1.has_vector and doc2.has_vector:
        return doc1.similarity(doc2)
    else: 
        return 0.0 

#made a function to print to the GUI because tkinter doesn't use the typical text based print()
def tk_print(msg, output_box):
    msg = msg.strip()
    output_box.configure(state="normal")
    output_box.insert(tk.END, msg + "\n")
    output_box.see(tk.END)
    output_box.configure(state="disabled")


# resetting game stats and visuals for a new round, printing stats if game over
def start_round(data, nlp, output_box, frame):
    if "restart_button" in data and data["restart_button"]:
        data["restart_button"].destroy()
        data["restart_button"] = None
         
    output_box.configure(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert("1.0", "SEMANTIC SEARCH PARTY\n")
    output_box.tag_add("title", "1.0", "2.0")
    output_box.tag_configure("title",font=("Times New Roman", 30, "bold"), foreground="white")
    output_box.insert(tk.END, "\n")
    output_box.delete("3.0", tk.END)
    output_box.configure(state="disabled")
    
    if data["level"] > data["NUM_LEVELS"]:
        if data["last_lev"]:
            tk_print(f'Forfeited. The word was: {data["sw"]}', output_box)
        tk_print("Congratulations! You've completed all the levels!", output_box)
        tk_print(f'Total Points: {data["tp"]} / {data["MAX_POINTS"] * data["NUM_LEVELS"]}', output_box)
        tk_print(f'Total Guesses: {data["tg"]}', output_box)
        tk_print(f'Total Hints Used: {data["th"]} (Hint Button)', output_box)
        tk_print(f'Total Letters Revealed: {data["total_letters_given"]} (Letter Reveal Button)', output_box)
        tk_print("To play again press restart", output_box)
  
        restart_button = Button(frame, text="Restart Game", bg="green", fg="white", font=("Times New Roman", 14), command=lambda: restart(data, nlp, output_box, frame))
        restart_button.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=5, padx=5)
        data["restart_button"] = restart_button
        return
  
    data["sw"] = choose_word(data["bins"], data["level"])
    data["rp"] = data["MAX_POINTS"]
    data["rg"] = 0
    data["rh"] = 0
    data["already_guessed"] = set()
    data["doc1"] = nlp(data["sw"])
    data["max_ss"] = 0
    data["ss_list"] = []
    data["num_guess"] = 0
    data["hints_given"] = set()
    data["letters_given"] = 0
    data["restart_button"] = None
    data["last_lev"] = False


    for word in data["words_only"]:
        ss = semantic_similarity(data["doc1"], word, nlp)
        data["ss_list"].append([word, ss])        

    tk_print("-" * 67, output_box)
    guess_entry.bind("<Return>", lambda e: on_guess(data, nlp, output_box, guess_entry, frame))
     
    tk_print(f'Level {data["level"]}', output_box)
    tk_print("Start Guessing!!", output_box)
    tk_print("-" * 67, output_box)
    box(output_box)

# handles the user's guess 
def play_round(guess, data, nlp, output_box):
    guess = guess.lower()

    if guess in data["already_guessed"]:
        tk_print("Already guessed", output_box)
        return
    else: 
        data["already_guessed"].add(guess)
        secret_word = data["sw"]
        doc1 = data["doc1"]
        max_ss = data["max_ss"]
        ss_list = data["ss_list"]
        round_hints = data["rh"]

        if guess == secret_word.lower():
            round_guesses = len(data["already_guessed"])
            round_points = data["rp"] 
                
            if round_points < 0:
                round_points = 0

            add_guess(data, output_box, guess, 1.0)
            tk_print("Correct!", output_box)
            tk_print(f"Points Earned: {round_points} / {data['MAX_POINTS']}", output_box)
            tk_print(f"Number of Guesses: {round_guesses}", output_box) 
            tk_print(f"Number of Hints Used: {round_hints} (Hint Button)", output_box) 
            tk_print(f"Number of Letters Revealed: {data['letters_given']} (Letter Reveal Button)", output_box) 

            data["rp"] = round_points
            data["rg"] = round_guesses
            data["tp"] += data["rp"]
            data["tg"] += data["rg"]
            data["th"] += data["rh"]
            data["trc"] += 1
            data["level"] += 1

            return True, round_points, round_guesses, round_hints
        else:
            similarity = semantic_similarity(doc1, guess, nlp)
            # making feedback more user friendly by ensuring similarity isn't negative
            if similarity < 0:
                similarity = 0
                
            if similarity > 0.9999 and guess != secret_word.lower():
                tk_print("Almost there! That was practically a perfect match!", output_box)
            else:        
                add_guess(data, output_box, guess, similarity)

            if similarity > max_ss:
                data["max_ss"] = similarity

# if they hit the restart button after a game
def restart(data, nlp, output_box, frame):
    data["level"] = 1
    data["tp"] = 0
    data["tg"] = 0
    data["th"] = 0
    data["trc"] = 0
    start_round(data, nlp, output_box, frame)

# Gives hints by revealing a word slightly more semantically similar to the secret word than previous guesses or hints
# upper bound used for progressively easier hints 
def hints(data, output_box):
    upper_bound = data["max_ss"] + 0.2 * data["rh"]
        
    candidates = [] 
    for word, ss in data["ss_list"]: 
        if word != data["sw"] and ss > data["max_ss"] and ss < upper_bound and word not in data["hints_given"]:
            candidates.append([word, ss]) 

    while len(candidates) == 0: 
        upper_bound += 0.05 
        if upper_bound >= 1: 
            for word, ss in data["ss_list"]: 
                if ss > data["max_ss"]: 
                    max_word = word 
                    data["max_ss"] = ss 
                    tk_print(f"Closest Word: {max_word}", output_box) 
                    return 
                else: 
                    tk_print("No more hints available", output_box)
                    return
                        
        else:
            for word, ss in data["ss_list"]: 
                if ss > data["max_ss"] + 0.1 and ss < upper_bound: 
                    candidates.append([word, ss]) 
                                
    hint = random.choice(candidates) 
    hint_word = hint[0] 
    hint_ss = hint[1] 
    data["hints_given"].add(hint_word)
    data["max_ss"] = hint_ss
    data["rh"] += 1
    data["rp"] -= 5
    if data["rp"] < 0:
        data["rp"] = 0

    tk_print(f"Hint:\n", output_box)
    add_guess(data, output_box, hint_word, hint_ss)

# reveals one more letter from the secret word and avoids revealing the whole word 
def letter_reveal(data, output_box): 
    given = data["letters_given"]

    if given >= len(data["sw"]) - 2:
        tk_print("No more letter reveal hints available for this round", output_box)

    else:
        given += 1
        data["letters_given"] = given
        data["total_letters_given"] += 1
        letters = data["sw"][:given]
        remain = len(data["sw"]) - given
        data["rp"] -= 10
        if data["rp"] < 0:
            data["rp"] = 0
    
        tk_print(f'Letter Reveal: {letters + "_ " * remain}', output_box)

def on_guess(data, nlp, output_box, guess_entry, frame):
    guess = guess_entry.get().strip()
    if not guess or guess == "Enter a word...":
        return
    
    guess_entry.delete(0, tk.END)   
    result = play_round(guess, data, nlp, output_box) 
   
    if result and result[0] is True: 
        output_box.after(12000, lambda: start_round(data, nlp, output_box, frame)) # pause to show round stats before new round starts



def on_hint(data, nlp, output_box):
    hints(data, output_box)

# reveals secret word when user hits forfeit button and pauses briefly to show the answer
def on_forfeit(data, nlp, output_box, frame):
    if data["level"] == data["NUM_LEVELS"]:
        data["last_lev"] = True
    else:
        tk_print(f'Forfeited. The word was: {data["sw"]}', output_box)
        data["last_lev"] = False

    data["rp"] = 0
    data["rg"] = len(data["already_guessed"])
    data["level"] += 1
    output_box.after(100, lambda: start_round(data, nlp, output_box, frame))


def box(output_box):
    output_box.configure(state="normal")
    topic = "#\tGuess\tSimilarity\n"
    output_box.insert("end", topic)
    output_box.insert("end", "-" * 67 + "\n")
    output_box.configure(state="disabled")

# Inserts the guess and feedback into the output box
def add_guess(data, output_box, word, ss):
    data["num_guess"] += 1
    num_guess = data["num_guess"]

    output_box.configure(state="normal")

    if ss < 0.33:
        color = "red"
    elif ss < 0.66:
        color = "orange"
    else:
        color = "green"

    if color not in output_box.tag_names():
        output_box.tag_configure(color, foreground=color)

    row_txt = f"{num_guess}\t{word.strip()}\t{ss:.2f}\n"
    output_box.insert("end", row_txt, color)
    output_box.configure(state="disabled")
    output_box.see("end")

# for placeholder text in entry box
def temp_msg(entry, msg):
    entry.insert(0, msg)
    entry.configure(fg="grey")

    def on_click(event):
        if entry.get() == msg:
            entry.delete(0, tk.END)
            entry.configure(fg="black")
    def click_out(event):
        if entry.get() == "":
            entry.insert(0, msg)
            entry.configure(fg="grey")
    entry.bind("<FocusIn>", on_click)
    entry.bind("<FocusOut>", click_out)


if __name__ == "__main__":  
    nlp = en_core_web_lg.load()
    NL = 3
    MP = 100
    word_freq_list, words_only = get_freq()
    bins = make_bins(difficulty_score(scale(word_freq_list)), NL)

    # decided to use a dictionary for game stats and counters because function calls were getting messy 
    data = {
        "NUM_LEVELS": NL,
        "MAX_POINTS": MP,
        "level": 1,
        "tp": 0,        # total points
        "tg": 0,        # total guesses
        "th": 0,        # total hints used
        "trc": 0,       # total rounds completed
        "rp": 0,        # current round points
        "rg": 0,        # current round guesses
        "rh": 0,        # current round hints used
        "already_guessed": set(),       # tracking words already guessed in the round
        "sw": "",       # current secret word
        "doc1": 0,      # current secret word spacy doc
        "max_ss": 0,        # max semantic similarity score in current round
        "ss_list": [],      # list of (word, similarity) tuples 
        "bins": bins,       # words per difficulty level
        "words_only": words_only,       # all words in dataset
        "hints_given": set(),       # words given as hints
        "letters_given": 0,         # num letters revealed
        "total_letters_given": 0,
        "num_guess": 0,         # sequential number for display of each guess
        "restart_button": None,         # whether restart button has been pressed or not
        "last_lev": False,      # True when last level reached     
    }
    
    # tkinter window 
    root = tk.Tk()
    root.title("Semantic Search Party") 
    root.configure(bg="navy")
    
    frame = tk.Frame(root, bg="navy")
    frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # 4 total columns, evenly distributed
    for i in range(4):
        frame.columnconfigure(i, weight=1)
    frame.rowconfigure(0, weight=1)

    output_box = tk.Text(frame, width=50, height=15, bg="black", fg="white", font=("Times New Roman", 18), selectbackground="purple", selectforeground="white")
    output_box.grid(row=0, column=0, columnspan=4, sticky="nsew")
    output_box.configure(state="disabled")
    output_box.configure(tabs=("60p", "250p")) # for column alignment


    guess_entry = tk.Entry(frame,bg="white", fg="black", font=("Times New Roman", 18), insertbackground="black")
    guess_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,5))
    temp_msg(guess_entry, "Enter a word...")

    guess_button = Button(frame, text="Guess", bg="blue", fg="white", font=("Times New Roman", 18), activebackground="darkblue", activeforeground="white", highlightbackground="blue", highlightthickness=1, command=lambda: on_guess(data, nlp, output_box, guess_entry, frame))
    guess_button.grid(row=1, column=2, columnspan=2, sticky="ew", pady=(0,5))
    

    hint_button = Button(frame, text="Hint (-5)", bg="purple", fg="white", font=("Times New Roman", 14), activebackground="indigo", activeforeground="white", highlightbackground="purple", highlightthickness=1,command=lambda: on_hint(data, nlp, output_box), width=10)
    hint_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

    forfeit_button = Button(frame, text="Forfeit Round", width=10, bg="orange", fg="white", font=("Times New Roman", 14), activebackground="darkorange", activeforeground="white", highlightbackground="orange", highlightthickness=1,command=lambda: on_forfeit(data, nlp, output_box, frame))
    forfeit_button.grid(row=2, column=2, sticky="ew", padx=5, pady=5) 

    quit_button = Button(frame, text="Quit", bg="red", fg="white", font=("Times New Roman", 14), activebackground="darkred", activeforeground="white", highlightbackground="red", highlightthickness=1,command=root.destroy, width=10)
    quit_button.grid(row=2, column=3, sticky="ew", padx=5, pady=5) 

    reveal_button = Button(frame, text="Reveal Letter (-10)", bg="green", fg="white", font=("Times New Roman", 14), activebackground="darkgreen", activeforeground="white", highlightbackground="green", highlightthickness=1, command=lambda: letter_reveal(data, output_box), width=10)
    reveal_button.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    start_round(data, nlp, output_box, frame)
    root.mainloop()

    

       