# -*- coding: utf-8 -*-

# This file provides settings for the application

file = open("alexa_skill_id.txt")
ALEXA_SKILL_ID = file.read()
file.close()

IMAGE_PATH: str = "./images"

imageRatingName: str = "imageRatings.json"


DOWNLOAD_FROM_GOOGLE: bool = False
DOWNLOAD_FROM_ICLOUD: bool = False
ICLOUD_EMAIL: str = ""
ICLOUD_PASSWORD: str = ""
CLOUD_FOLDER: str = "smart picture frame"

ENABLE_DEBUGGING = False
RUNS_ON_RPI: bool = True

touch_threshold: int = 40
"""this is the touch threshold - setting it low makes it more like a proximity trigger default value is 40 for touch"""

release_threshold: int = 20
"""this is the release threshold - must ALWAYS be smaller than the touch threshold default value is 20 for touch"""

autoImgChangeTime = 60 * 2
"""number of seconds before image changes automatically"""

GYROSCOPE_LEFT_ROTATION_THRESHOLD: int = 70
GYROSCOPE_RIGHT_ROTATION_THRESHOLD: int = -70
GYROSCOPE_UP_ROTATION_THRESHOLD: int = 70
GYROSCOPE_DOWN_ROTATION_THRESHOLD: int = -70

HAND_LEFT = 100
HAND_RIGHT = 470
