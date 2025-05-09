from main import Robot

robot = Robot('Black')

prev_state = ''

while not robot.done:
    robot.check_state()
    if prev_state != robot.state:
        print(robot.state)
    time.sleep_ms(5)
    prev_state = robot.state