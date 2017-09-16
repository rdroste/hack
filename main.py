import numpy as np
import cv2
import os, time
import pegboard as peg
import utils
import multiprocessing as mp

DEBUG = True

nCoins = 3
emotion_key = os.environ['MICROSOFT_EMOTION']

# Main routine
if __name__ == '__main__':

    # Initialize all the connections with yumi and the camera
    if DEBUG:
        cap = cv2.VideoCapture("peg.avi")
    else:
        cap = utils.prepare_camera()

    # Yumi says hi and explains the experiment

    # Test 1: The pegboard experiment

    # Yumi explains the pegboard experiment

    # Start the experiment
    # Initialize the pegboard
    ret, frame = cap.read()
    if ret:
        initImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rectList = peg.initPegboard(initImg.copy())
        expRunning = True
        # Yumi shows the pegboard routine

        # Yumi tells the person to do routine (and countdown maybe?)


        while expRunning:
            # Start facial/behavioral analysis with 10 sec timer
            ret, currImg = cap.read()
            # Feed the image to sentiment analysis

            expRunning = False

        # Evaluate the board
        ret, frame = cap.read()
        currImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        score = peg.assessRoutine(initImg, currImg, rectList)

    roi_coords = np.array([[323, 472], [243, 411]]) # [[411, 243], [472, 323]] for coin_test_1.mp4
    # results = vision_coin.run(3, roi_coords)
    if DEBUG:
        # cap = cv2.VideoCap    ture("./coin_test_1.mp4")
        cap = cv2.VideoCapture("./coin_test_2.avi")

    # ret, frame = cap.read()
    # currImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('image',currImg)
    # cv2.waitKey()

    # Yumi explains the coin experiment

    # Start the experiment

    # Initialize test 2: The coin experiment
    # roi_coords = np.array([[323, 472], [243, 411]])  # [[411, 243], [472, 323]] for coin_test_1.mp4
    roi_coords = np.array([[282, 349], [219, 282]])  # [[411, 243], [472, 323]] for coin_test_1.mp4
    ref_n_frames = 2
    sos_n_frames = 4
    asos_train = 4
    asos_thr_factor = 5
    coin_thr = 20
    time_thr_coins = 20 # seconds
    filepath = './tmp.png'

    roi_size = roi_coords[:, 1] - roi_coords[:, 0]
    asos_array = np.zeros(asos_train)
    reference = np.zeros(roi_size)
    ref_frames = np.zeros((roi_size[0], roi_size[1], ref_n_frames))
    sos_array = np.zeros(sos_n_frames)
    coin_times = np.zeros(nCoins)

    roi_counter = 0
    frame_counter = 0
    asos_train_counter = 0
    coin_frame = -1000
    asos_thr = 0
    coin_counter = 0
    emotions = []
    p = mp.Pool()
    mp_counter = 0
    r = []
    # r = p.apply_async(utils.get_emotion, args=(filepath, emotion_key))

    init_time = time.time()
    this_init_time = init_time

    # Throw away the first frames
    for i in range(20):
        cap.read()

    expRunning = True
    while expRunning:

        if time.time() - init_time > time_thr_coins:
            break

        ret, frame = cap.read()
        if not ret:
            expRunning = False
            continue

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Motion Tracking here...

        # Emotion analysis
        if frame_counter % 20 == 0:
            # if frame_counter > 0:
            #     # s.join()
            #     # p.join()
            #     # p.close()
            #     # r.close()
            #     emotion_nr, emotion_certainty = r.get()
            #
            #     if emotion_nr:
            #         print(emotion_nr)
            #         print(emotion_certainty)
            #         # cv2.waitKey()

            utils.save_image(img)
            # s = mp.Process(target=utils.get_emotion, args=(filepath, emotion_key))
            # s.start()
            r.append(p.apply_async(utils.get_emotion, args=(filepath, emotion_key)))
            mp_counter = mp_counter + 1


        # Detect coin in ROI
        if frame_counter % 2 == 0:
            # Get roi and blur
            roi = img[roi_coords[0,0]:roi_coords[0,1], roi_coords[1,0]:roi_coords[1,1]]
            roi = cv2.GaussianBlur(roi, (13, 13), 0)

            # Get frame for reference and update reference if necessary
            ref_frames[:,:, roi_counter % ref_n_frames] = roi
            if roi_counter % ref_n_frames == ref_n_frames - 1:
                reference = np.mean(ref_frames, axis=2)

            # If a reference has been created and the last coin is some frames ago, compute SOS
            if roi_counter >= ref_n_frames - 1 and frame_counter - coin_frame > coin_thr:
                sos_array[roi_counter % sos_n_frames] = np.sum(np.square(roi - reference))

                # If the SOS array is full, compute the average
                if roi_counter % sos_n_frames == sos_n_frames - 1:
                    asos = np.mean(sos_array)

                    # Compute a few average SOS to set the threshold
                    if asos_train_counter < asos_train:
                        asos_array[asos_train_counter] = asos
                        if asos_train_counter == asos_train - 1:
                            asos_thr = asos_thr_factor * np.mean(asos_array)
                        asos_train_counter = asos_train_counter + 1

                    # Check if asos threshold is exceeded
                    else:
                        if asos > asos_thr:
                            coin_counter = coin_counter + 1
                            print (coin_counter)
                            if coin_counter == nCoins:
                                expRunning = False
                            sos_array = np.zeros(sos_n_frames)
                            coin_frame = frame_counter

                            # Add timer
                            coin_times[coin_counter - 1] = time.time() - this_init_time
                            this_init_time = time.time()

            if DEBUG:
                cv2.imshow('image', img)
                cv2.waitKey(120)
                roi_counter = roi_counter + 1

        # Feed the image to sentiment analysis

        frame_counter = frame_counter + 1

    emotion_nr = np.zeros(mp_counter)
    emotion_certainty = np.zeros(mp_counter)
    for i in range(mp_counter):
        emotion_nr[i], emotion_certainty[i] = r[i].get()

    p.close()
    p.join()

    print(coin_times)


    utils.close_camera(cap)