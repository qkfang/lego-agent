import motor
import motor_pair
import time
import math
import runloop
import color_sensor
import sys
import time
from hub import port, motion_sensor
from hub import light_matrix


################### modify code below
async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    motion_sensor.set_yaw_face(motion_sensor.BACK)

    ###placeholder###

    sys.exit(0)

################### modify code abve




################### custom library
### obj
class Speed(int):
    Slow = 1
    Normal = 2
    Fast = 3


class LogLevel(int):
    Detailed = 1
    Normal = 2


### functions
# yaw
def getYaw():
    # log(motion_sensor.tilt_angles())
    return (
        round(motion_sensor.tilt_angles()[0] / 10, 3) * -1
    )# left is positive, right is negative


async def yaw(targetYaw, speed = Speed.Slow):
    log("[yaw] targetYaw=",targetYaw)

    yawStart = getYaw()
    yawDiff = round(targetYaw - yawStart, 3)
    if(yawDiff > 180):
        yawDiff = - (360 - yawDiff)
        log("[yaw] change to shortest direction: ", yawDiff)
    elif (yawDiff < -180):
        yawDiff = - (-360 - yawDiff)
        log("[yaw] change to shortest direction: ", yawDiff)

    await turn(yawDiff, speed)

    yawEnd = getYaw()
    log(
        "[yaw##] targetYaw=",targetYaw," yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff
    )


async def yawMove(targetYaw, targetDistance, speed = Speed.Slow):
    log("[yawMove] targetYaw=",targetYaw," targetDistance=",targetDistance)

    yawStart = getYaw()
    await yaw(targetYaw, speed)
    await move(targetDistance, speed)

    yawEnd = getYaw()
    yawDiff = round(targetYaw - yawStart, 3)

    log(
        "[yawMove##] targetYaw=",targetYaw," targetDistance=",targetDistance," yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff
    )


# move
async def move(targetDistance, speed=Speed.Slow):
    log("[move] targetDistance=",targetDistance)
    try:
        if targetDistance > 0:
            # _moveForward
            # light_matrix.show_image(light_matrix.IMAGE_ARROW_N)
            await _moveInternal("_fw_", targetDistance,
                                lambda diff, slowOffset : diff < -slowOffset,
                                lambda diff, stopOffset : diff < -stopOffset,
                                lambda diff, adjustOffset : diff > adjustOffset,
                                lambda diff, adjustOffset : diff < -adjustOffset,
                                lambda yawSum : yawSum > 0,
                                speed)
        elif targetDistance < 0:
            # _moveBackward
            # light_matrix.show_image(light_matrix.IMAGE_ARROW_S)
            await _moveInternal("_bw_" ,targetDistance,
                                lambda diff, slowOffset : diff > slowOffset,
                                lambda diff, stopOffset : diff > stopOffset,
                                lambda diff, adjustOffset : diff < -adjustOffset,
                                lambda diff, adjustOffset : diff > adjustOffset,
                                lambda yawSum : yawSum < 0,
                                speed)
    except Exception as e:
        sys.print_exception(e)
        log("[move] unable to reach target")
        pass


