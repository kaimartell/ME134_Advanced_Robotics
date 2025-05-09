import time, math, gc, os
from Husky.huskylensPythonLibrary import HuskyLensLibrary

# husky = HuskyLensLibrary(proto="I2C")  # or "SERIAL" depending on your connection
# husky.tag_recognition_mode()
# while True:
#     data = husky.command_request_blocks_learned()
#     print(data)
#     for i in data:
#         area = i[3]*i[2]
#         print(f'Tag {i[4]} has an area of {area}')
#     time.sleep_ms(500)


def read_tags(husky):
    husky.tag_recognition_mode() # Switch to tag recon mode
    time.sleep_ms(100) # Wait for camera data to become available
    data = husky.command_request_blocks_learned()
    
    # Parse through available tags
    for i in data:
        tag_x = i[0]
        tag_y = i[1]
        area = i[2]*i[3]
        id = i[4]
        print(f'Tag {id} has an area of {area}')

husky = HuskyLensLibrary(proto="I2C")
while True:
    read_tags(husky)