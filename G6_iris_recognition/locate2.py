from G6_iris_recognition.pupil2 import *
from G6_iris_recognition.iris2 import *
from numpy import zeros
from skimage import draw

def locate(img):
  # global east_mark, south_mark, west_mark, north_mark
  try:
    pupil_img = pupil_detect(img)
    rows = pupil_img.shape[0]
    cols = pupil_img.shape[1]

    for col in range(cols):
        col = cols - 1 - col
        if sum(pupil_img[:,col]) > 0:
            east_mark = col
            break

    for col in range(east_mark):
        col = east_mark - 1 - col
        if sum(pupil_img[:,col]) == 0:
            west_mark = col
            break

    for row in range(rows):
        row = rows - 1 - row
        if sum(pupil_img[row,:]) > 0:
            south_mark = row
            break

    for row in range(south_mark):
        row = south_mark - 1 - row
        if sum(pupil_img[row,:]) == 0:
            north_mark = row
            break

    center_x = int((west_mark + east_mark) / 2)
    center_y = int((north_mark + south_mark) / 2)

    lines = zeros([rows,cols])
    rr, cc = draw.line(south_mark,east_mark,north_mark,east_mark)
    lines[rr,cc] = 1
    rr, cc = draw.line(south_mark,west_mark,north_mark,west_mark)
    lines[rr,cc] = 1
    rr, cc = draw.line(south_mark,west_mark,south_mark,east_mark)
    lines[rr,cc] = 1
    rr, cc = draw.line(north_mark,west_mark,north_mark,east_mark)
    lines[rr,cc] = 1
    rr, cc = draw.disk((center_y,center_x),3)
    lines[rr,cc] = 1

    #Locating Iris bounding box
    iris_img = iris_detect(img)

    x = east_mark
    while(iris_img[center_y,x]) == 1: x += 1
    iris_east = x

    x = west_mark
    while(iris_img[center_y,x]) == 1: x -= 1
    iris_west = x

    rr, cc = draw.line(0,iris_east,rows-1,iris_east)
    lines[rr,cc] = 1
    rr, cc = draw.line(0,iris_west,rows-1,iris_west)
    lines[rr,cc] = 1

    # Displaying bounding boxes with lines
    full_color = zeros([rows,cols,3])
    for i in range(rows):
        for j in range(cols):
            full_color[i,j,0] = pupil_img[i,j]
            full_color[i,j,1] = lines[i,j]

    for i in range(rows):
        for j in range(cols):
            full_color[i,j,2] = iris_img[i,j]

    #print('Eastern distance: ' + str(iris_east - center_x))
    #print('Western distance: ' + str(center_x - iris_west))
    #disp(full_color)

    # Generating mask:
    radius = max([(iris_east - center_x),(center_x - iris_west)])
    mask = zeros([rows,cols])

    rr, cc = draw.disk((center_y, center_x),radius)
    for i in range(len(rr)):
        if rr[i] < 0: rr[i] = 0
        if rr[i] >= rows: rr[i] = rows - 1
    for i in range(len(cc)):
        if cc[i] < 0: cc[i] = 0
        if cc[i] >= cols: cc[i] = cols - 1
    mask[rr,cc] = 1

    # rr, cc = draw.circle(center_y, center_x,(0.5*(east_mark-west_mark)))
    rr, cc = draw.disk((center_y, center_x),(0.5*(east_mark-west_mark)))

    for i in range(len(rr)):
        if rr[i] < 0: rr[i] = 0
        if rr[i] >= rows: rr[i] = rows - 1
    for i in range(len(cc)):
        if cc[i] < 0: cc[i] = 0
        if cc[i] >= cols: cc[i] = cols - 1
    mask[rr,cc] = 0

    # img = bnw(fname)
    # img = fname
    pad = 0
    masked_eye = zeros([img.shape[0]-2*pad,img.shape[1]-2*pad])
    for i in range(rows):
            for j in range(cols):
                masked_eye[i,j] = min([mask[i,j],img[pad+i,pad+j]])

    check_mask = zeros([rows,cols,3])
    for i in range(rows):
        for j in range(cols):
            check_mask[i,j,0] = img[i,j] * 0.8
            check_mask[i,j,1] = img[i,j] * (0.8 + 0.2*mask[i-2*pad,j-2*pad])
            check_mask[i,j,2] = img[i,j] * (0.8 + 0.2*mask[i-2*pad,j-2*pad])

    inner_radius = 0.5 * (east_mark - west_mark)
    outer_radius = 0.5 * (iris_east - iris_west)
    center_r, center_c = center_y,center_x
    return [inner_radius, outer_radius, (center_r, center_c)]
  except Exception as e:
      print("locate expression 1",e)
      return "invalid image"