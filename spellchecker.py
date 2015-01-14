import sys
import os
import shutil
import csv
import math


def readDirFilesToDict(dictDir):
    # parse the spam or ham folders' files into words corpus

    def hasIllegalChars(str):  # decide if a string is a legit word
        if str == '' or str[0] == '-' or str[-1] == '-' or str[0] > 'z' or str[0] < 'A':
            return True
        for c in str:
            if not (c >= 'a' and c <= 'z' or c >= 'A' and c <= 'Z' or c ==
                    '-'):
                return True
        if len(str) >= 50:
            return True
        return False

    def removePunctuation(s): # there might be some punctuation at the end
        s = s.replace('.', '')
        s = s.replace(',', '')
        s = s.replace(';', '')
        s = s.replace('?', '')
        s = s.replace('!', '')
        return s

    if dictDir[-1] != '/':  # deal with folder path
        dictDir = ''.join(dictDir + '/')
    filenameList = os.listdir(dictDir)  # find all files in the folder
    dic = {}    # dict of { filename: {word: 1} }
    illegalChars = '?!.,:;_<>()[]{}+*/=#$%^&` \" \' \\ \n \t'  # obselete

    for filename in filenameList:
        if filename != '.DS_Store':  # Mac OS X auto created file
            wordList = {}
            csvfile = open(dictDir + filename, 'rb')
            dat = csv.reader(csvfile, delimiter=' ')
            for lineCtnt in dat:
                for word in lineCtnt:
                    wordTmp = removePunctuation(word)
                    if not hasIllegalChars(wordTmp):  # deal with illegal char
                        wordList[wordTmp.lower()] = 1
            csvfile.close()
            dic[filename] = wordList

    # sys.stdout = open('ham_dict.txt', 'wb')
    # print dic
    return dic


def makedictionary(spam_directory, ham_directory, dictionary_filename):
    # read spam and ham files from folders for training
    spamMailDict = readDirFilesToDict(spam_directory)
    hamMailDict = readDirFilesToDict(ham_directory)
    spamMailNum = len(spamMailDict)
    hamMailNum = len(hamMailDict)

    # ham and spam {word: 1}, combining into total[word]
    hamWordDict, spamWordDict, totalWordList = {}, {}, []
    for doc in hamMailDict.values():
        for word in doc:
            hamWordDict[word] = 1
    for doc in spamMailDict.values():
        for word in doc:
            spamWordDict[word] = 1
    for word in hamWordDict.keys():
        if spamWordDict.has_key(word):
            totalWordList.append(word)
    totalWordList.sort()

    dictionary = []  # output to file, so it's alphabet ordered list
    i = 0   # indicating progress
    for word in totalWordList:
        if i % 500 == 0:    # show the progress
            print 'calculating', i, 'of', len(totalWordList), 'words'
        i += 1

        spamCount, hamCount = 0, 0
        for doc in spamMailDict.values():
            if doc.has_key(word):
                spamCount += 1
        for doc in hamMailDict.values():
            if doc.has_key(word):
                hamCount += 1
        spamRatio = 1.0 * spamCount / spamMailNum
        hamRatio = 1.0 * hamCount / hamMailNum
        dictionary.append([word, spamRatio, hamRatio])

    dicfile = open(dictionary_filename, 'wb')  # output to file
    for item in dictionary:
        dicfile.writelines(
            item[0] + ' ' + str(item[1]) + ' ' + str(item[2]) + '\n')


def spamsort(mail_directory, spam_directory, ham_directory, dictionary_filename, spam_prior_probability):
    # deal with folder path, create spam and ham folder if necessary
    if mail_directory[-1] != '/':
        mail_directory = ''.join(mail_directory + '/')
    if not os.path.isdir(spam_directory):
        os.makedirs(spam_directory)
    if not os.path.isdir(ham_directory):
        os.makedirs(ham_directory)

    # read in the dictionary file
    csvfile = open(dictionary_filename, 'rb')
    dat = csv.reader(csvfile, delimiter=' ')
    dictionary = []
    for lineCtnt in dat:
        dictionary.append(lineCtnt)
    csvfile.close()
    dictionaryDict = {}
    for item in dictionary:
        dictionaryDict[item[0]] = [
            math.log(float(item[1])), math.log(float(item[2]))]

    mailDict = readDirFilesToDict(mail_directory)  # read in emails
    for k, v in mailDict.items():  # k=filename, v={word:1} dict
        probSpam = math.log(spam_prior_probability)
        probHam = math.log(1 - spam_prior_probability)
        for word in v.keys():   # add up the probabilities
            if dictionaryDict.has_key(word):
                probSpam += dictionaryDict[word][0]
                probHam += dictionaryDict[word][1]
        mailPath = mail_directory + k
        if probSpam > probHam:   # move emails
            # shutil.copy2(mailPath, spam_directory)
            shutil.move(mailPath, spam_directory)
        else:
            # shutil.copy2(mailPath, ham_directory)
            shutil.move(mailPath, ham_directory)


if __name__ == "__main__":
    makedictionary('./spam', './easy_ham', './dictionary.txt')
    # spamsort('./mail', './out_spam', './out_ham', './dictionary.txt', 0.16415)
