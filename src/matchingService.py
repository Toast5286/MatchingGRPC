import io
from scipy.io import savemat, loadmat
import cv2  #install opencv-python and opencv-contrib-python
import numpy as np
import os
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any
import logging

class matching:
    def __init__(self,ImageDirectory,ImageFormat) -> None:
        self.ImgDir = ImageDirectory
        self.ImageFormat = ImageFormat

        self.DescriptorType = ''

        self.ImageNames = {}
        count = 0
        for filename in os.listdir(self.ImgDir):
            #Check if file is of the correct format
            if not filename.endswith(self.ImageFormat): 
                continue
            self.ImageNames[count] = filename
            count+=1

        self.NImages = count

        #Keypoints
        self.kp: List[List[cv2.KeyPoint]] = [[] for _ in range(self.NImages)]
        #Descriptors
        self.des: List[Any] = [None for _ in range(self.NImages)]
        self.matches: Dict[Tuple[int, int], List[cv2.DMatch]] = {}
        self.mask: Dict[Tuple[int, int], List[bool]] = {}

        self.Results = {}

    def __ReinitializeVar__(self):

        self.ImageNames = {}
        count = 0
        for filename in os.listdir(self.ImgDir):
            #Check if file is of the correct format
            if not filename.endswith(self.ImageFormat): 
                continue
            self.ImageNames[count] = filename
            count+=1

        self.NImages = count

        #Keypoints
        self.kp: List[List[cv2.KeyPoint]] = [[] for _ in range(self.NImages)]
        #Descriptors
        self.des: List[Any] = [None for _ in range(self.NImages)]
        self.matches: Dict[Tuple[int, int], List[cv2.DMatch]] = {}
        self.mask: Dict[Tuple[int, int], List[bool]] = {}

    def __CheckForUpdates__(self,NewDescriptorType):

        if NewDescriptorType != self.DescriptorType:
            self.DescriptorType = NewDescriptorType
            return True

        count = 0
        for filename in os.listdir(self.ImgDir):
            #Check if file is of the correct format
            if not filename.endswith(self.ImageFormat): 
                continue

            if not filename in self.ImageNames.values():
                return True   
              
            count +=1   
            
        if count != self.NImages:
            return True

        return False


    def __Detect__(self,FeatureDetector,img1,img2):
        kp1, des1 = FeatureDetector.detectAndCompute(img1,None)
        kp2, des2 = FeatureDetector.detectAndCompute(img2,None)

        return kp1, des1, kp2, des2
    
    def __BruteForceMatching__(self,des1,des2,descriptor_type):
        if descriptor_type == 'SIFT':
            # For SIFT (or other float descriptors like SURF), use L2 norm
            matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        elif descriptor_type == 'ORB':
            # For ORB (or other binary descriptors), use Hamming norm
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        else:
            raise ValueError("Unsupported descriptor type. Use 'SIFT' or 'ORB'.")
        
        matches = matcher.knnMatch(des1, des2, k=2)
        
        good_matches = []
        if descriptor_type == 'SIFT':
            for m, n in matches:
                if m.distance < 0.75 * n.distance:  # Ratio test
                    good_matches.append(m)
        else:
            # For ORB or binary descriptors, just take the best match
            for m in matches:
                if len(m) > 0:  # Ratio test
                    good_matches.append(m[0])

        return good_matches

    def __SiftDetecMatch__(self,img1,img2):
        #Create Descriptor function object
        DescFunc = cv2.SIFT_create()
        #Feature Detection
        kp1, des1, kp2, des2 = self.__Detect__(DescFunc,img1,img2)
        #Feature Matching
        matches = self.__BruteForceMatching__(des1,des2,'SIFT')
        return matches, kp1, des1, kp2, des2
        
    def __OrbDetecMatch__(self,img1,img2):
        #Create Descriptor function object
        DescFunc = cv2.ORB_create()
        #Feature Detection
        kp1, des1, kp2, des2 = self.__Detect__(DescFunc,img1,img2)
        #Feature Matching
        matches = self.__BruteForceMatching__(des1,des2,'ORB')
        return matches, kp1, des1, kp2, des2
    
    def __GetMatchingKPAndDesc__(self, index,mask = {}):
        desc1 = []
        desc2 = []
        pt1 = []
        pt2 = []
        for i, match in enumerate(self.matches[index]):
            if not mask or mask[index][i]:

                # Get the matching keypoints coordinates
                pt1.append(self.kp[index[0]][match.queryIdx].pt)  # Point from the first image
                pt2.append(self.kp[index[1]][match.trainIdx].pt)  # Point from the second image
                
                # Get the corresponding descriptors
                desc1.append(self.des[index[0]][match.queryIdx])
                desc2.append(self.des[index[1]][match.trainIdx])

        pt1 = np.array(pt1)
        pt2 = np.array(pt2)
        desc1 = np.array(desc1)
        desc2 = np.array(desc2)

        return pt1, desc1, pt2, desc2


    def __RANSACFundamental__(self,index):
        
        if len(self.matches[index]) < 8:
            raise ValueError("Not enough good matches to compute the fundamental matrix.")
        
        pt1, _, pt2, _ = self.__GetMatchingKPAndDesc__(index)

        # Compute the fundamental matrix and get the mask of inliers
        F, mask = cv2.findFundamentalMat(pt1, pt2, cv2.FM_RANSAC, 1.0, 0.99)
        
        if F is None:
            raise ValueError("Fundamental matrix computation failed.")

        if mask[mask].size < 8:
            raise ValueError("Not enough inlier matches to compute the fundamental matrix.")
        
        return mask

    def __seqMatch__(self,DetectMatchMethod):

        for index, filename in self.ImageNames.items():

            #Get Image in gray scale
            image = cv2.imread(self.ImgDir+filename) 
            img2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

            if index == 0:
                img1 = img2
                continue

            self.matches[(index-1,index)], self.kp[index-1],self.des[index-1], self.kp[index], self.des[index] = DetectMatchMethod(img1,img2)
            #self.mask[(index-1,index)] = self.__RANSACFundamental__((index-1,index))
            img1 = img2

    def __allMatch__(self,DetectMatchMethod):

        for index1, filename1 in self.ImageNames.items():

            #Get Image in gray scale
            image1 = cv2.imread(self.ImgDir+filename1) 
            img1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY) 

            for index2, filename2 in self.ImageNames.items():
                if index2<=index1:
                    continue

                #Get Image in gray scale
                image2 = cv2.imread(self.ImgDir+filename2) 
                img2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY) 

                self.matches[(index1,index2)], self.kp[index1],self.des[index1], self.kp[index2], self.des[index2] = DetectMatchMethod(img1,img2)
                #self.mask[(index1,index2)] = self.__RANSACFundamental__((index1,index2))
                
    def SIFT_Seq_Match(self):
        if self.__CheckForUpdates__("SIFT_Seq"):
            self.__ReinitializeVar__()
            self.__seqMatch__(self.__SiftDetecMatch__)
            self.Results = self.SaveToDictionary()

    def SIFT_All_Match(self):
        if self.__CheckForUpdates__("SIFT_All"):
            self.__ReinitializeVar__()
            self.__allMatch__(self.__SiftDetecMatch__)
            self.Results = self.SaveToDictionary()
    
    def Orb_Seq_Match(self):
        if self.__CheckForUpdates__("Orb_Seq"):
            self.__ReinitializeVar__()
            self.__seqMatch__(self.__OrbDetecMatch__)
            self.Results = self.SaveToDictionary()
    
    def Orb_All_Match(self):
        if self.__CheckForUpdates__("Orb_All"):
            self.__ReinitializeVar__()
            self.__allMatch__(self.__OrbDetecMatch__)
            self.Results = self.SaveToDictionary()

    def SaveToDictionary(self):
        Dict = {}

        for index in self.matches:
            pt1, desc1, pt2, desc2 = self.__GetMatchingKPAndDesc__(index,self.mask) 
            #, 'Descriptor1':desc1, 'Descriptor2':desc2 
            filename1, _ = os.path.splitext(self.ImageNames[index[0]])
            filename2, _ = os.path.splitext(self.ImageNames[index[1]])
            Dict[str(filename1)+"_"+str(filename2)] = np.hstack((pt1,pt2))
        print(Dict)
        return Dict
    
def saveBinaryMat(dict):
    #save mat file and open it as binary
    savemat("/tmp/data.mat",dict,long_field_names=True, do_compression=True)
    with open("/tmp/data.mat", 'rb') as fp:
        bytesData = fp.read()
    os.remove("/tmp/data.mat")

    return bytesData

def OpenMatFile(Directory):
    for filename in os.listdir(Directory):
        #Check if file is of the correct format
        if not filename.endswith(".mat"): 
            continue
        else:
            Dict = loadmat(Directory+filename)
            return Dict
    raise ValueError("No .mat file found in the Directory")


#Main for test purposes      
if __name__ == '__main__':
    test = matching("./src/TestImages/",".jpg")
    test.SIFT_Seq_Match()
    print(test.SaveToDictionary())

    image = cv2.imread(test.ImgDir+test.ImageNames[0]) 
    img1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

    image = cv2.imread(test.ImgDir+test.ImageNames[1]) 
    img2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

    print(np.transpose(test.mask[(0,1)])[0])
    img3 = cv2.drawMatches(img1, test.kp[0], img2, test.kp[1], test.matches[(0,1)], 
                       outImg=None, matchesMask = np.transpose(test.mask[(0,1)])[0],
                       flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    plt.imshow(img3),plt.show()
    