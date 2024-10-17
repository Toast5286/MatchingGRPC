import concurrent.futures as futures
import grpc
import grpc_reflection.v1alpha.reflection as grpc_reflection
import logging
import generic_box_pb2
import generic_box_pb2_grpc
import utils

import matchingService as ms

InputDirectory = "/app/inputImages/"

class ServiceImpl(generic_box_pb2_grpc.GenericBoxServiceServicer):

    def __init__(self):
        """
        Args:
            calling_function: the function that should be called
                              when a new request is received

                              the signature of the function should be:

                              (image: bytes) -> bytes

                              as described in the process method

        """
        self.Matcher = ms.matching(InputDirectory,".jpg")


    def Sift_Seq(self, request: generic_box_pb2.Data, context):
        #Run SIFT Sequential Match
        self.Matcher.SIFT_Seq_Match()
        #Get results in a dictionary
        ResultDict = self.Matcher.Results
        #Save results in a .mat file and get the binary of the file
        BinaryMat = ms.saveBinaryMat(ResultDict)
        #Send GRPC message
        return generic_box_pb2.Data(file = BinaryMat)
    
    def Sift_All(self, request: generic_box_pb2.Data, context):
        #Run SIFT Sequential Match
        self.Matcher.SIFT_All_Match()
        #Get results in a dictionary
        ResultDict = self.Matcher.Results
        #Save results in a .mat file and get the binary of the file
        BinaryMat = ms.saveBinaryMat(ResultDict)
        #Send GRPC message
        return generic_box_pb2.Data(file = BinaryMat)

    def Orb_Seq(self, request: generic_box_pb2.Data, context):
        #Run SIFT Sequential Match
        self.Matcher.Orb_Seq_Match()
        #Get results in a dictionary
        ResultDict = self.Matcher.Results
        #Save results in a .mat file and get the binary of the file
        BinaryMat = ms.saveBinaryMat(ResultDict)
        #Send GRPC message
        return generic_box_pb2.Data(file = BinaryMat)

    def Orb_All(self, request: generic_box_pb2.Data, context):
        #Run SIFT Sequential Match
        self.Matcher.Orb_All_Match()
        #Get results in a dictionary
        ResultDict = self.Matcher.Results
        #Save results in a .mat file and get the binary of the file
        BinaryMat = ms.saveBinaryMat(ResultDict)
        #Send GRPC message
        return generic_box_pb2.Data(file = BinaryMat)
    
    def Manual(self, request: generic_box_pb2.Data, context):
        #Load the first .mat file found in the Input directory
        ResultDict = ms.OpenMatFile(InputDirectory)
        #Save results in a .mat file and get the binary of the file
        BinaryMat = ms.saveBinaryMat(ResultDict)

        #Send GRPC message
        return generic_box_pb2.Data(file = BinaryMat)

    
    

def grpc_server():
    logging.basicConfig(
        format='[ %(levelname)s ] %(asctime)s (%(module)s) %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    server = grpc.server(futures.ThreadPoolExecutor())
    generic_box_pb2_grpc.add_GenericBoxServiceServicer_to_server(
        ServiceImpl(),
        server)

    # Add reflection
    service_names = (
        generic_box_pb2.DESCRIPTOR.services_by_name['GenericBoxService'].full_name,
        grpc_reflection.SERVICE_NAME
    )
    grpc_reflection.enable_server_reflection(service_names, server)

    utils.run_server(server)
        

if __name__ == '__main__':
    grpc_server()
