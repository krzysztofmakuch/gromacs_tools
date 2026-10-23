import cv2
import os
import re


def list_of_png(pattern):
    '''(str) -> list
    Takes a png pattern and returns list of all
    PNG files matching it. You don't have to
    add .png or numbering at the endo of pattern.

    Possible improvement:
    It's somehow redundant to list of xvg in
    create_image_from_xvg
    '''
    pattern = re.sub(r'_?[0-9]*(\.png)?$','',pattern)
    print('I\'m using pattern for PNG files: ', pattern)
    allfiles = os.listdir()
    png_files = list(filter(lambda fn: fn.startswith(pattern) and fn.endswith('.png'),
                            allfiles))
    # sort by the numbers in the names, so _B500 comes before _B1000
    png_files.sort(key = lambda fn: [int(part) if part.isdigit() else part
                                     for part in re.split(r'(\d+)', fn)])
    return png_files
    

    
def create_video(png_pattern, vid_name = '', fps = 1):
    '''(str, str, float) -> str
    Creates a video from png files matching the pattern, one frame
    per file. If vid_name is empty, <pattern>_film.avi is used.
    Returns the video name.
    '''

    images = list_of_png(png_pattern)
    if not images:
        raise FileNotFoundError('No PNG files match the pattern: ' + png_pattern)
    print(images)
    if not vid_name:
        vid_name = re.sub(r'\.png$', '', png_pattern) + '_film'
    if not vid_name.lower().endswith('.avi'):
        vid_name += '.avi'

    frame = cv2.imread(images[0])
    height, width, layers = frame.shape

    video = cv2.VideoWriter(vid_name, cv2.VideoWriter_fourcc(*'MJPG'),
                            fps, (width, height))
    if not video.isOpened():
        raise RuntimeError('Could not create the video file: ' + vid_name)

    for img in images:
        frame = cv2.imread(img)
        if frame is None:
            raise ValueError('Could not read image: ' + img)
        # all frames must have the size of the first one
        if frame.shape[:2] != (height, width):
            frame = cv2.resize(frame, (width, height))
        video.write(frame)

    video.release()
    return vid_name

def run_function():
    """ Take input from a user and run the module """

    print("Give me a pattern for PNG images. Beginning of the name is sufficient, png extension isn't required:")
    png_name = input().strip()

    print("Give me the name of a video you want to be created .AVI will be added at the end (Enter = automatic name):")
    vid_name = input().strip()

    vid_name = create_video(png_name, vid_name)
    print('Video saved as: ' + vid_name)



if __name__ == '__main__':
    run_function()


#thank you stackoverflow :)
"""
image_folder = 'images'
video_name = 'video.avi'

images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter(video_name, 0, 1, (width,height))

for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

cv2.destroyAllWindows()
video.release()
"""