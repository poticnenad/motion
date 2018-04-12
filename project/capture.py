import cv2
from datetime import datetime
import pandas as pd


first_frame = None
status_list = [None, None]
times = []
df = pd.DataFrame(columns=["Start", "End"])

# Startujem web kameru (0 = primarna kamera)
video = cv2.VideoCapture(0)

while True:
    check, frame = video.read()

    # Nema pokreta u tekucem (prvom) frejmu
    status = 0

    # Konvertujem frejm u crno/belu skalu
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blurujem kako bi 'smanjio' osetljivost na pokret
    # (GaussianBlur([frejm], [blur parametri - tuple], [stand.dev.]))
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Deklarisem prvi frejm kao referencu ili pozadinu
    if first_frame is None:
        first_frame = gray
        continue

    # delta_frame je frejm koji je razlika izmedju first_frame i gray
    delta_frame = cv2.absdiff(first_frame, gray)

    # thresh_frame koristimo kao sliku/frejm (THRESH_BINARY metoda vraca listu, frejm je drugi po redu u listi)
    # threshold([frejm],
    #           [min. vrednost na datoj poziciji u frejmu],
    #           [ako je prekoracena vrednost -> menjamo je direktno u 255 (belo)],
    #           [izabrana metoda])
    thresh_frame = cv2.threshold(delta_frame, 100, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    (_,cnts,_) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtriram cnts (listu kontura) i prihvatam samo one koje zadovoljavaju kriterijum (dole)
    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        # Pokret je detektovan
        status = 1

        # Kreiramo pravougaonik oko konture, definisemo njegove dimenzije
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
    status_list.append(status)

    # Belezimo SAMO promene stanja (pozitivnu detekciju, ili negativnu)
    # tako da ce u listi biti naizmenicno 0 i 1
    status_list = status_list[-2:]
    if status_list[-1] == 1 and status_list[-2] == 0:
        times.append(datetime.now())
    if status_list[-1] == 0 and status_list[-2] == 1:
        times.append(datetime.now())

    # Izlaz na 4 prozora:
    cv2.imshow("Grey Frame", gray)
    cv2.imshow("Delta Frame", delta_frame)
    cv2.imshow("Threshold Frame", thresh_frame)
    cv2.imshow("Current Frame", frame)

    key = cv2.waitKey(1)

    # Klikom na taster 'q' se zavrsava 'snimanje' (i prikazuje .html sa dijagramom)
    if key == ord('q'):
        if status == 1:
            times.append(datetime.now())
        break

# U .csv upisujem, takodje, samo promene stanja (mirno, ili pokret detektovan - naizmenicno)
for i in range(0, len(times), 2):
    df = df.append({"Start": times[i], "End": times[i+1]}, ignore_index=True)
df.to_csv("times.csv")


# Gasi se kamera i zatvaraju svi (4) prozori
video.release()
cv2.destroyAllWindows
