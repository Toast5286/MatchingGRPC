
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

Since .mat file does not accept tensors, the Keys for the image pairs are a string with the following structure: "index1-index2". 

The pairs of keypoint coordinates are stored with the dictionary key "matching_coord" and their descriptors in "Descriptor1" and "Descriptor2".

There are some wrappers due to the .mat file way to handle numpy arrays.

The pairs of keypoint coordinates are stored in a numpy array with 4 columns (x1, y1, x2, y2).

For example, to access the matching points between image 1 and 4: 

```
matched_points = Dict['0-3']['matching_coord'][0][0]
```

## Deploy

To create the necessary generic_box_pb2.py and generic_box_pb2_grpc.py files use the following command:

```
  python -m grpc_tools.protoc --proto_path=./protos --python_out=. --grpc_python_out=. generic_box.proto
```

To build the docker image use:

```
docker build -t matching_grpc --build-arg SERVICE_NAME=generic_box -f docker/Dockerfile .
```

To execute the docker container, make sure you have a file called "inputImages" so the volume can attactched to a folder and then exectue the following command: 
```
docker run -p 8061:8061 -it --volume "%cd%/inputImages/":/app/inputImages/ --rm matching_grpc
```

You can now add files to the "inputImages" directory and run the "test_generic_box.ipynb". 