async def _moveInternal(label, targetDistance, funcNormal, funcSlow, funcYawLeft, funcYawRight, funcYawSum, speed=Speed.Slow):
    degreeWheel = int(targetDistance / Const_Wheel_C * 360 * Const_Distant_Adj)
    wheelAcceleration = speed * Const_Acceleration

    motor.reset_relative_position(port.B, 0)

    if(speed == Speed.Slow):
        velocityNormalStart = 500
        velocityNormalAdj = 50
        wheelAcceleration = Const_Acceleration
        wheelSlowOffset = 100
        wheelStopOffset = 50
        wheelAdjustOffset = 0.3

    elif(speed == Speed.Fast):
        velocityNormalStart = 1000
        velocityNormalAdj = 50
        wheelAcceleration = Const_Acceleration * 2
        wheelSlowOffset = 150
        wheelStopOffset = 50
        wheelAdjustOffset = 0.3


    yawStart = getYaw()
    degreeStart = motor.relative_position(port.B)
    degreeDiff = 0

    log(
        "[move",label,"] targetDistance=",targetDistance," c=",Const_Wheel_C," degreeWheel=",degreeWheel," yawStart=",yawStart, " velocityNormalStart=", velocityNormalStart, " velocityNormalAdj=", velocityNormalAdj, " wheelAcceleration=", wheelAcceleration
    )

    motor_pair.move_tank_for_degrees(
        motor_pair.PAIR_1,
        degreeWheel * 2,
        velocityNormalStart,
        velocityNormalStart,
        acceleration=wheelAcceleration,
        stop = motor.COAST
    )

    # start
    retry = 0
    # make sure the wheel has started moving towards right direction
    while( ((degreeWheel > 0 and degreeDiff < 10) or (degreeWheel < 0 and degreeDiff > -10)) and retry < 100):
        degreeEnd = motor.relative_position(port.B)
        degreeDiff = round(degreeEnd - degreeStart, 3)
        retry = retry + 1
        log("[turn",label,"a] degreeEnd=",degreeEnd," degreeDiff=", degreeDiff, " retry=",retry, logLevel = LogLevel.Detailed)
        time.sleep_ms(10)

    log(
        "[move",label,"b] move started"," degreeDiff=", degreeDiff, " degreeWheel=",degreeWheel, " retry=", retry
        # logLevel = LogLevel.Detailed,
    )

    retry = 0
    maxRetry = 30
    yawSum = 0
    while funcNormal(degreeDiff - degreeWheel, wheelSlowOffset) and retry < maxRetry:
        yawEnd = getYaw()
        yawDiff = round(yawEnd - yawStart, 3)
        yawSum += yawDiff
        # print(yawSum, " ", yawDiff)
        degreeEnd = motor.relative_position(port.B)
        degreeDiffLast = degreeDiff
        degreeDiff = round(degreeEnd - degreeStart, 3)
        if abs(degreeDiff - degreeDiffLast) < 1:
            retry = retry + 1
        else:
            retry = 0

        velocityAdj = abs(int(velocityNormalAdj*yawDiff))
        if(velocityAdj>10):
            velocityAdj = 10

        if funcYawLeft(yawDiff, wheelAdjustOffset) or funcYawSum(yawSum):
            log(
                "[move",label,"c <-] yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff, " degreeWheel=",degreeWheel, " degreeWheel", degreeWheel," degreeEnd=",degreeEnd," degreeDiff=",degreeDiff," retry=",retry,
                logLevel = LogLevel.Detailed,
            )
            motor_pair.move_tank_for_degrees(
                motor_pair.PAIR_1,
                degreeWheel,
                velocityNormalStart-velocityAdj,
                velocityNormalStart+velocityAdj,
                acceleration=wheelAcceleration,
                deceleration=wheelAcceleration,
                stop = motor.COAST
            )
        elif funcYawRight(yawDiff, wheelAdjustOffset) or not funcYawSum(yawSum):
            log(
                "[move",label,"c ->] yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff, " degreeWheel=",degreeWheel, " degreeEnd=",degreeEnd," degreeDiff=",degreeDiff," retry=",retry,
                logLevel = LogLevel.Detailed,
            )
            motor_pair.move_tank_for_degrees(
                motor_pair.PAIR_1,
                degreeWheel,
                velocityNormalStart+velocityAdj,
                velocityNormalStart-velocityAdj,
                acceleration=wheelAcceleration,
                deceleration=wheelAcceleration,
                stop = motor.COAST
            )
        else:
            log(
                "[move",label,"c <>] yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff, " degreeWheel=",degreeWheel," degreeEnd=",degreeEnd," degreeDiff=",degreeDiff," retry=",retry,
                logLevel = LogLevel.Detailed,
            )
            motor_pair.move_tank_for_degrees(
                motor_pair.PAIR_1,
                degreeWheel,
                velocityNormalStart,
                velocityNormalStart,
                acceleration=wheelAcceleration,
                deceleration=wheelAcceleration,
                stop = motor.COAST
            )

        time.sleep_ms(5)

    # slow down
    motor_pair.move_tank_for_degrees(
        motor_pair.PAIR_1,
        200,
        80,
        80,
        acceleration=wheelAcceleration,
        stop = motor.COAST
    )

    log(
        "[move",label,"d] slow down", " degreeWheel=",degreeWheel, " degreeDiff=", degreeDiff
    )

    retry = 0
    yawSum = 0
    # must use motor.BRAKE in slow down otherwise it drifts
    while funcSlow(degreeDiff - degreeWheel, wheelStopOffset) and retry < maxRetry:
        yawEnd = getYaw()
        yawDiff = round(yawEnd - yawStart, 3)
        yawSum += yawDiff
        degreeEnd = motor.relative_position(port.B)
        degreeDiffLast = degreeDiff
        degreeDiff = round(degreeEnd - degreeStart, 3)
        if abs(degreeDiff - degreeDiffLast) < 1:
            retry = retry + 1
        else:
            retry = 0

        velocityAdj = abs(int(velocityNormalAdj/5*yawDiff))
        if(velocityAdj > 5):
            velocityAdj = 5

        if funcYawLeft(yawDiff, wheelAdjustOffset) or funcYawSum(yawSum):
            log(
                "[move",label,"e <--] yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff, " degreeWheel=",degreeWheel, " degreeEnd=",degreeEnd," degreeDiff=",degreeDiff," retry=",retry,
                logLevel = LogLevel.Detailed,
            )
            motor_pair.move_tank_for_degrees(
                motor_pair.PAIR_1,
                degreeWheel,
                80-velocityAdj,
                80+velocityAdj,
                acceleration=400,
                deceleration=400,
                stop = motor.BRAKE
            )
        elif funcYawRight(yawDiff, wheelAdjustOffset) or not funcYawSum(yawSum):
            log(
                "[move",label,"e -->] yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff, " degreeWheel=",degreeWheel, " degreeEnd=",degreeEnd," degreeDiff=",degreeDiff," retry=",retry,
                logLevel = LogLevel.Detailed,
            )
            motor_pair.move_tank_for_degrees(
                motor_pair.PAIR_1,
                degreeWheel,
                80+velocityAdj,
                80-velocityAdj,
                acceleration=400,
                deceleration=400,
                stop = motor.BRAKE
            )
        else:
            log(
                "[move",label,"e -=-] yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff, " degreeWheel=",degreeWheel, " degreeEnd=",degreeEnd," degreeDiff=",degreeDiff," retry=",retry,
                logLevel = LogLevel.Detailed,
            )
            motor_pair.move_tank_for_degrees(
                motor_pair.PAIR_1,
                degreeWheel,
                80,
                80,
                acceleration=400,
                deceleration=400,
                stop = motor.BRAKE
            )
        time.sleep_ms(5)

    # stop
    motor_pair.stop(motor_pair.PAIR_1, stop = motor.BRAKE)
    time.sleep_ms(200)

    yawEnd = getYaw()
    yawDiff = round(yawEnd - yawStart, 3)
    degreeEnd = motor.relative_position(port.B)
    degreeDiff = round(degreeEnd - degreeStart, 3)
    degreeMiss = degreeWheel - degreeDiff

    log(
        "[move",label,"##] targetDistance=",targetDistance," degreeWheel=",degreeWheel," degreeDiff=",degreeDiff," degreeMiss=",degreeMiss," yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff
    )
    log(
        "[move",label,"@@@] degreeMiss=",degreeMiss, " yawDiff=",yawDiff
    )



