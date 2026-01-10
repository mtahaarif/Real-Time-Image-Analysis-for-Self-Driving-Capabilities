import cv2
import numpy as np

def detect_obstacles(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    color_range_min = np.array([0, 45, 50])
    color_range_max = np.array([15, 255, 255])

    obstacle_mask = cv2.inRange(hsv_frame, color_range_min, color_range_max)

    contours, _ = cv2.findContours(obstacle_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    detected_boxes = []

    for cnt in contours:
        if cv2.contourArea(cnt) > 150:
            x, y, width, height = cv2.boundingRect(cnt)
            detected_boxes.append((x, y, width, height))
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255,0), 2)
            cv2.putText(frame, "Object", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255,0), 2)

    return frame, detected_boxes

def directional_decision_making(road,highlighted_frame,object,x1,x2, y1,y2):
    highlighted_frame[x1:x2, y1:y2] = object
    check_upward=True
    check_right=True
    check_left=True
    check_backward=True
    for i in range (y1,y2):                                                             ### check for forward
        if [road[x1-1,i][0],road[x1-1,i][1],road[x1-1,i][2]]==[0,255,255]:        ### move upwards
            pass
        else:
            check_upward=False
    
    if (check_upward==True) :
        x1-=1
        x2-=1
    else:
        for i in range (x1,x2):                                                             ### check for right
            if [road[i,y2+1][0],road[i,y2+1][1],road[i,y2+1][2]]==[0,255,255] :        ### move right
                pass
            else:
                check_right=False
        
        if (check_right==True) or [road[i,y1-20][0],road[i,y1-20][1],road[i,y1-20][2]]!=[0,255,255]:
            y1+=1
            y2+=1
        else:            
            for i in range (x1,x2):                                                             ### check for left
                if [road[i,y1-1][0],road[i,y1-1][1],road[i,y1-1][2]]==[0,255,255] :        ### move left
                    pass
                else:
                    check_left=False
            
            if (check_left==True) or [road[i,y2+20][0],road[i,y2+20][1],road[i,y2+20][2]]!=[0,255,255]:
                y1-=1
                y2-=1

            else: 
                for i in range (y1,y2):                                                             ### check for backward
                    if [road[x1+1,i][0],road[x1+1,i][1],road[x1+1,i][2]]==[0,255,255]:        ### move backward
                        pass
                    else:
                        check_backward=False
                
                if (check_backward==True) or [road[x1-20,i][0],road[x1-20,i][1],road[x1-20,i][2]]!=[0,255,255]:
                    x1+=1
                    x2+=1
    return highlighted_frame,x1,x2, y1,y2

def highlight_largest_lane_region(frame, edge_pixel_thresh=100):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    kernel = np.ones((5, 5), np.uint8)
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    inv = cv2.bitwise_not(closed_edges)

    height, width = inv.shape
    bottom = inv[height // 2:, :]

    _, binary = cv2.threshold(bottom, 127, 255, cv2.THRESH_BINARY)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    min_area = 4000
    best_label = -1
    best_score = 0

    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        if area < min_area:
            continue

        component_mask = (labels == i).astype(np.uint8) * 255
        edge_pixels_in_component = cv2.bitwise_and(bottom, bottom, mask=component_mask)
        nonzero_edge_count = cv2.countNonZero(edge_pixels_in_component)

        if nonzero_edge_count < edge_pixel_thresh:
            continue

        cx, cy = centroids[i]
        distance_from_center = abs((width / 2) - cx)
        vertical_position_score = h
        score = area - 5 * distance_from_center + vertical_position_score

        if score > best_score:
            best_score = score
            best_label = i

    if best_label == -1:
        return frame, edges

    mask = np.zeros_like(binary)
    mask[labels == best_label] = 255

    full_mask = np.zeros_like(gray)
    full_mask[height // 2:, :] = mask

    contours, _ = cv2.findContours(full_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    overlay = frame.copy()
    for cnt in contours:
        cv2.drawContours(overlay, [cnt], -1, (0, 255, 255), -1)  

    blended = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
    return overlay, edges,blended

def process_video_realtime(video_path):
    cap = cv2.VideoCapture(video_path)
    obj = np.ones((20, 20, 3), dtype=np.uint8) * np.array([0, 0, 255], dtype=np.uint8)
    x1, x2 = 400, 420
    y1, y2 = 250 - 10, 250 + 10  

    if not cap.isOpened():
        print("Failed to open video.")
        return

    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (640, 480))

        if not ret:
            break

        frame, _ = detect_obstacles(frame)
        frame, edge_map,highlighted_frame = highlight_largest_lane_region(frame)
        frame, x1, x2, y1, y2 = directional_decision_making(frame,highlighted_frame, obj, x1, x2, y1, y2)


        cv2.imshow("Edge Map", edge_map)
        cv2.imshow("Lane and Obstacle Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

process_video_realtime('E:/Documents/6th Semester/DIP/Lab/Project/DIP Project Videos/q1.mp4')
