
# MatchingGRPC

Feature detection and matching as a GRPC "box".
## Methods

| Method   | Input       | Output                           |
| :---------- | :--------- | :---------------------------------- |
| `Sift_Seq` | `Empty` | `Data (bytes)` |
| `Sift_All` | `Empty` | `Data (bytes)` |
| `Orb_Seq` | `Empty` | `Data (bytes)` |
| `Orb_All` | `Empty` | `Data (bytes)` |
| `Manual` | `Empty` | `Data (bytes)` |

#### Sift_Seq

Runs feature detection with the SIFT descriptor and uses KNN for matching.

Only matches sequentially, meaning it only matches a image with the next one (in alphabetic order). 

#### Sift_All

Runs feature detection with the SIFT descriptor and uses KNN for matching.

Matches between all images (in alphabetic order). To avoid repetition, the first index must be greater than the second one.

#### Orb_Seq

Runs feature detection with the ORB descriptor and uses KNN for matching.

Only matches sequentially, meaning it only matches an image with the next one (in alphabetic order). 

#### Orb_All

Runs feature detection with the ORB descriptor and uses KNN for matching.

Matches between all images (in alphabetic order). To avoid repetition, the first index must be greater than the second one.


#### Manual

Doesn't run any feature detection or matching. Returns whatever the first .mat file found in the "inputImages" file has. 

### Output Data

All outputs are an array of bytes that represent a compressed .mat file containing the corresponding keypoints between images and their descriptors.

Since .mat file does not accept tensors, the Keys for the image pairs are a string with the following structure: "[name of image 1]-[name of image 2]". 

There are some wrappers due to the .mat file way to handle numpy arrays.

The pairs of keypoint coordinates are stored in a numpy array with 4 columns (x1, y1, x2, y2).

For example, to access the matching points between image 1 and 4: 

```
matched_points = Dict['img_00000-img_00003'][0][0]
```

## Deploy

To build the docker image use:

```
docker build -t matching_grpc --build-arg SERVICE_NAME=generic_box -f docker/Dockerfile .
```

After this, just run the pipeline (Instructions are on the pipeline's repository).

In case you want to test this pipeline element, follow the next instructions.

To execute the docker container, make sure you have a file called "inputImages" so the volume can attactched to a folder and then exectue the following command: 
```
docker run -p 8061:8061 -it --volume "%cd%/inputImages/":/app/inputImages/ --rm matching_grpc
```

To test this pipeline element, it needs the grpc message types. All the grpc functions are stored in the "generic_box_pb2.py" and "generic_box_pb2_grpc.py". To get these files we run:

```
  python -m grpc_tools.protoc --proto_path=./protos --python_out=. --grpc_python_out=. generic_box.proto
```

You can now add .jpg images to the "inputImages" directory and run the "test_generic_box.ipynb". The output file will be stored as FeatureData.mat in you're working directory.
