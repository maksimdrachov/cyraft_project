#!/usr/bin/env python3
import asyncio
import pycyphal
import cyraft, cyraft.cluster
from pycyphal.application import make_node, NodeInfo, register

UPDATE_PERIOD = 1.0


async def main() -> None:
    node = make_node(NodeInfo(name="org.opencyphal.cyraft"))

    def on_request(msg: cyraft.NameToIDRequest_0, _metadata: pycyphal.transport.TransferFrom):
        print(f"Received request {msg} via {_metadata}")

    async def on_request_vote(request: cyraft.cluster.RequestVote_1.Request,
                              _metadata) -> cyraft.cluster.RequestVote_1.Response:
        print(f"Request vote: {request}")
        return cyraft.cluster.RequestVote_1.Response()

    # Set up the ports.
    pub_response = node.make_publisher(cyraft.NameToIDResponse_0, 3000)
    pub_response.priority = pycyphal.transport.Priority.SLOW

    pub_discovery = node.make_publisher(cyraft.cluster.Discovery_1, 3002)
    pub_discovery.priority = pycyphal.transport.Priority.SLOW

    sub_request = node.make_subscriber(cyraft.NameToIDRequest_0, 3001)
    sub_request.receive_in_background(on_request)

    srv_request_vote = node.get_server(cyraft.cluster.RequestVote_1, 100)
    srv_request_vote.serve_in_background(on_request_vote)

    # TODO: subscribe to discovery messages

    # Run the main loop forever.
    node.start()
    next_update_at = asyncio.get_running_loop().time()
    while True:
        # Publish discovery message.
        await pub_discovery.publish(
            cyraft.cluster.Discovery_1()  # TODO fill the msg
        )
        # Sleep until the next iteration.
        next_update_at += UPDATE_PERIOD
        await asyncio.sleep(next_update_at - asyncio.get_running_loop().time())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
