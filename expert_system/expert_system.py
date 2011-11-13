
class BasicContext(object):
    
    def __init__(self):
        self.data = {}
        
    def add(self, question, answer):
        self.data[question] = answer
        
    def remove(self, question):
        self.data.pop(question)
        
class QuestionBase(object):
    
    def __init__(self, name):   
        self.name = name
        
    def ask(self, context):
        return None

class ExpertSystem(object):
    
    def __init__(self, context):
        self.context = context

    def get_question(self):
        return None

    def get_resolution(self):
        return None
        
    def show_resolution(self, resolution):
        pass
        
    def run(self):
        while True:
            question = self.get_question()
            if not question:
                break
            answer = question.ask(self.context)
            if not answer:
                break
            self.context.add(question, answer)
        resolution = self.get_resolution()
        if resolution:
            self.show_resolution(resolution)

if __name__ == "__main__":
    pass
