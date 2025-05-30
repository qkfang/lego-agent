curl -X POST http://localhost:8000/exec -H "Content-Type: application/json" -d 'import runloop, sys
from hub import light_matrix

async def main():
    await light_matrix.write("Yup!")
    print("done")
    sys.exit(0)

    
runloop.run(main())'
