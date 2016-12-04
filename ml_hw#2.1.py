import csv
import string
import re


g_SPAM_WORD = "spam"
g_HAM_WORD  = "ham"
g_SMS_SPAM_FILE_ADDRESS = 'main_sms_spam.csv'
g_STOP_WORDS_FILE_ADDRESS = 'stopwords.csv'
g_CACHE_F_V = []
g_CACHE_F_V_COUNT = []


def probability(feature, feature_value, instances, instances_types):
    # number of instance that its type value is 'ham'
    ham_count = 0.0
    # number of instance that its type value is 'ham' AND its feature value is equal to feature_value
    ham_feature_matched_count = 0.0

    # number of instance that its type value is 'spam'
    spam_count = 0.0
    # number of instance that its type value is 'spam' AND its feature value is equal to feature_value
    spam_feature_matched_count = 0.0

    i = 0
    while i < len(instances_types):
        instance = instances[i]
        if instances_types[i] == g_HAM_WORD:
            ham_count += 1
            if instance.count(feature) == feature_value:
                ham_feature_matched_count += 1
        elif instances_types[i] == g_SPAM_WORD:
            spam_count += 1
            if instance.count(feature) == feature_value:
                spam_feature_matched_count += 1
        i += 1

    # Don`t return 0
    if ham_feature_matched_count == 0:
        ham_feature_matched_count += 0.001
        ham_count += len(instances_types) * 0.001
    if spam_feature_matched_count == 0:
        spam_feature_matched_count += 0.001
        spam_count += len(instances_types) * 0.001

    return (ham_feature_matched_count / ham_count), (spam_feature_matched_count / spam_count)


def predict(feature_list, instance_feature_values_list, instances, instances_types):
    # P(spam | feature)
    p_spam = 1
    # P(ham  | feature)
    p_ham = 1
    indexes_count = len(feature_list)
    for f_index in range(indexes_count):
        feature = feature_list[f_index]
        feature_value = instance_feature_values_list[f_index]
        # number of instance that its type value is 'ham'
        ham_count = 0.0
        # number of instance that its type value is 'ham' AND its feature value is equal to feature_value
        ham_feature_matched_count = 0.0

        # number of instance that its type value is 'spam'
        spam_count = 0.0
        # number of instance that its type value is 'spam' AND its feature value is equal to feature_value
        spam_feature_matched_count = 0.0

        if g_CACHE_F_V.count((f_index, feature_value)) == 0:
            i = 0
            while i < len(instances_types):
                instance = instances[i]
                if instances_types[i] == g_HAM_WORD:
                    ham_count += 1
                    if instance.count(feature) == feature_value:
                        ham_feature_matched_count += 1
                elif instances_types[i] == g_SPAM_WORD:
                    spam_count += 1
                    if instance.count(feature) == feature_value:
                        spam_feature_matched_count += 1
                i += 1
            g_CACHE_F_V_COUNT.append((ham_feature_matched_count, ham_count, spam_feature_matched_count, spam_count))
        else:
            t_index = g_CACHE_F_V_COUNT.index((f_index, feature_value))
            t = g_CACHE_F_V_COUNT[t_index]
            ham_feature_matched_count = t[0]
            ham_count = t[1]
            spam_feature_matched_count = t[2]
            spam_count = t[3]

        # Don`t return 0
        if ham_feature_matched_count == 0:
            ham_feature_matched_count += 0.001
            ham_count += len(instances_types) * 0.001
        if spam_feature_matched_count == 0:
            spam_feature_matched_count += 0.001
            spam_count += len(instances_types) * 0.001

        p_ham *= ham_feature_matched_count / ham_count
        p_spam *= spam_feature_matched_count / spam_count

    if (p_ham / p_spam) >= 1.0:
        return g_HAM_WORD
    else:
        return g_SPAM_WORD


