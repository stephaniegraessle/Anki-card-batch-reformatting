import csv
import re

# Export shared deck from Anki app as .txt file
INPUT_CSV = 'All in One Kanji.csv'
MAX_ROWS_PER_FILE = 2500
# (Optional) When importing to Anki, add '漢字' as a tag for all cards

with open(INPUT_CSV, 'r', newline='') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=';')

    words = [] # contains list of words associated with each kanji
    level_info = [] # contains JLPT level information

    # Skip the header row
    next(csv_reader)

    for row in csv_reader:
        if '#' not in row[0]:  # skip heading rows which contain '#'
            words.append(row[5])
            level_info.append(row[20])

# Lists to store the extracted parts and levels
head_words = []
readings = []
definitions = []
levels = []

# Regular expression to match the parts
pattern = re.compile(r'(\S+)\(([^)]+)\): (.+?)(?=<br>|$)')
list_split_pattern = re.compile(r'(\(\d+\))')

for k in range(len(words)):
    # get level information
    info = level_info[k]

    if 'N5' in info:
        level = 'N5'
    elif 'N4' in info:
        level = 'N4'
    elif 'N3' in info:
        level = 'N3'
    elif 'N2' in info:
        level = 'N2'
    elif 'N1' in info:
        level = 'N1'
    else:
        level = 'N0'

    # get word information
    matches = pattern.findall(words[k])
    for match in matches:
        head_word = match[0].replace('<br>', '')  # Remove any <br> tags from head words
        head_words.append(head_word)

        readings.append(match[1])

        definition = list_split_pattern.sub(r'<br>\1', match[2]).lstrip('<br>')
        definitions.append(definition)

        levels.append(level)

# Print the results
print("Head Word:", head_words[2])
print("Reading:", readings[2])
print("Definition:", definitions[2])
print("Level:", levels[2])

fronts = head_words # head Japanese entry

# Combine reading and definition into the backs of the cards
backs = [] # reading + <br><br> + definition

for i in range(len(fronts)):
    back_contents = readings[i]
    back_contents += "<br><br>"
    back_contents += definitions[i]
    backs.append(back_contents)

# combine the levels of duplicate fronts/head words
combined_entries = {}
for i in range(len(fronts)):
    if fronts[i] in combined_entries:
        combined_entries[fronts[i]]['levels'].add(levels[i])
    else:
        combined_entries[fronts[i]] = {'levels': set([levels[i]]), 'back': backs[i]}

# Dictionary to store file writers for each JLPT level
jlpt_files = {}
jlpt_writers = {}

# Open files for each JLPT level
for level in ['N5', 'N4', 'N3', 'N2', 'N1', 'N0']:
    jlpt_files[level] = open(f'output_{level}.csv', 'w', newline='')
    jlpt_writers[level] = csv.writer(jlpt_files[level])

# Write headers to each file
#for writer in jlpt_writers.values():
#    writer.writerow(['Front', 'Back', 'Tags'])

print("Writing processed information to output CSV files...")
if len(levels) == len(fronts) == len(backs):
    for key in combined_entries:
        levels = combined_entries[key]['levels']
        back_contents = combined_entries[key]['back']
        levels_combined = ' '.join(levels)

        for level in levels:
            if level in jlpt_writers:
                jlpt_writers[level].writerow([key, back_contents, levels_combined])

    # Close all JLPT level files
    for file in jlpt_files.values():
        file.close()
else:
    print("Lists are not of the same length.")

print("Completed.")