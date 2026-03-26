from __future__ import annotations
import time
import random
from abc import ABC, abstractmethod
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

class State(ABC):
    def __init__(self, student: Student):
        self.student = student

    @abstractmethod
    def click_lock(self): 
        pass

    @abstractmethod
    def click_play(self): 
        pass

    @abstractmethod
    def click_next(self, dbl: bool): 
        pass

    @abstractmethod
    def click_prev(self, dbl: bool): 
        pass

class SleepingState(State):
    def click_lock(self):
        if self.student.is_active:
            self.student.change_state(GamingState(self.student))
        else:
            self.student.change_state(StudyingState(self.student))
        return "Студент проснулся"

    def click_play(self): 
        return "Студент спит и не слышит"
    
    def click_next(self, d): 
        return "Ззз..."
    
    def click_prev(self, d): 
        return "Ззз..."

class StudyingState(State):
    def click_lock(self):
        self.student.change_state(SleepingState(self.student))
        return "Студент уснул"

    def click_play(self):
        self.student.is_active = True
        self.student.change_state(GamingState(self.student))
        return "Бросил учебу, сел за комп"

    def click_next(self, dbl: bool):
        if self.student.is_day():
            gain = random.randint(8, 15) if dbl else random.randint(1, 5)
            self.student.iq += gain
            return f"Удачно почитал! +{gain} IQ"
        else:
            gain = random.choice([0, 1])
            self.student.iq += gain
            return f"Ночью плохо учится... +{gain} IQ"

    def click_prev(self, dbl: bool):
        loss = random.randint(1, 3)
        self.student.iq -= loss
        return f"Запутался в старом материале... -{loss} IQ"

class GamingState(State):
    def click_lock(self):
        self.student.change_state(SleepingState(self.student))
        return "Студент уснул прямо в наушниках"

    def click_play(self):
        self.student.is_active = False
        self.student.change_state(StudyingState(self.student))
        return "Выключил Доту, взял учебник"

    def click_next(self, dbl: bool):
        if not self.student.is_day():
            gain = random.randint(40, 70) if dbl else random.randint(20, 30)
            self.student.mmr += gain
            return f"Потная победа! MMR +{gain}"
        
        else:
            loss = random.randint(10, 40)
            self.student.mmr -= loss
            return f"Дневные руинеры в тиме... MMR -{loss}"

    def click_prev(self, dbl: bool):
        luck = random.randint(-10, 10)
        self.student.mmr += luck
        return f"Посмотрел реплей. Изменение: {luck} MMR"

class Student:
    def __init__(self):
        self.iq = 100
        self.mmr = 1000
        self.is_active = False
        self.start_time = time.time()
        self.state = StudyingState(self)

    def change_state(self, state: State):
        self.state = state

    def is_day(self):
        hour = (int((time.time() - self.start_time) * 2) % 24)
        return 6 <= hour < 22

    def click_lock(self): 
        return self.state.click_lock()
    
    def click_play(self): 
        return self.state.click_play()
    
    def click_next(self, d=False): 
        return self.state.click_next(d)
    
    def click_prev(self, d=False): 
        return self.state.click_prev(d)

student_context = Student()

@app.get("/status")
def get_status():
    elapsed = time.time() - student_context.start_time
    hour = int(elapsed * 2) % 24
    return {
        "hour": f"{hour:02d}:00",
        "is_day": student_context.is_day(),
        "state": student_context.state.__class__.__name__,
        "iq": student_context.iq,
        "mmr": student_context.mmr
    }

@app.post("/action/{method}")
def action(method: str, dbl: bool = False):
    act_map = {
        "lock": student_context.click_lock,
        "play": student_context.click_play,
        "next": lambda: student_context.click_next(dbl),
        "prev": lambda: student_context.click_prev(dbl)
    }
    return {"message": act_map[method]()}

@app.get("/")
def index():
    try:
        content = open("lab03/back/index.html", encoding="utf-8").read()
    except FileNotFoundError:
        content = "<h1>index.html not found! Check the path.</h1>"
    return HTMLResponse(content=content)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
