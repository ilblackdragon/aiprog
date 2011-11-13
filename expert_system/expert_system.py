
class QuestionBase(object):
    
    def __init__(self, name):   
        self.name = name
        
    def ask(self):
        return None

class ExpertSystem(object):
    
    def __init__(self):
        pass
        
    def get_question(self):
        pass
        
    def get_answer(self):
        pass
        
    def run(self):
        pass
        while True:
            question = self.get_question()
            if not question:
                break
            answer = question.ask()
            if not answer:
                break
            context.add(answer)
        

if __name__ == "__main__":
    pass
