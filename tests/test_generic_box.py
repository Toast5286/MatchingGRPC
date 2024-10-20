# Test for the estimation of a single image key-points

import argparse
import grpc
import io
import matplotlib.pyplot as plt
import generic_box_pb2
import generic_box_pb2_grpc
from sicpy.io import savemat, loadmat
import PIL.Image as PIL_image
import cv2 as cv


def process_image(stub, image_path):
    print(f'Processing image: \'{image_path}\'')
    img=cv.imread(image_path)
    savemat("img.mat",{"im":img})
    with open("img.mat", 'rb') as fp:
        image_bytes = fp.read()
    request = generic_box_pb2.Data(file=image_bytes)
    return stub.process(request)


def display_image(image):
    dados=loadmat(image)
#    img = PIL_image.open(io.BytesIO(image.data))
    img=dados['newim']
    ax = plt.gca()
    ax.imshow(img)
    plt.show()


def parse_args():
    """
    Parse arguments for test setup

    Returns:
        The arguments for the test
    """
    parser = argparse.ArgumentParser(description='Test for OpenPose gRPC Service')
    parser.add_argument(
        'image',
        help='Path to the image to send to the server')
    parser.add_argument(
        '--target',
        metavar='target',
        default='localhost:8061',
        help='Location of the tested server (defaults to localhost:8061)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    target = args.target
    image_path = args.image
    with grpc.insecure_channel(target) as channel:
        estimator_stub = image_generic_pb2_grpc.GenericBoxServiceStub(channel)
        try:
            response = process_image(estimator_stub, image_path)
            display_image(response)
        except grpc.RpcError as rpc_error:
            print('An error has occurred:')
            print(f'  Error Code: {rpc_error.code()}')
            print(f'  Details: {rpc_error.details()}')
