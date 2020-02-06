"""
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    Scanner(
        # frame_provider=VideoFrameProvider('images\\VID_20200205_080142.mp4'),
        frame_provider=RandomStoredImageFrameProvider()
        # plate_extractor=PlateExtractor(),
        # ocr=Ocr(),
        # plate_lookup=PlateLookup()
    ).run()
    """

    """
    x = PlateExtractor()
    img = cv2.imread('images\\jeep.jpg')
    plate = x.get_plate_crops(img)[0]
    #cv2.imshow("original", img)
    #cv2.imshow("plate", plate)
    plate_crop = cv2.adaptiveThreshold(
                    cv2.cvtColor(plate, cv2.COLOR_RGB2GRAY),
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    11,
                    2)
    cv2.imshow("plate", plate_crop)
    plate_number = pytesseract.image_to_string(Image.fromarray(plate_crop))
    print(plate_number)
    cv2.waitKey(0)
    """
