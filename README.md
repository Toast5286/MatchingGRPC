
# MatchingGRPC

A feature detection and matching as a GRPC "box".
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
