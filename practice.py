# coding=utf-8
import sys
from random import shuffle
from random import randint, sample


class Question(object):
    def __init__(self, word, answers, correct_answer):
        self.word = word.strip().strip('\n')
        self.answers = map(lambda x: x.strip().strip('\n'), answers)
        self.correct_answer = correct_answer

    def _is_correct(self, answer):
        return self.correct_answer == answer

    def answer_question(self, index):
        print '%d. What is the meaning of word "%s"' % (index, self.word)
        for t in xrange(4):
            print '%d. %s' % (t + 1, self.answers[t])
        answer = raw_input("Choose your answer: ")
        try:
            int(answer)
        except ValueError:
            print 'You have input wrong answer'
            return False
        return self._is_correct(int(answer))


class QuestionSet(object):
    def __init__(self, feed_map=None):
        if not feed_map or not isinstance(feed_map, dict):
            return
        self._feed_map = feed_map
        self._question_set = self._create_question_set(feed_map)
        self._index = 0
        self._correct_questions = []

    def _create_question_from_word(self, word, answer, answers):
        correct_answer = randint(0, 3)
        answers = sample(list(set(answers) - {answer}), 3)
        answers.insert(correct_answer, answer)
        return Question(word=word, answers=answers, correct_answer=correct_answer + 1)

    def _create_question_set(self, feed_map):
        words = feed_map.keys()
        shuffle(words)
        answers_cn = map(lambda x: x['en'], feed_map.values())
        result = []
        for word in words:
            result.append(self._create_question_from_word(word, feed_map[word]['en'], answers_cn))
        return result

    def answer_next_question(self):
        if len(self._question_set) == 0:
            print 'Sorry, there is no question now.'
            return
        elif len(self._question_set) == self._index:
            print('You have answered all questions.')
            return
        question = self._question_set[self._index]
        correct = question.answer_question(self._index + 1)
        if not correct:
            print 'The correct answer is %d, "%s"' % (question.correct_answer,
                                                      question.answers[question.correct_answer - 1])
        else:
            print 'Your answer is correct.'
            self._correct_questions.append(self._index)
        self._index += 1

    def begin_answer(self):
        for _ in xrange(len(self._question_set)):
            self.answer_next_question()
        print '(%d/%d) questions you answered are correct, correct rate: %.2f%%' % \
              (len(self._correct_questions), len(self._question_set),
               float(len(self._correct_questions)) * 100 / len(self._question_set))
        print 'The following words need to be remembered:'
        incorrect_questions = set(range(len(self._question_set))) - set(self._correct_questions)
        for i in incorrect_questions:
            question = self._question_set[i]
            print 'The meaning of "%s" is "%s"' % (question.word, question.answers[question.correct_answer - 1])


def practice(path, practice_set=None):
    with open(path) as f:
        data = f.readlines()
    word_map = {}
    word_property_map = {}
    for l in data:
        if l.startswith('name:'):
            word_property_map = {}
            word_map[l[l.index(':') + 1:]] = word_property_map
        elif l.strip() and not l.startswith('---') and ':' in l:
            colon_index = l.index(':')
            word_property_map[l[:colon_index]] = l[colon_index + 1:]
    if practice_set:
        word_map = {k: v for k, v in word_map.items() if k.startswith(practice_set)}
    qs = QuestionSet(feed_map=word_map)
    qs.begin_answer()


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('请先指定toefl单词路径')
    practice(sys.argv[1], practice_set=(sys.argv[2] if len(sys.argv) > 2 else None))


if __name__ == '__main__':
    main()
