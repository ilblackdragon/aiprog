import codecs

FILE_ENCODING = 'cp1251'
CONSOLE_ENCODING = 'cp866'

class Condition(object):
    
    def __init__(self, name, flag=True):
        self.name = name
        self.flag = flag
        
    def __unicode__(self):
        if not self.flag:
            return '~' + self.name
        return self.name
        
    def __repr__(self):
        return self.__unicode__().encode(CONSOLE_ENCODING)
        
class Rule(object):
    
    def __init__(self, conditions, result):
        self.conditions = conditions
        self.result = result
        self.applied = False

    def list_of_needs(self, context, not_context):
        needs = []
        for cond in self.conditions:
            if cond not in context and cond not in not_context:
                needs.append(cond)
        return needs
        
    def test(self, context):
        if self.applied:
            return False
        for cond in self.conditions:
            if cond not in context:
                return False
        return True

    def apply(self, context):
        for cond in self.result:
            context.append(cond)
        self.applied = True

    def __unicode__(self):
        return u' & '.join([unicode(cond) for cond in self.conditions]) + u" => " + u' & '.join([unicode(cond) for cond in self.result])
        
    def __repr__(self):
        return self.__unicode__().encode(CONSOLE_ENCODING)
        
class ExpertSystem(object):
    
    def __init__(self, fname):
        self.context = []
        self.rules = []
        self.conditions = {}
        self.load_rules(fname)
            
    def get_or_create_condition(self, condition_name):
        if condition_name[0] == '~':
            condition_name, flag = condition_name[1:], False
        else:
            condition_name, flag = condition_name, True
        if condition_name in self.conditions:
            return self.conditions[condition_name][flag]
        self.conditions[condition_name] = {
            True: Condition(condition_name, True), 
            False: Condition(condition_name, False) 
        }
        return self.conditions[condition_name][flag]
        
    def load_rules(self, fname):
        lines = codecs.open(fname, "r", FILE_ENCODING).readlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            conditions, result = line.split('=>')
            condition_list = [self.get_or_create_condition(condition) for condition in conditions.split(',')]
            result_list = [self.get_or_create_condition(condition) for condition in result.split(',')]
            self.rules.append(Rule(condition_list, result_list))

    def apply_rules(self):
        changed = False
        for rule in self.rules:
            if rule.test(self.context):
                rule.apply(self.context)
                print("Rule %s applied" % unicode(rule))
                changed = True
        if changed:
            self.apply_rules()

    def get_not_cond(self, cond):
        return self.conditions[cond.name][not cond.flag]
            
    def find_question(self):
        need_counts = [0] * len(self.conditions.values())
        not_context = [self.get_not_cond(cond) for cond in self.context]
        for rule in self.rules:
            if not rule.applied:
                list_of_needs = rule.list_of_needs(self.context, not_context)
                for cond in list_of_needs:
                    for i, key in enumerate(self.conditions):
                        if cond == self.conditions[key][True] or cond == self.conditions[key][False]:
                            need_counts[i] += 1
                            break
        max_value = max(need_counts)
        if max_value == 0:
            return None
        return self.conditions.values()[need_counts.index(max(need_counts))][True]
           
    def run(self):
        for rule in self.rules:
            print(rule)

        while True:
            self.apply_rules()
            cond = self.find_question()
            if not cond:
                break
            print("Are %s true or false?" % unicode(cond))
            try:
                answer = raw_input(">")
            except KeyboardInterrupt:
                break
            if answer == "true" or answer == "t" or answer == "y":
                answer = True
            else:
                answer = False
            if answer:
                self.context.append(cond)
            else:
                self.context.append(self.conditions[cond.name][False])

        print(self.context)

if __name__ == "__main__":
    es = ExpertSystem('knowledge.dat')
    es.run()
