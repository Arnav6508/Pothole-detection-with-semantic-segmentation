from ultralytics import YOLO
import cv2

model_path = './best.pt'
model = YOLO(model_path)

def test_on_video(video_path):

    cap = cv2.VideoCapture(video_path)
    ret = True

    while ret:
        ret, frame = cap.read()
        if not ret: break
        H, W, _ = frame.shape

        result = model(frame)[0]

        # Show bounding box
        if result and result.boxes.xyxy != None:
            for box in result.boxes.xyxy:
                box = box.numpy()
                cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (255, 255, 255), 1)
                cv2.putText(frame, 'Pothole', (int(box[0]), int(box[1])-5), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Segment and count potholes
        if result and len(result.masks) != 0: 

            potholes = 0
            for mask in result.masks.data:

                mask = mask.numpy()*255
                mask = cv2.resize(mask, (W, H))
                mask = mask.astype('uint8')

                colored_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                colored_mask[:, :, 1:] = 0 

                frame = cv2.addWeighted(frame, 1, colored_mask, 1, 0)
                potholes += 1
        
        cv2.putText(frame, f'Pothole Count: {potholes}', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow('frame', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()


def test_on_image(image_path):

    img = cv2.imread(image_path)
    H, W, _ = img.shape

    result = model(img)[0]
    result.save(filename="./result/prediction.png")

    for j, mask in enumerate(result.masks.data):
        mask = mask.numpy()*255
        mask = cv2.resize(mask, (W, H))
        cv2.imwrite(f'./result/maskt_{j}.png', mask)
        
    result.show()