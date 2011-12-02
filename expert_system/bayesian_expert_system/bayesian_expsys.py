from math import log
import codecs
import os

# UTILITES

FILE_ENCODING = 'cp1251'
CONSOLE_ENCODING = 'cp866'

def exception(name):
    return type(name, (Exception, ), {})
    
IncorrectNumberOfTermsExcpetion = exception('IncorrectNumberOfTermsExcpetion')

def get_terms(line, types):
    line = line.split(',')
    if len(line) != len(types):
        raise IncorrectNumberOfTermsExcpetion()
    return [term_type(term) for term, term_type in zip(line, types)]

def create_object(line, types, object_class, *args, **kwargs):
    args = get_terms(line, types) + list(args)
    return object_class(*args, **kwargs)
    
def create_multi_dict(default_value, args):
    if not args:
        return default_value
    result = {}
    for iter in args:
        for item in iter:
            result[item] = create_multi_dict(default_value, args[1:])
    return result
    
class ObjectWithName(object):
        
    def __unicode__(self):
        return self.name
        
    def __repr__(self):
        return unicode(self).encode(CONSOLE_ENCODING)

def entropy(x):
    return -log(x)*x
        
# Expert system
        
class Resolution(ObjectWithName):
    
    def __init__(self, id, prob, name):
        self.id = id
        self.name = name
        self.prob = prob

class Answer(ObjectWithName):
    
    def __init__(self, id, prob, name):
        self.id = id
        self.name = name
        self.prob = prob

class Question(ObjectWithName):
    
    def __init__(self, id, name, answers):
        self.id = id
        self.answers = answers
        self.name = name

    def ask(self):
        print(self)
        for i, ans in enumerate(self.answers):
            print("%d) %s." % (i + 1, unicode(ans)))
        while True:
            try:
                num = raw_input("Enter number of answer (1-%d): " % len(self.answers))
            except KeyboardInterrupt:
                print("exit\n")
                break
            if (num == "e" or num== "exit"):
                break
            try:
                num = int(num)
            except:
                pass
            if num >= 1 and num <= len(self.answers):
                return self.answers[num - 1]
        return None
        
