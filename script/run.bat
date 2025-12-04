

az login --tenant 285f1bcc-8795-4823-b35e-c6f15d78e70b

http://localhost:5173/app?flags=tools,debug

fastapi run main.py

npm run dev
uvicorn main:app 


python object_detector.py ../../testdata/test4.jpg --method color --output dist.json

python lego-api/robot/object_detector.py testdata/test4.jpg --method color --output result.json