# turn
async def turn(targetTurnDegree, speed=Speed.Slow):
    log("")
    log("[turn] targetTurnDegree=",targetTurnDegree)
    try:
        if(targetTurnDegree>0):
            #right
            # light_matrix.show_image(light_matrix.IMAGE_ARROW_E)
            await _turnInternal('->',
                                targetTurnDegree, 1,
                                lambda diff, offset : diff > offset, # slow down
                                lambda diff, offset : diff > offset, # stop
                                speed)
        elif(targetTurnDegree<0):
            #left
            # light_matrix.show_image(light_matrix.IMAGE_ARROW_W)
            await _turnInternal('<-',
                                targetTurnDegree, -1,
                                lambda diff, offset : diff < offset, # slow down
                                lambda diff, offset : diff < offset, # stop
                                speed)
    except Exception as e:
        sys.print_exception(e)
        log("[turn] unable to reach target")
        pass


async def _turnInternal(label, targetTurnDegree, direction, functNorm, funcSlow, speed=Speed.Slow):
    wheelDistance = Const_Wheel_Distance * Const_Pie / (360 / targetTurnDegree)
    wheelDegree = abs(int(wheelDistance / Const_Wheel_C * 360)) * 2 # ensure enough move

    yawStart = getYaw()
    yawEnd = getYaw()
    yawTarget = round(yawStart + targetTurnDegree, 3)
    yawDiff = (yawTarget - yawEnd)
    becomeNegative = False
    becomePositive = False
    if yawTarget > 0:
        becomeNegative = True
    elif yawTarget < 0:
        becomePositive = True

    motor.reset_relative_position(port.B, 0)
    degreeStart = motor.relative_position(port.B)
    degreeDiff = 0

    if(abs(targetTurnDegree) <= 40):
        speedVelocity = 100
        speedOffsetNormal = (0 + 5) * direction
        speedOffsetSlow = (0 + 0.8) * direction
    elif(abs(targetTurnDegree) <= 70):
        speedVelocity = 250
        speedOffsetNormal = (10 + 10) * direction
        speedOffsetSlow = (3.5 + 0.8) * direction
    elif(abs(targetTurnDegree) <= 140):
        speedVelocity = 300
        speedOffsetNormal = (15 + 10) * direction
        speedOffsetSlow = (7.5 + 0.8) * direction
    elif(abs(targetTurnDegree) <= 200):
        speedVelocity = 300
        speedOffsetNormal = (30 + 10) * direction
        speedOffsetSlow = (9.5 + 0.8) * direction
    else:
        speedVelocity = 300
        speedOffsetNormal = (40 + 10) * direction
        speedOffsetSlow = (10 + 0.8) * direction

    log(
        "[turn",label,"] targetTurnDegree=",targetTurnDegree," wheelDegree=", wheelDegree," yawTarget=",yawTarget," yawStart=",yawStart, " yawDiff=", yawDiff, " becomeNegative=", becomeNegative, " becomePositive=", becomePositive, " speedOffsetNormal=", speedOffsetNormal, " speedOffsetSlow=", speedOffsetSlow, " speedVelocity=", speedVelocity
    )

    # more speed seems to mess up yaw reading, stuck at -180
    motor_pair.move_tank_for_degrees(
        motor_pair.PAIR_1,
        wheelDegree,
        speedVelocity * direction,
        speedVelocity * -1 * direction,
        acceleration=Const_Acceleration,
        deceleration=Const_Acceleration,
        stop = motor.COAST
    )

    # startup
    retry = 0
    while(abs(degreeDiff) < 10 and retry < 100):
        degreeEnd = motor.relative_position(port.B)
        degreeDiff = round(degreeEnd - degreeStart, 3)
        retry = retry + 1
        log("[turn",label,"a] degreeEnd=",degreeEnd," degreeDiff=", degreeDiff, " retry=",retry, logLevel = LogLevel.Detailed)
        time.sleep_ms(10)

    log(
        "[turn",label,"b] turn start", " degreeDiff=", degreeDiff, " yawDiff=",yawDiff, " retry=", retry
    )

    retry = 0
    maxRetry = 30
    offSet = 0
    while functNorm(yawDiff, speedOffsetNormal) and retry < maxRetry:
        degreeEnd = motor.relative_position(port.B)
        degreeDiffLast = degreeDiff
        degreeDiff = round(degreeEnd - degreeStart, 3)

        yawEndLast = yawEnd
        yawEnd = getYaw()
        if(becomeNegative == True and yawEnd < -150 and yawEndLast > 150):
            offSet = 360
        if(becomePositive == True and yawEnd > 150 and yawEndLast < -150):
            offSet = -360
        yawEnd = yawEnd + offSet
        yawDiff = round(yawTarget - yawEnd, 3)

        if abs(degreeDiff - degreeDiffLast) < 1:
            retry = retry + 1
        else:
            retry = 0

        log("[turn",label,"c] yawEnd=",yawEnd," yawDiff=",yawDiff, " offSet=", offSet, " degreeEnd=",degreeEnd, " degreeDiff=", degreeDiff," speedOffsetNormal=",speedOffsetNormal," retry=",retry, logLevel = LogLevel.Detailed)
        time.sleep_ms(15)

    # must set to motor.BRAKE, otherwise it drifts
    motor_pair.move_tank_for_degrees(
        motor_pair.PAIR_1,
        180,
        80 * direction,
        80 * -1 * direction,
        acceleration=Const_Acceleration,
        deceleration=Const_Acceleration,
        stop = motor.BRAKE
    )

    retry = 0
    log(
        "[turn",label,"d] slow down", " yawDiff=", yawDiff, " offSet=", offSet, " speedOffset=",speedOffsetSlow, " retry=", retry
    )

    while funcSlow(yawDiff, speedOffsetSlow) and retry < maxRetry:
        degreeEnd = motor.relative_position(port.B)
        degreeDiffLast = degreeDiff
        degreeDiff = round(degreeEnd - degreeStart, 3)

        yawEndLast = yawEnd
        yawEnd = getYaw()
        if(becomeNegative == True and yawEnd < -150 and yawEndLast > 150):
            offSet = 360
        if(becomePositive == True and yawEnd > 150 and yawEndLast < -150):
            offSet = -360
        yawEnd = yawEnd + offSet
        yawDiff = round(yawTarget - yawEnd, 3)

        if abs(degreeDiff - degreeDiffLast) < 1:
            retry = retry + 1
        else:
            retry = 0
        log("[turn",label,"e] yawEnd=",yawEnd," yawDiff=",yawDiff," offSet=", offSet, " degreeEnd=",degreeEnd," degreeDiff=", degreeDiff, " speedOffsetSlow=",speedOffsetSlow," retry=",retry, logLevel = LogLevel.Detailed)
        time.sleep_ms(5)

    motor_pair.stop(motor_pair.PAIR_1)
    time.sleep_ms(200)

    yawEnd = getYaw()
    if(becomeNegative == True and yawEnd < -150 and yawEndLast > 150):
        offSet = 360
    if(becomePositive == True and yawEnd > 150 and yawEndLast < -150):
        offSet = -360
    yawEnd = yawEnd + offSet
    yawDiff = round(yawTarget - yawEnd, 3)
    log(
        "[turn",label,"##] targetTurnDegree=",targetTurnDegree," yawTarget=",yawTarget," yawStart=",yawStart," yawEnd=",yawEnd," yawDiff=",yawDiff
    )
    log(
        "[turn",label,"@@@] yawDiff=",yawDiff
    )


