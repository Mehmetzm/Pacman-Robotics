from random import randint
import cv2
try:
    from pypylon import pylon # type: ignore
except ImportError:
    print("konnte pypylon nicht importieren, Debugmodus wird verwendet")
    pylon = None
import cv2.aruco as aruco
import numpy as np
import time

def transformPunkt(pt, transform_matrix):
    """
    pt: punkt zum umwandeln
    transform_matrix: Matrix zur Transformation
    """
    punkt = np.array([*pt, 1.0], dtype=np.float32)
    punkt_proj = transform_matrix @ punkt
    punkt_proj /= punkt_proj[2]
    return punkt_proj[:2]

class Pac_Coords():
        x_proj = 1920//2
        y_proj = 1080//2

def set_coords(value):
    Pac_Coords.x_proj = int(value[0])
    Pac_Coords.y_proj = int(value[1])

def main():
    if not pylon:
        import settings
        while True:
            if Pac_Coords.x_proj < 0:
                Pac_Coords.x_proj += settings.TILE_WIDTH
            elif Pac_Coords.x_proj > settings.SCREEN_WIDTH:
                Pac_Coords.x_proj += -settings.TILE_WIDTH
            elif Pac_Coords.y_proj < 0:
                Pac_Coords.y_proj += settings.TILE_HEIGHT
            elif Pac_Coords.y_proj >= settings.SCREEN_HEIGHT:
                Pac_Coords.y_proj += settings.TILE_HEIGHT
            else:
                choice = randint(0,4)
                if choice == 1:
                    Pac_Coords.y_proj += settings.TILE_HEIGHT
                elif choice == 2:
                    Pac_Coords.y_proj -= settings.TILE_HEIGHT
                elif choice == 3:
                    Pac_Coords.x_proj += settings.TILE_WIDTH
                else:
                    Pac_Coords.x_proj -= settings.TILE_WIDTH
            time.sleep(0.5)
    else:
        try:
            camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            camera.Open()
            camera.ExposureTime.SetValue(35000)
            print("Kamera erfolgreich verbunden.")
        except Exception as e:
            print("Keine Kamera verfügbar:", str(e))
            return

        # Grabing Continusely (video) with minimal delay
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
        converter = pylon.ImageFormatConverter()

        # umwandeln zu opencv bgr format
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        # Parameter
        dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        parameters = aruco.DetectorParameters()
        parameters.adaptiveThreshConstant = 20  #20 7 5 3
        #parameters.adaptiveThreshWinSizeMin = 15 #13 
        #parameters.adaptiveThreshWinSizeMax = 50 #53
        #parameters.adaptiveThreshWinSizeStep = 5
        # Mehr Toleranz für verzerrte Formen
        parameters.polygonalApproxAccuracyRate = 0.08  
        parameters.maxErroneousBitsInBorderRate = 0.9
        # Präzisere Ecken
        parameters.cornerRefinementMethod = aruco.CORNER_REFINE_SUBPIX  
        punkte = []
        markerId = [14]
        farbe=(0,0,0)
        rioSize = 100 #80
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        frame_width = camera.Width.Value
        frame_height = camera.Height.Value
        zeit = []
        nErkannt= 0

        # Erstelle ArUco detector
        detector = aruco.ArucoDetector(dictionary, parameters)

        # Bildpunkte (projiziertes Rechteck)
        src_pts = np.array([[137,420], [1849,397], [1878,1368], [139,1397]], dtype=np.float32)
        # Zielrechteckgröße
        width, height = 1920, 1080
        projektion = np.ones((height,width,3),np.uint8)*255 
        dst_pts = np.array([[0, 0], [1920, 0], [1920, 1080], [0, 1080]], dtype=np.float32)
        transform_matrix, _ = cv2.findHomography(src_pts, dst_pts)



        while camera.IsGrabbing():
            grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                start = time.time()
                # Access the image data
                image = converter.Convert(grabResult)
                frame = image.GetArray()

                # Bildausschnitt 
                if len(punkte) <= 0:
                    # In Graustufen umwandeln
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = clahe.apply(gray)
                    y1, y2, x1, x2 = 0,0,0,0
                else:
                    x_min, y_min = np.min(punkte, axis=0)
                    x_max, y_max = np.max(punkte, axis=0)
                    y1 = int(max(y_min - rioSize, 0))
                    y2 = int(min(y_max + rioSize,frame_height))
                    x1 = int(max(x_min - rioSize, 0))
                    x2 = int(min(x_max + rioSize,frame_width))
                    rio = frame[y1:y2, x1:x2]
                    gray = cv2.cvtColor(rio, cv2.COLOR_BGR2GRAY) 

                # markers erkennen
                corners, ids, rejected = detector.detectMarkers(gray)
                punkte = []
            
                # Marker einzeichnen
                if ids is not None:
                    # Mittelpunkt des Roboters berechnen
                    for marker_corners, marker_id in zip(corners, ids):
                        corners_reshaped = marker_corners[0] + [x1,y1]
                        # Mittelpunkt berechnen
                        center_x = np.mean(corners_reshaped[:, 0])
                        center_y = np.mean(corners_reshaped[:, 1])
                        # Roboter mittelpunkt
                        mPunkt = np.array([center_x, center_y])
                        
                        #######################################
                        # Das sind die ermittelten Koordinaten des Roboters
                        #Pac_Coords.x_proj, Pac_Coords.y_proj = transformPunkt(mPunkt,transform_matrix)
                        set_coords(transformPunkt(mPunkt,transform_matrix))
                        # farbe anpassen bei mehren Markern
                        #if marker_id == markerId[0]:
                            #farbe=(255,0,0)
                        #else:
                            #frabe=(0,0,255)
                        #cv2.circle(projektion, (int(x_proj), int(y_proj)), 2, (0,0,255), 8)
                        punkte.append(mPunkt)
                else:
                    nErkannt = nErkannt+1
                # Video anzeigen 
                #cv2.namedWindow('Vollbild', cv2.WINDOW_NORMAL)
                #cv2.setWindowProperty('Vollbild', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                #cv2.imshow('Vollbild', projektion)
                k = cv2.waitKey(1)
                if k == 27:
                    break
                end = time.time()
                zeit.append(end-start)
            grabResult.Release()

        # Releasing the resource    
        camera.StopGrabbing()
        camera.Close()
        cv2.destroyAllWindows()
        print(max(zeit))
        print(1/min(zeit))
        print(1/np.average(zeit))
        print (f"Anzahl nicht erkannte {nErkannt}")
        print("alle Parameter außer thresh schrittweise")