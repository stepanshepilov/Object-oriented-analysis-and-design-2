from __future__ import annotations
import time
import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

class Student:
    def __init__(self):
        self.iq = 100
        self.mmr = 1000
        
        self.is_sleeping = False
        self.is_gaming = False
        self.start_time = time.time()

    def is_day(self):
        hour = (int((time.time() - self.start_time) * 2) % 24)
        return 6 <= hour < 22

    def click_lock(self):
        if self.is_sleeping:
            self.is_sleeping = False
            return "Студент проснулся"
        else:
            self.is_sleeping = True
            return "Студент уснул"

    def click_play(self):
        if self.is_sleeping:
            return "Студент спит и не слышит"
        
        if self.is_gaming:
            self.is_gaming = False
            return "Выключил Доту, взял учебник"
        else:
            self.is_gaming = True
            return "Бросил учебу, сел за комп"

    def click_next(self, dbl: bool):
        if self.is_sleeping:
            return "Ззз..."
        
        if self.is_gaming:
            if not self.is_day():
                gain = random.randint(40, 70) if dbl else random.randint(20, 30)
                self.mmr += gain
                return f"Потная победа! MMR +{gain}"
            else:
                loss = random.randint(10, 40)
                self.mmr -= loss
                return f"Дневные руинеры в тиме... MMR -{loss}"
        else:
            if self.is_day():
                gain = random.randint(8, 15) if dbl else random.randint(1, 5)
                self.iq += gain
                return f"Удачно почитал! +{gain} IQ"
            else:
                gain = random.choice([0, 1])
                self.iq += gain
                return f"Ночью плохо учится... +{gain} IQ"

    def click_prev(self, dbl: bool):
        if self.is_sleeping:
            return "Ззз..."
            
        if self.is_gaming:
            luck = random.randint(-10, 10)
            self.mmr += luck
            return f"Посмотрел реплей. Изменение: {luck} MMR"
        else:
            loss = random.randint(1, 3)
            self.iq -= loss
            return f"Запутался в старом материале... -{loss} IQ"

student_context = Student()

@app.get("/status")
def get_status():
    elapsed = time.time() - student_context.start_time
    hour = int(elapsed * 2) % 24
    
    current_state_name = "SleepingState" if student_context.is_sleeping else \
                         ("GamingState" if student_context.is_gaming else "StudyingState")
    
    return {
        "hour": f"{hour:02d}:00",
        "is_day": student_context.is_day(),
        "state": current_state_name,
        "iq": student_context.iq,
        "mmr": student_context.mmr
    }

@app.post("/action/{method}")
def action(method: str, dbl: bool = False):
    if method == "lock":
        msg = student_context.click_lock()
    elif method == "play":
        msg = student_context.click_play()
    elif method == "next":
        msg = student_context.click_next(dbl)
    elif method == "prev":
        msg = student_context.click_prev(dbl)
    else:
        msg = "Unknown action"
    return {"message": msg}

@app.get("/")
def index():
    try:
        content = open("lab03/back/index.html", encoding="utf-8").read()
    except FileNotFoundError:
        content = "<h1>index.html not found!</h1>"
    return HTMLResponse(content=content)

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
    