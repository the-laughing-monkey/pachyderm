
<?xml version="1.0" encoding="UTF-8"?>

### Pachyderm Video Processing Demo

Welcome to the video processing demo of Pachyderm! We’re going to use the power of Pachyderm’s data version control and data transformation to do some video capture. To do that, we'll work with Python 3 and OpenCV to capture the video frame by frame, dumping those frames to JPGs.  

If you’re just getting started with Pachyderm, make sure you’ve gone through the [local installation](https://docs.pachyderm.io/en/latest/getting_started/local_installation.html) to get started and at least the [beginner demo](https://docs.pachyderm.io/en/latest/getting_started/beginner_tutorial.html) before moving on to this one.  

Ready? Let’s go!

### Create a Repo

First we create a repo, which is the highest level data primitive in Pachyderm. Like many things in Pachyderm, it borrows from well known Git concepts and a repo behaves the same way here as it does in Git.

For this demo, we’ll create a repo called **videos** to hold the data we want to process:

$ **pachctl create repo videos**

$ **pachctl list repo**

NAME CREATED SIZE (MASTER)
videos 7 seconds ago 0B

This shows that we successfully created the videos repo and that the size of repo’s master branch is 0B, since we haven’t added any data to it yet.

### Adding Data to Pachyderm

Now that we’ve created a repo it’s time to add some data.

In Pachyderm, you write data to an explicit commit (again, similar to Git). Commits are immutable snapshots of your data which give Pachyderm its version control properties. Files can be added, removed, or updated in a given commit.  

We’ll start by adding just one video file to the repo with a new commit. We’ve provided some small online videos used for testing programs from a few sources in the videos.txt file. NOTE: If you want to use your own videos, make sure they are small or you could be watching frames dumping for hours or days! In other words, don’t download the latest episode of Game of Thrones for this demo or it might take as long to finish as GRR Martin is taking to finish writing the books.

We’ll use the put file command along with the **-f** flag. The flag can take either a local file, a URL, or a object storage bucket which it’ll automatically scrape. In our case, we’ll pass a URL.

Unlike Git, commits in Pachyderm must be explicitly started and finished as they can contain huge amounts of data and we don’t want that much “dirty” data hanging around in an unpersisted state. The “put file” command automatically starts and finishes a commit for you so you can add files more easily. If you want to add many files over a period of time, you can do start commit and finish commit yourself.

We also specify the repo name “**videos**”, the branch name “**master**”, and the file name: “**small.mp4**”.

Here’s an example atomic commit of the file small.mp4 to the images repo’s master branch:

$ **pachctl put file videos@master:small.mp4 -f [http://techslides.com/demos/sample-videos/small.mp4](http://techslides.com/demos/sample-videos/small.mp4)**
 
Let’s check to make sure the data got added into Pachyderm’s videos repo.  

$ **pachctl list repo**

NAME CREATED SIZE (MASTER)
videos About a minute ago 57.27KiB
 
The **list** command shows us the repo and that there’s data inside of it.

We can also view the commit we just created:

$ **pachctl list commit videos**

REPO COMMIT PARENT STARTED DURATION SIZE
videos d89758a7496a4c56920b0eaa7d7d3255 <none> 29 seconds ago Less than a second 57.27KiB

And we can see the actual file in there, the commit ID and the size of the file:
 
$ **pachctl list file videos@master**

COMMIT NAME TYPE COMMITTED SIZE
d89758a7496a4c56920b0eaa7d7d3255 /small.mp4 file About a minute ago 57.27KiB

Finally, we can also view the file we just added. Since this is an video, we can’t just print it out but we can call a program on our mac to view the file easily  

On macOS # If you have VLC installed:
**$ pachctl get file videos@master:small.mp4 | open -f -a /Applications/VLC.app**

  
### Create a Pipeline

Now that we’ve got some data in our repo, it’s time to do something with it. Pipelines the way we work with data inside of Pachyderm. In other words, it’s how we do something. We create a pipeline’s key pieces with a JSON encoding. For this example, we’ve already created the pipeline for you and you can find the [code on Github](https://github.com/the-laughing-monkey/pachyderm).

When you want to create your own pipelines later, you can refer to the full [Pipeline Specification](https://docs.pachyderm.io/en/latest/reference/pipeline_spec.html) to use more advanced options. Options include building your own code into a container instead of the pre-built Docker image we’ll be using here.

For now, we’re going to create a single pipeline that takes a video, captures it frame by frame and dumps those frames to jpgs.

Below is the pipeline spec and python code we’re using. Let’s walk through the details.

```
{  
  "pipeline": {  
    "name": "videoprocessing"  
  },  
  "input": {  
    "pfs": {  
      "repo": "videos",  
      "glob": "/*"  
  }  
  },  
  "transform": {  
    "cmd": [ "python3", "/video-processing-pach.py" ],  
    "image": "rabbit37/videoprocessing:v23"  
  }  
}
```  


 
Our pipeline spec contains a few simple sections. First is the pipeline name: **videoprocessing**.

Next we specify the input. Here we only have one PFS input, our videos repo with a particular glob pattern that grabs everything in the repo with an *.

Finally we have the transform which specifies the docker image we want to use, rabbit37/videoprocessing:23 (which defaults to using DockerHub as the registry), and we have a small python script that will do the frame capture for us called **video-processing-pach.py**{LINK TO GITHUB}.

The code for the video-processing-pach.py is below:

```# Import libraries  
import cv2 # opencv  
import os #os specific stuff  
  
## Vars  
  
f_path = "/pfs/videos"  
f_out = "/pfs/out"  
  
  
## Functions  
  
# Process video  
def process_video(video):  
    cap = cv2.VideoCapture(video)  
    currentframe = 0  
  
  # Get video name without extension for naming video  
  vid_name = (os.path.splitext(os.path.basename(video))[0])  
  
  while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()  
  
    # process the video into frames
    if ret:
      # Saves image of the current frame in jpg file
      name = str(vid_name) + "_" + str(currentframe) + '.jpg'
      cv2.imwrite(os.path.join(f_out, name), frame)
      
      # Iterate through the frames one by one
      currentframe += 1
 
    else:
      cap.release()
      break  
  
## Body  
  
# Read all the videos from the specified path and process them  
for dirpath, dirs, files in os.walk(f_path):  
    for file in files:  
        process_video(os.path.join(dirpath, file))  
```
  
We walk through all the videos stored in the repo, which we connect to through the special local directory of **/pfs/videos**, do our frame capture, and write out the frames as jpgs to the special output directory **/pfs/out**.

/pfs/videos and /pfs/out are special local directories that Pachyderm creates in the container automatically. All the input data for a pipeline will be found in /pfs/<input_repo_name> and your code should always write out to /pfs/out. Pachyderm will automatically gather everything you write to /pfs/out and version it as this pipeline’s output.

Now let’s create the pipeline in Pachyderm:

$ **pachctl create pipeline -f** [**https://raw.githubusercontent.com/the-laughing-monkey/pachyderm/master/video-processing.json**](https://raw.githubusercontent.com/the-laughing-monkey/pachyderm/master/video-processing.json)

### What Happens When You Create a Pipeline

Creating a pipeline tells Pachyderm to run your code on the data in your input repo (the HEAD commit) as well as all future commits that occur after the pipeline is created. Our repo already had a commit, so Pachyderm automatically launched a job to process that data.

The first time Pachyderm runs a pipeline job, it needs to download the Docker image (specified in the pipeline spec) from the specified Docker registry (DockerHub in this case). This first run this might take a minute or more because of the image download, depending on your Internet connection. Subsequent runs will be much faster, since Docker will store the container image in your local registry.

You can view the job with:

$ **pachctl list job**

ID PIPELINE STARTED DURATION RESTART PROGRESS DL UL STATE

3de25f1b34e841e786b17f872fd29b52 videoprocessing About an hour ago 4 seconds 0 2 + 0 / 2 1.372MiB 13.89MiB success

You can also see the pipeline working and whether it succeed:

$ **pachctl list pipeline**

NAME INPUT CREATED STATE / LAST JOB
videoprocessing videos:/* About an hour ago running / success

 
It looks like our job was a success. But to make sure you want to make sure the the frames were written to the videoprocessing directory:

$ **pachctl list file videoprocessing@master**
COMMIT NAME TYPE COMMITTED SIZE
799a80fbdb7e4a1db237a6553cbd444c /small_0.jpg file About an hour ago 27.93KiB
799a80fbdb7e4a1db237a6553cbd444c /small_1.jpg file About an hour ago 28.27KiB
799a80fbdb7e4a1db237a6553cbd444c /small_10.jpg file About an hour ago 26.23KiB
799a80fbdb7e4a1db237a6553cbd444c /small_100.jpg file About an hour ago 29.68KiB

You’ll see a lot more files in your output, depending on how long the video was and how many frames were in the video.  

### Conclusion

Congratulations! 
You successfully created a repo in Pachyderm, put videos in that repo and used Python and OpenCV to do frame capture on the videos. 

Now you are ready to move on to more advanced tutorials!
