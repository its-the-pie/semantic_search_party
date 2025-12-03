from wordfreq import word_frequency
import random 
import spacy  
import en_core_web_lg
import tkinter as tk
from tkinter import ttk

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

def choose_word(bin_dict, level):
    word = random.choice(bin_dict[level])
    return word

def semantic_similarity(doc1, guess, nlp):
    doc2 = nlp(guess)
    num = doc1.similarity(doc2)
    return num
 

def play_game(data, bins, nlp, words_only):
    while data["level"] <= data["NUM_LEVELS"]:  
        solved, round_points, round_guesses, round_hints = start_round(data, bins, nlp, words_only)
        if solved:
            data["trc"] += 1
        
        data["tp"] += data["rp"]
        data["tg"] += data["rg"]
        data["th"] += data["rh"]
        data["level"] += 1  
    print(f'Game Over!\nScore: {data["tp"]}/ {data["NUM_LEVELS"] * data["MAX_POINTS"]} points\nTotal Rounds Correct: {data["trc"]} / {data["NUM_LEVELS"]}\nTotal Number of Guesses: {data["tg"]}\nTotal Number of Hints: {data["th"]}')

def start_round(data, bins, nlp, words_only):
    data["sw"] = choose_word(bins, data["level"])
    print(data["sw"])
    print(f'Level {data["level"]}')

    data["rp"] = data["MAX_POINTS"]
    data["rg"] = 0
    data["rh"] = 0
    data["already_guessed"] = set()

    result = play_round(data, nlp, words_only)
    return result


def play_round(data, nlp, words_only):
    round_points = data["MAX_POINTS"]
    secret_word = data["sw"]
    round_hints = data["rh"]
    round_guesses = data["rg"]
    doc1 = nlp(secret_word)
    max_ss = 0
    ss_list = []


    while True: 
        guess = input("Make a guess: ").lower()

        if guess in data["already_guessed"]:
            print("Already guessed")
        else: 
            data["already_guessed"].add(guess)

            if guess == secret_word.lower():
                round_guesses = len(data["already_guessed"])
                extra = round_guesses - 1
                round_points -= extra 
                
                if round_points < 0:
                    round_points = 0

                print(f"Correct!\nPoints Earned: {round_points}\nNumber of guesses: {round_guesses}\nNumber of Hints: {round_hints}") 
                
                data["rp"] = round_points
                data["rg"] = round_guesses
                data["rh"] = round_hints
                return True, round_points, round_guesses, round_hints
            else:
                similarity = semantic_similarity(doc1, guess, nlp)

                if similarity > 0.9999 and guess != secret_word.lower():
                    print("Almost there! That was practically a perfect match!")
                else:        
                    print(f"Similarity: {similarity:.2f}")

                if similarity > max_ss:
                    max_ss = similarity

                
                hint_option = input("Need a hint? (y/n): ").lower()    
                if hint_option =="y":
                    if ss_list == []:
                        for word in words_only: 
                            ss = semantic_similarity(doc1, word, nlp)
                            ss_list.append([word, ss])

                    round_hints += 1
                    round_points -= 2

                    if round_points < 0:
                        round_points = 0
                    
                    upper_bound = max_ss + 0.1 * round_hints
                    w, ss = hints(max_ss, ss_list, upper_bound)
                    max_ss = ss
                
                forfeit = input("Would you like to forfeit the round? (y/n)").lower()
                if forfeit == "y":
                    print(f"Forfeited. The word was: {secret_word}")
                    round_points = 0
                    data["rp"] = round_points
                    data["rg"] = len(data["already_guessed"])
                    data["rh"] = round_hints
                    return False, round_points, len(data["already_guessed"]), round_hints
               
def hints(max_ss, ss_list, upper_bound): 
    candidates = [] 
    for i in ss_list: 
        word = i[0] 
        ss = i[1] 
        if ss > max_ss and ss < upper_bound:
            candidates.append([word, ss]) 
            while len(candidates) == 0: 
                upper_bound += .05 
                if upper_bound >= 1: 
                    for i in ss_list: 
                        if i[1] > max_ss: 
                            max_word = i[0] 
                            max_ss = i[1] 
                            print(f"Closest Word: {max_word}") 
                            return max_word, max_ss 
                        for i in ss_list: 
                            word = i[0] 
                            ss = i[1]
                            if ss > max_ss and ss < upper_bound: 
                                candidates.append([word, ss]) 
                                hint = random.choice(candidates) 
                                hint_word = hint[0] 
                                hint_ss = hint[1] 
                                print(f"Hint: {hint_word}, Similarity: {hint_ss:.2f}") 
                                return hint_word, hint_ss




        
    


if __name__ == "__main__":  
    nlp = en_core_web_lg.load()
    NL = 2
    MP = 100
    word_freq_list, words_only = get_freq()
    bins = make_bins(difficulty_score(scale(word_freq_list)), NL)


    data = {
        "NUM_LEVELS": NL,
        "MAX_POINTS": MP,
        "level": 1,
        "tp": 0,
        "tg": 0,
        "th": 0,
        "trc": 0,
        "rp": 0,
        "rg": 0,
        "rh": 0,
        "already_guessed": set(),
        "sw": ""
    }

    # tkinter window
    root = tk.Tk()
    root.title("Semantic Search Party") 



    play_game(data, bins, nlp, words_only)

       