# rotate
async def rotateTop(targetDegree, speed=Speed.Slow):
    await rotate(port.D, targetDegree, 1.38, speed)


async def rotateFront(targetDegree, speed=Speed.Slow):
    await rotate(port.C, targetDegree, 0.6, speed)


async def rotate(port, targetDegree, rate, speed=Speed.Slow):
    rotationSpeed = speed * 180
    rotationDegree = int(targetDegree * rate)
    log(
        "[rotate] port=",port," targetDegree=",rotationDegree," rotationDegree=",rotationDegree
    )
    await motor.run_for_degrees(port, rotationDegree, rotationSpeed, stop= motor.BRAKE)


def log(*args, logLevel=LogLevel.Normal):
    if logLevel >= Const_Level:
        # stamp = time.strftime('%H:%M:%S', time.gmtime(12345))
        # print(*args, sep='')
        i = 1


Const_StartTime = time.ticks_ms()
Const_EndTime = time.ticks_ms()
def timerStart():
    global Const_StartTime
    Const_StartTime = time.ticks_ms()
    print("[timer] StartTime=", Const_StartTime, sep='')

async def timerEnd():
    global Const_EndTime
    Const_EndTime = time.ticks_ms()
    diff = time.ticks_diff(Const_EndTime, Const_StartTime)
    print("[timer##] Diff=", diff / 1000, "s (", diff,"ms)", " StartTime=", Const_StartTime, " EndTime=", Const_EndTime, sep='')
    return math.ceil(diff / 1000)


def buzz():
    sound.beep(880, 200, 100)


### setting
Const_Acceleration = 300
Const_Speed = 500
Const_Pie = 3.1415926
Const_Wheel_R = 4.8 / 2
Const_Wheel_C = 2 * Const_Wheel_R * Const_Pie# 15.0796
Const_Wheel_Distance = 9.6

Const_Level = LogLevel.Normal
Const_Move_Adj = 27# stop motor in advance to offset momentan
Const_Curve_Adj = 5# stop motor in advance to offset momentan
Const_Distant_Adj = 0.8# wheel length / distance offset
Const_Steering_Adj = 11# wheel length / distance offset

# main code
runloop.run(main())