python app.py --program '
import runloop, sys
from hub import light_matrix
print("Console message from hub.")
async def main():
    await light_matrix.write("Yup!")
    print("done")
    sys.exit(0)

runloop.run(main())
'
