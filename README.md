
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

Only matches sequentially, meaning it only matches a image with the next one (in alphabetic order). 

#### Orb_All

Runs feature detection with the ORB descriptor and uses KNN for matching.

Matches between all images (in alphabetic order). To avoid repetition, the first index must be greater then the second one.

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
