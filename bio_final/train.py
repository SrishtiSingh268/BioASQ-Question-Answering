import cPickle as pickle
import numpy as np
from sklearn import svm
import os.path

def save_object(filename, obj):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_object(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)

def filter_for_space(questions):

    filtered_questions = []
    for i, question in enumerate(questions):
        answers = question['answers']
        candidates = [a['candidate'] for a in question['candidates']]
        is_present = False
        
        for candidate in candidates:
            for answer in answers:
                if answer.lower() == candidate.lower():
                    is_present = True

        if is_present:
            filtered_questions.append(question)

    return filtered_questions

def get_soft_score(questions, max_perc_total):

    percentual = []
    for i, question in enumerate(questions):
        answers = question['answers']
        candidates = [a['candidate'] for a in question['candidates']]
        is_present = False
        
        for candidate in candidates:
            for answer in answers:
                if answer.lower() == candidate.lower():
                    is_present = True

        if is_present:
            percentual.append(1)
        else:
            percentual.append(0)

    percent = np.array(percentual).mean()

    return 'Percentual (local): ' + str(percent*100), ' Percentual (global): ' + str(percent*max_perc_total)

def normalize(a):
    col_min = np.amin(a,axis=0)
    col_ptp = a.ptp(0)

    return ((2*(a-col_min))/col_ptp) - 1

def train(train_questions, test_questions):

    sorted_questions = []
    X = []
    y = []

    for i, question in enumerate(train_questions):
        for candidate in question['candidates']:
            score = candidate['score']
            features = candidate['features']
            X.append(np.array(features))
            y.append(score)

    X = normalize(np.array(X))
    y = normalize(np.array(y))

    print X

    """
    clf_name = 'pkl/clf_svr_norm_all_clean_100'
    if os.path.exists(clf_name):
        clf = load_object(clf_name)
        print 'load clf...'
    else:
        print 'start clf...'
        clf = svm.SVR()
        clf.fit(X, y)
        save_object(clf_name, clf)
    """

    clf_name = 'pkl/new_clf'
    print 'start clf...'
    clf = svm.SVR()
    clf.fit(X, y)
    save_object(clf_name, clf)

    for i, question in enumerate(test_questions):
        candidates_arr = []
        sorted_question = {}
        for candidate in question['candidates']:
            features = np.array([np.array(candidate['features'])])
            score = clf.predict(features)[0]
            candidates_arr.append((score, candidate['candidate'], features))

        candidates_arr.sort(key=lambda x: x[0], reverse=True)
        candidates_arr = candidates_arr[:5]
        #print question['query']
        #print '\n'
        #print question['answers']
        #print '\n'
        #for s,c,f in candidates_arr:
        #    print c
        #print '\n\n\n\n'
        sorted_question['candidates'] = [{'candidate': c} for s,c,f in candidates_arr]
        sorted_question['answers'] = question['answers']
        sorted_questions.append(sorted_question)

    return sorted_questions






def main():

    initial_questions = load_object('pkl/questions.pkl')
    questions = filter_for_space(initial_questions)
    max_perc_total = (len(questions)/float(len(initial_questions)))*100
    train_questions = questions[:174]
    test_questions = questions[174:]


    print get_soft_score(test_questions, max_perc_total)
    sorted_test_questions = train(train_questions, test_questions)
    print get_soft_score(sorted_test_questions, max_perc_total)



    #train_questions = questions[:388]

    """
    for i, question in enumerate(questions):
    	print question['query'], '\n'
    	print question['answers'], '\n'
    	print question['candidates'][:3], '\n'

    	_temp = []
    	for candidate in question['candidates']:
    		if candidate['score']>0.5:
    			_temp.append(candidate)

    	print _temp[:3]

    	print '\n\n'
    """


if __name__ == '__main__':
    main()