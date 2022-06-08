from audioop import add
from typing import Optional
from unicodedata import name
from pecan import response
import razorpay
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from datetime import datetime as dt


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

success_add_class = 'show-success-add'
failure_add_class = 'show-failure-add'

success_delete_class = 'show-success-delete'
failure_delete_class = 'show-failure-delete'

secretKeyMain = "secret"



def getPaymentInformation(paymentId):
    message = "failure, api key doesnot exist"
    amount = ""
    paymentId = paymentId.strip()
    success, message, date, email, contact, address, merchantOrderId, accountId, amount, tax = None, None, None, None, None, None, None, None, None, None
    try:
        keyFile = open("keyvalue.txt", 'r')
        keyText = keyFile.read()
        keyFile.close()

        keyText = keyText.split("\n")
        print(keyText)

        clientList = []

        for keys in keyText:
            if keys.strip() != "":
                try:
                    keyvalue =keys.split("#")
                    print(keys)
                    print(keyvalue[0], keyvalue[1])
                    clientList.append(razorpay.Client(auth=(keyvalue[0], keyvalue[1])))
                except Exception as e:
                    print(e)

        for client in clientList:
            try:
                message = "success"
                response = client.payment.fetch(paymentId)
                print(response)
                email = response["email"]
                date = dt.fromtimestamp(response["created_at"])
                contact = response["contact"]
                address = response["notes"]["address"]
                merchantOrderId = response["notes"]["merchant_order_id"]
                accountId = response["account_id"]
                amount = response["currency"]+" "+str(response["amount"]/100.0)
                tax = response["tax"]
                break
            except Exception as e:
                print(paymentId)
                print(e)
                message = "failure "+ str(e)
    except Exception as e:
        print(e)
    return  message, paymentId, date, email, contact, address, merchantOrderId, accountId, amount, tax




@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/form")
def form_post(request: Request):
    result = ""
    return templates.TemplateResponse('form.html', context={'request': request, 'result': result, 'amount':'', 'showResult':'hide'})



@app.post("/form")
def form_post(request: Request, paymentId: str = Form(...)):
    message, paymentId, date, email, contact, address, merchantOrderId, accountId, amount, tax = getPaymentInformation(paymentId)
    return templates.TemplateResponse('form.html', context={
            'request': request, 
            'id': paymentId,
            'date': str(date),
            'email': email,
            'contact': contact,
            'address': address,
            'merchantOrderId': merchantOrderId,
            'accountId': accountId,
            'amount':amount, 
            'tax': tax,
            'message':message, 
            'showResult':'show'
        })

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

@app.get("/addkey")
def form_post(request: Request):
    return templates.TemplateResponse('addKey.html', context={'request': request, 'responseClass':'hide', 'responseMessage':''})

def addKey(key, value):
    print(f"adding key and value {key} {value}")
    keyFile = open("keyvalue.txt", 'a+')
    keyFile.write(f"{key.strip()}#{value.strip()}\n")
    keyFile.close()
    return 'key and value added successfully', success_add_class

@app.post("/addkey")
def add_api(
        request: Request, 
        secretKey: str= Form(default=""), 
        key: str= Form(default=""),  
        value: Optional[str] = Form(default="")
    ):
    responseClass = failure_add_class
    message = "secret key donot match"
    
    if secretKey == "secret":
        message = "key and value successfully added"
        if key =="" or value == "":
            message = "please provide both key and value"
        else:
            message, responseClass = addKey(key, value)
    
    return templates.TemplateResponse('addKey.html', context={'request': request, 'responseClassAdd': responseClass, 'responseMessageAdd': message, 'responseClassDelete': 'hide', 'responseMessageDelete': '',})


def deleteKey(key):
    message = "given key doesnot exist"
    response = failure_delete_class
    file = open("keyvalue.txt", 'r')
    content = file.read()
    file.close()
    contentList = content.split("\n")
    newContent = []
    for contentItem in contentList:
        contentItem = contentItem.strip()
        if contentItem != "":
            contentItemSplitted = contentItem.split("#")
            print(contentItemSplitted)
            if contentItemSplitted[0] == key:
                message = f"key: {key} successfully deleted"
                response = success_delete_class
            else: 
                newContent.append(contentItem)
    
    print(newContent)
    newContent = "\n".join(newContent)
    file = open("keyvalue.txt", 'w')
    content = file.write(newContent)
    file.close()

    return message, response


@app.post("/deletekey")
def delete_api(
        request: Request, 
        secretKey: str= Form(default=""), 
        key: str= Form(default=""),  
        value: Optional[str] = Form(default="")
    ):
    message, responseClass = "", ""
    if secretKey != secretKeyMain:
        message, responseClass = "secrete key donot match", failure_delete_class
    else:
        message, responseClass = deleteKey(key=key)
    
    return templates.TemplateResponse('addKey.html', context={'request': request, 'responseClassDelete': responseClass, 'responseMessageDelete': message, 'responseClassAdd': 'hide', 'responseMessageAdd':''})
