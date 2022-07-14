import uvicorn

if __name__ == '__main__':
    uvicorn.run("run:app", host="0.0.0.0", port=5001, reload=False, workers=1)