def main():
    print "<main> started..."

    # <editor-fold desc="Definition of Data"
    print "Definition of Data"
    stop_words = []
    sms_spam_types = []
    sms_spam_texts = []
    words_index = []
    words_count = []

    # Train data:
    train_sms_texts = []
    train_sms_types = []
    # Test data:
    test_sms_texts = []
    test_sms_types = []
    # </editor-fold>

    # <editor-fold desc="Reading stop words">
    print "Reading stop words"
    with open(g_STOP_WORDS_FILE_ADDRESS, 'rb') as stopWordsFile:
        spreader = csv.reader(stopWordsFile, delimiter=',', quotechar='|')
        for row in spreader:
            for cell in row:
                word = cell.replace(' ', '')  # remove blank character from the cell
                stop_words.append(word)

    # <editor-fold desc="Destructing variables of this fold">
    del row
    del cell
    del spreader
    del stopWordsFile
    # </editor-fold>
    # </editor-fold>

    # <editor-fold desc="Reading sms texts and types">
    print "Reading sms texts and types"
    with open(g_SMS_SPAM_FILE_ADDRESS, 'rb') as smsSpamFile:
        spreader = csv.reader(smsSpamFile, delimiter='\n', quotechar='|')

        for row in spreader:
            cells = row[0].split("\",\"")
            text_type = cells[0][1:]            # extract content of type
            text = cells[1][:len(cells[1])-1]   # extract content of text

            # Add to types index set
            if (text_type != g_HAM_WORD) and (text_type != g_SPAM_WORD):
                print "WARNING >> Invalid type (" + text_type + ")"
                continue

            sms_spam_types.append(text_type)

            # Removing numbers from text
            text = re.sub(r'\d+', '', text)

            # Removing punctuations from text
            text = text.replace('\'', '')
            exclude = set(string.punctuation)
            for ch in text:
                if ch in exclude:
                    text = text.replace(ch, ' ')

            # Removing single character words
            text_words = [w.replace(' ', '').lower() for w in text.split(' ') if len(w) > 1]

            # Removing stop words AND Appending the sentence
            sms_spam_texts.append(' '.join(w for w in text_words if stop_words.count(w) == 0))

    # <editor-fold desc="Destructing variables of this fold">
    del w
    del ch
    del row
    del text
    del cells
    del exclude
    del spreader
    del text_type
    del text_words
    del smsSpamFile
    # </editor-fold>
    # </editor-fold>

    # <editor-fold desc="Filling words index list and word count list">
    print "Filling words index list and word count list"
    for s in sms_spam_texts:
        for w in s.split(' '):
            if len(w) > 1:
                if w in words_index:
                    w_index = words_index.index(w)
                    words_count[w_index] += 1
                else:
                    words_index.append(w)
                    words_count.append(1)
    # </editor-fold>

    # <editor-fold desc="Splitting test data from train data">
    print "Splitting test data from train data"
    ham_indices = [i for i, x in enumerate(sms_spam_types) if x == "ham"]
    spam_indices = [i for i, x in enumerate(sms_spam_types) if x == "spam"]
    train_ham_texts_count = len(ham_indices) * 0.8
    train_spam_texts_count = len(spam_indices) * 0.8
    hams_count = 0
    for ham_index in ham_indices:
        if hams_count < train_ham_texts_count:
            train_sms_texts.append(sms_spam_texts[ham_index])
            train_sms_types.append(sms_spam_types[ham_index])
            hams_count += 1
        else:
            test_sms_texts.append(sms_spam_texts[ham_index])
            test_sms_types.append(sms_spam_types[ham_index])
    spams_count = 0
    for spam_index in spam_indices:
        if spams_count < train_spam_texts_count:
            train_sms_texts.append(sms_spam_texts[spam_index])
            train_sms_types.append(sms_spam_types[spam_index])
            spams_count += 1
        else:
            test_sms_texts.append(sms_spam_texts[spam_index])
            test_sms_types.append(sms_spam_types[spam_index])

    del i
    del x
    del train_ham_texts_count
    del train_spam_texts_count
    del hams_count
    del spams_count
    del ham_index
    del spam_index
    del ham_indices
    del spam_indices
    # </editor-fold>

    # <editor-fold desc="Predicating">
    print "> Predicating...\n"
    output_types = []
    test_texts = test_sms_texts
    test_types = test_sms_types
    text_index = 0

    while text_index < len(test_texts):
        instance = test_texts[text_index]
        f_values_list = [instance.count(f) for f in words_index]
        output_types.append(predict(words_index, f_values_list, train_sms_texts, train_sms_types) +
                            " (" + test_types[text_index] + ")")

        print output_types[-1]
        text_index += 1

    # </editor-fold>

    with open('output.csv', 'wb') as outputFile:
        outputFile.write('\n'.join(t for t in output_types))

    print "<main> ...finished"


print "started..."
print
main()
print
print "...finished"

