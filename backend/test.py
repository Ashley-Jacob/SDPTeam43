import pandas as pd
import cv2

filename = "hello.png"
imgs = pd.read_csv("images.csv")
print(imgs)
imgs = pd.concat([imgs, pd.DataFrame([filename], columns=imgs.columns)], ignore_index=True)
#imgs += filename
'''if imgs.size > 10:
    imgs = imgs.iloc[1:]
    '''
print(imgs)
#imgs.to_csv("images.csv", index=False)
# cv2.imwrite(filename, frame)