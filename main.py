from typing import Optional
import razorpay
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request


app = FastAPI()
handler = Mangum(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def getPaymentInformation(paymentId):
    success = "failure"
    message = "api key doesnot exist"
    amount = ""
    paymentId = paymentId.strip()
    try:
        keyFile = open("keyvalue.txt", 'r')
        keyText = keyFile.read()
        keyFile.close()

        keyText = keyText.split("\n")

        clientList = []

        print("getting len")
        for keys in keyText:
            print(keys)
            if keys.strip() != "":
                try:
                    keyvalue =keys.split("#")
                    print(keys)
                    print(keyvalue[0], keyvalue[1])
                    clientList.append(razorpay.Client(auth=(keyvalue[0], keyvalue[1])))
                except Exception as e:
                    print(e)

        print(len(clientList))

        for client in clientList:
            try:
                print(paymentId)
                response = client.payment.fetch(paymentId)
                print(response)
                success = "success"
                message = str(response)
                amount = "INR "+str(response["amount"]/100.0)
                break
            except Exception as e:
                print(e)
                success = "failure"
                message = e
    except Exception as e:
        print(e)
    return success, message, amount




@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/form")
def form_post(request: Request):
    result = ""
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result, 'amount':'', 'showResult':'hide'})



@app.post("/form")
def form_post(request: Request, paymentId: str = Form(...)):
    result, message, amount = getPaymentInformation(paymentId=paymentId)
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result, 'amount':amount, 'message':message, 'showResult':'show'})

@app.get("/setapi")
def form_post(request: Request):
    result = ""
    return templates.TemplateResponse('setKey.html', context={'request': request})

@app.post("/setapi")
def set_api(
        request: Request, 
        secretKey: str= Form(default=""), 
        key1: str= Form(default=""),  
        value1: Optional[str] = Form(default=""),
        key2: str= Form(default=""),  
        value2: Optional[str] = Form(default=""),
        key3: str= Form(default=""),  
        value3: Optional[str] = Form(default="")
    ):
    message = "secret key donot match"
    keyFile = open("keyvalue.txt", 'w')
    if secretKey == "secret":
        message = "keys and value successfully added"
        if key1 !="" and value1 != "": keyFile.write(f"{key1}#{value1}\n")
        if key2 !="" and value2 != "":keyFile.write(f"{key2}#{value2}\n")
        if key2 !="" and value2 != "":keyFile.write(f"{key3}#{value3}\n")
    keyFile.close()
    
    return templates.TemplateResponse('success.html', context={'request': request, 'message': message})