class ExpertSystem(object):
    
    def __init__(self):
        self.answers = {}
        self.questions = {}
        self.resolutions = {}
        self.probs = {}
        self.answer_count = {}
        self.total_guess_count = 0
        self.load()
        
    def load(self):
        lines = codecs.open("data/answers.dat", "r", FILE_ENCODING).readlines()
        answers = [create_object(line.strip(), (int, float, unicode), Answer) for line in lines]
        self.answers = dict([(obj.id, obj) for obj in answers])

        lines = codecs.open("data/questions.dat", "r", FILE_ENCODING).readlines()
        questions = [create_object(line.strip(), (int, unicode), Question, answers) for line in lines]
        self.questions = dict([(obj.id, obj) for obj in questions])

        lines = codecs.open("data/resolutions.dat", "r", FILE_ENCODING).readlines()
        self.total_guess_count = int(lines.pop(0))
        resolutions = [create_object(line.strip(), (int, float, unicode), Resolution) for line in lines]
        self.resolutions = dict([(obj.id, obj) for obj in resolutions])

        if os.path.exists("data/probs.dat") and os.path.exists("data/answer_count.dat"):
            probs_list = codecs.open("data/probs.dat", "r", FILE_ENCODING).readlines()
            for probs in probs_list:
                probs = probs.strip()
                if probs:
                    r_id, q_id, ans_id, prob = probs.split(',')
                    if int(r_id) not in self.probs:
                        self.probs[int(r_id)] = {}
                    if int(q_id) not in self.probs[int(r_id)]:
                        self.probs[int(r_id)][int(q_id)] = {}
                    self.probs[int(r_id)][int(q_id)][int(ans_id)] = float(prob)
            answer_count_list = codecs.open("data/answer_count.dat", "r", FILE_ENCODING).readlines()
            for answer_count in answer_count_list:
                answer_count = answer_count.strip()
                if answer_count:
                    r_id, q_id, count = answer_count.split(',')
                    if int(r_id) not in self.answer_count:
                        self.answer_count[int(r_id)] = {}
                    self.answer_count[int(r_id)][int(q_id)] = float(count)
        else:
            self.probs = {}
            self.answer_count = {}
            for r_id in self.resolutions:
                self.probs[r_id] = {}
                self.answer_count[r_id] = {}
                for q_id, question in self.questions.iteritems():
                    self.probs[r_id][q_id] = {}
                    self.answer_count[r_id][q_id] = len(question.answers)
                    for ans in question.answers:
                        self.probs[r_id][q_id][ans.id] = 1.0

    def save(self):
        f = codecs.open("data/resolutions.dat", "w+", FILE_ENCODING)
        f.write("%d\n" % (self.total_guess_count))
        for resolution in self.resolutions.values():
            f.write("%d,%f,%s\n" % (resolution.id, resolution.prob, resolution.name))
        f.close()
        f = codecs.open("data/probs.dat", "w+", FILE_ENCODING)
        for r_id in self.probs:
            for q_id in self.probs[r_id]:
                for ans_id in self.probs[r_id][q_id]:
                    f.write("%d,%d,%d,%f\n" % (r_id, q_id, ans_id, self.probs[r_id][q_id][ans_id]))
        f.close()
        f = codecs.open("data/answer_count.dat", "w+", FILE_ENCODING)
        for r_id in self.answer_count:
            for q_id in self.answer_count[r_id]:
                f.write("%d,%d,%f\n" % (r_id, q_id, self.answer_count[r_id][q_id]))
        f.close()
        
                
    def get_question(self):
        current_q = None
        current_entropy = 999999
        res_probs = self.get_resolution_probs()
        for q in self.questions:
            if q in self.asked:
                continue
            ce = 0
            for a in self.questions[q].answers:
                pa = 0
                for resolution, res_prob in zip(self.resolutions, res_probs):
                    pa += res_prob * (self.probs[resolution][q][a.id] / self.answer_count[resolution][q])
                self.asked[q] = a
                current_res_probs = self.get_resolution_probs()
                ce += pa * sum([entropy(c_prob) for c_prob in current_res_probs])
                self.asked.pop(q)
            if ce < current_entropy:
                current_entropy = ce
                current_q = self.questions[q]
        return current_q
                
    def get_resolution_probs(self):
        res = [0] * len(self.resolutions)
        for i, resolution in enumerate(self.resolutions.values()):
            p = 1
            for q_id in self.asked:
                p *= self.probs[resolution.id][q_id][self.asked[q_id].id] / self.answer_count[resolution.id][q_id]
            res[i] = p * resolution.prob / self.total_guess_count
        res = [x / sum(res) for x in res]
        return res
                
    def get_answer(self):
        res = self.get_resolution_probs()
        print(res)
        st = max(res)
        return (self.resolutions.values()[res.index(st)], st)
                
    def run(self):
        self.asked = {}
        while True:
            q = self.get_question()
            if not q:
                break
            ans = q.ask()
            if not ans:
                break
            self.asked[q.id] = ans
            answer, st = self.get_answer()
            if st > 0.8:
                break
        answer, st = self.get_answer()
        print("My best choice: %s" % answer )
        try:
            corr_ans = raw_input("Am I right? [Y/N] ")
        except KeyboardInterrupt:
            print("exit")
            return
        if corr_ans in ("N", "n", "no"):
            for r_id, resolution in self.resolutions.iteritems():
                if r_id != answer.id:
                    print("%d) %s." % (r_id, unicode(resolution)))
            corr_ans = raw_input("Correct answer?")
            corr_ans = int(corr_ans)
            for q_id in self.asked:
                self.probs[corr_ans][q_id][self.asked[q_id].id] += 1
                self.answer_count[corr_ans][q_id] += 1
        if corr_ans in ("Y", "y", "yes"):
            answer.prob += 1
            self.total_guess_count += 1
            for q_id in self.asked:
                self.probs[answer.id][q_id][self.asked[q_id].id] += 1
                self.answer_count[answer.id][q_id] += 1
                
def main():
    exp = ExpertSystem()
    exp.run()
    exp.save()

if __name__ == "__main__":
    main()
